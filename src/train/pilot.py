"""Pilot v1 runner: train one arm/seed with the FROZEN configs/pilot_v1_1.json, then evaluate (D-023).

  python -m src.train.pilot train --rep BN-G --seed 666 [--subset train_1h]
  python -m src.train.pilot eval  --rep BN-G --seed 666 [--subset train_1h]

train: official F5 Trainer via src.train.f5_train helpers. The F5 Trainer calls ema_model.update()
       exactly once per optimizer update (after the step); that call is wrapped to count updates, snapshot
       the EMA weights (fp16 safetensors, loadable by f5 load_checkpoint) at the pre-registered eval
       updates, and stop after exactly `updates` updates. The 5 GB optimizer checkpoint is never written.
       F5's scheduler decays over whole epochs, so epochs = ceil(updates / updates_per_epoch) and the
       schedule end slightly exceeds `updates` (lr_at_stop is logged).
eval:  separate process (no GPU sharing with training). For every eval checkpoint (update 0 = the
       arm's expanded pretrained weights) synthesize the fixed eval set; at the final update also
       test_seen and test_unseen (reference utterances are never scored). Score with the primary and
       secondary ASR (src.eval.asr) against the Bengali-script transcripts.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import time
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[2]
CONFIG = json.loads((ROOT / "configs/pilot_v1_1.json").read_text(encoding="utf-8"))
SMOKE = os.environ.get("PILOT_SMOKE") == "1"  # pipeline check only: tiny budget, separate run dir, never reported
if SMOKE:
    CONFIG = {**CONFIG, "version": CONFIG["version"] + "_smoke",
              "train": {**CONFIG["train"], "updates": 20, "warmup_updates": 2},
              "eval": {**CONFIG["eval"], "eval_updates": [0, 10, 20]}}
SMOKE_MAX_ITEMS = 5
MANIFEST = ROOT / "data/derived/slr37_bn_bd/manifest.tsv"
SPLITS = ROOT / "data/derived/splits/v1"
FRAMES_PER_S = 24000 / 256


def _disable_power_throttling() -> None:
    """Opt this process out of Windows 11 EcoQoS (D-026). Background/scheduled-task processes otherwise run on
    efficiency cores at low clocks, halving F5 throughput. Wall-clock only; no effect on computation.
    Runs at import, so spawned DataLoader workers (which re-import the main module) opt out as well."""
    if os.name != "nt":
        return
    import ctypes
    import ctypes.wintypes as wt

    class _State(ctypes.Structure):
        _fields_ = [("Version", wt.ULONG), ("ControlMask", wt.ULONG), ("StateMask", wt.ULONG)]

    st = _State(1, 0x1, 0)  # PROCESS_POWER_THROTTLING_EXECUTION_SPEED off
    k32 = ctypes.WinDLL("kernel32")
    k32.SetProcessInformation(k32.GetCurrentProcess(), 4, ctypes.byref(st), ctypes.sizeof(st))


_disable_power_throttling()


class StopTraining(Exception):
    pass


def run_dir(rep: str, seed: int, subset: str) -> Path:
    return ROOT / "runs" / CONFIG["version"] / f"{rep}__{subset}__s{seed}"


def micro_batches_per_epoch(durations: list[float], batch_frames: int, max_samples: int, seed: int) -> int:
    from f5_tts.model.dataset import DynamicBatchSampler
    from torch.utils.data import SequentialSampler

    class _Frames:
        def __len__(self):
            return len(durations)

        def get_frame_len(self, i):
            return durations[i] * FRAMES_PER_S

    return len(DynamicBatchSampler(SequentialSampler(_Frames()), batch_frames, max_samples=max_samples,
                                   random_seed=seed, drop_residual=False))


def save_online_fp16(trainer, path: Path) -> None:
    """Online (trained, non-EMA) weights, keys as in CFM.state_dict(); load with use_ema=False (D-024)."""
    from safetensors.torch import save_file
    model = trainer.accelerator.unwrap_model(trainer.model)
    sd = {k: (v.detach().to(torch.float16) if v.is_floating_point() else v.detach()).contiguous().cpu()
          for k, v in model.state_dict().items()}
    save_file(sd, str(path))


def train(rep: str, seed: int, subset: str) -> None:
    from f5_tts.model import CFM, DiT, Trainer
    from f5_tts.model.dataset import CustomDataset

    from src.train.f5_train import ARCH, MEL, build_dataset, expanded_checkpoint, load_vocab
    tc = CONFIG["train"]
    out = run_dir(rep, seed, subset)
    out.mkdir(parents=True, exist_ok=True)
    if (out / "train_done.json").exists():
        print(f"{out.name}: already trained")
        return
    torch.manual_seed(seed)
    vocab_map, vocab_path = load_vocab(rep)
    train_hf, durations = build_dataset(rep, subset, vocab_map)
    ckpt = expanded_checkpoint(len(vocab_map), out)
    micro = micro_batches_per_epoch(durations, tc["batch_frames"], tc["max_samples"], seed)
    upe = math.ceil(micro / tc["grad_accum"])
    epochs = math.ceil(tc["updates"] / upe)

    model = CFM(transformer=DiT(**ARCH, checkpoint_activations=tc["checkpoint_activations"],
                                text_num_embeds=len(vocab_map), mel_dim=MEL["n_mel_channels"]),
                mel_spec_kwargs=MEL, vocab_char_map=vocab_map)
    trainer = Trainer(model, epochs, tc["learning_rate"], num_warmup_updates=tc["warmup_updates"],
                      save_per_updates=10**9, keep_last_n_checkpoints=0, checkpoint_path=str(out),
                      batch_size_per_gpu=tc["batch_frames"], batch_size_type="frame", max_samples=tc["max_samples"],
                      grad_accumulation_steps=tc["grad_accum"], max_grad_norm=tc["max_grad_norm"], logger=None,
                      log_samples=False, last_per_updates=10**9, bnb_optimizer=False,
                      accelerate_kwargs={"mixed_precision": tc["mixed_precision"]})
    dataset = CustomDataset(train_hf, durations=durations, preprocessed_mel=False, **MEL)

    eval_updates = {u for u in CONFIG["eval"]["eval_updates"] if u > 0}
    log, t0, state = [], time.time(), {"updates": 0}
    orig_backward, orig_ema_update = trainer.accelerator.backward, trainer.ema_model.update

    def backward(loss, **kw):
        log.append((time.time() - t0, float(loss.detach())))
        return orig_backward(loss, **kw)

    def ema_update(*a, **kw):
        res = orig_ema_update(*a, **kw)  # called once per optimizer update, after the step
        state["updates"] += 1
        u = state["updates"]
        if u in eval_updates:
            save_online_fp16(trainer, out / f"online_u{u}.safetensors")
        if u >= tc["updates"]:
            raise StopTraining
        return res

    trainer.accelerator.backward = backward
    trainer.ema_model.update = ema_update
    config = {"rep": rep, "seed": seed, "subset": subset, "pilot_config": CONFIG["version"],
              "vocab_file": str(vocab_path), "vocab_size": len(vocab_map), "pretrained": str(ckpt),
              "micro_batches_per_epoch": micro, "updates_per_epoch": upe, "epochs": epochs,
              "schedule_total_updates": epochs * upe, "n_utts": len(durations),
              "audio_hours": sum(durations) / 3600}
    (out / "train_config.json").write_text(json.dumps(config, indent=2), encoding="utf-8")
    torch.cuda.reset_peak_memory_stats()
    try:
        trainer.train(dataset, num_workers=tc["num_workers"], resumable_with_seed=seed)
    except StopTraining:
        pass
    with open(out / "train_loss.tsv", "w", encoding="utf-8", newline="\n") as f:
        f.write("micro\tt\tloss\n" + "".join(f"{i}\t{t:.2f}\t{loss:.5f}\n" for i, (t, loss) in enumerate(log)))
    missing = sorted(u for u in eval_updates if not (out / f"online_u{u}.safetensors").exists())
    assert not missing, f"missing eval checkpoints {missing}"
    done = {"updates": state["updates"], "micro_batches": len(log), "wall_s": time.time() - t0,
            "lr_at_stop": trainer.scheduler.get_last_lr()[0],
            "peak_vram_reserved_gb": torch.cuda.max_memory_reserved() / 2**30,
            "weight_snapshots": sorted(p.name for p in out.glob("online_u*.safetensors"))}
    (out / "train_done.json").write_text(json.dumps(done, indent=2), encoding="utf-8")
    print(json.dumps(done, indent=2))


def split_items(name: str, exclude: set[str]) -> list[dict]:
    with open(MANIFEST, encoding="utf-8", newline="") as f:
        man = {r["utt_id"]: r for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE)}
    with open(SPLITS / f"{name}.tsv", encoding="utf-8") as f:
        ids = [r["utt_id"] for r in csv.DictReader(f, delimiter="\t")]
    return [{"utt_id": u, "speaker": man[u]["speaker"], "text": man[u]["text"]} for u in ids if u not in exclude]


def evaluate(rep: str, seed: int, subset: str) -> None:
    from src.eval.asr import ASR, bootstrap, corpus, load_audio_16k, utt_scores
    from src.infer.f5_infer import F5Synth, load_eval, synthesize_set
    out = run_dir(rep, seed, subset)
    done = json.loads((out / "train_done.json").read_text(encoding="utf-8"))
    ev = CONFIG["eval"]
    fixed, refs = load_eval("fixed_v1")
    ref_ids = {r["ref_utt_id"] for r in refs.values()}
    final_u = max(ev["eval_updates"])
    pretrained = next(out.glob("pretrained_*.safetensors"))
    jobs = [(u, "fixed_v1", fixed) for u in ev["eval_updates"]]
    jobs += [(final_u, s, split_items(s, ref_ids)) for s in ev["final_eval_sets"]]
    if SMOKE:
        jobs = [(u, s, items[:SMOKE_MAX_ITEMS]) for u, s, items in jobs]

    for u in ev["eval_updates"]:  # 1) synthesis, one model load per checkpoint
        todo = [(s, items) for uu, s, items in jobs
                if uu == u and not (out / "eval" / f"u{u}" / s / "summary.json").exists()]
        if not todo:
            continue
        synth = F5Synth(rep, str(pretrained if u == 0 else out / f"online_u{u}.safetensors"), use_ema=(u == 0))
        for s, items in todo:
            synthesize_set(synth, items, refs, out / "eval" / f"u{u}" / s)
        del synth
        torch.cuda.empty_cache()

    results = {}
    for asr_id in (ev["asr_primary"], ev["asr_secondary"]):  # 2) ASR scoring, one load per ASR model
        asr, tag = ASR(asr_id), asr_id.split("/")[-1]
        for u, s, items in jobs:
            d = out / "eval" / f"u{u}" / s
            texts = {it["utt_id"]: it["text"] for it in items}
            ids = sorted(texts)
            hyps = asr.transcribe([load_audio_16k(str(d / f"{i}.wav")) for i in ids])
            rows = [{"utt_id": i, **utt_scores(texts[i], h)} for i, h in zip(ids, hyps)]
            with open(d / f"asr_{tag}.tsv", "w", encoding="utf-8", newline="\n") as f:
                f.write("utt_id\tcer\tcer_nospace\twer\tref\thyp\n")
                for r in sorted(rows, key=lambda r: -r["cer"]):
                    f.write(f"{r['utt_id']}\t{r['cer']:.4f}\t{r['cer_nospace']:.4f}\t{r['wer']:.4f}\t"
                            f"{r['ref']}\t{r['hyp']}\n")
            results[f"{tag}|u{u}|{s}"] = {**corpus(rows), **bootstrap(rows), "n": len(rows)}
        del asr
        torch.cuda.empty_cache()
    summary = {"rep": rep, "seed": seed, "subset": subset, "train": done, "results": results}
    (out / "eval_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    for k, v in results.items():
        print(f"{k:62s} CER {v['CER']:6.2f} [{v['CER_ci95'][0]:.2f},{v['CER_ci95'][1]:.2f}]  "
              f"CERns {v['CER_nospace']:6.2f}  WER {v['WER']:6.2f}  n={v['n']}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["train", "eval"])
    ap.add_argument("--rep", required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--subset", default=CONFIG["train_subset_pilot"])
    a = ap.parse_args()
    assert a.rep in CONFIG["arms"] and a.seed in CONFIG["train"]["seeds"], "arm/seed not in frozen config"
    (train if a.cmd == "train" else evaluate)(a.rep, a.seed, a.subset)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
