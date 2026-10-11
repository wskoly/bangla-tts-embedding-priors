"""F5-TTS fine-tuning launcher using the official classes (CFM, DiT, CustomDataset, Trainer) (D-019).

Differences from f5_tts/train/finetune_cli.py, all deliberate and documented:
  * text is passed as plain strings -> one token per code point through list_str_to_idx
    (convert_char_to_pinyin is bypassed; D-016); every utterance is validated with zero unknown symbols;
  * the pretrained checkpoint is expanded to the arm's vocabulary exactly like the official
    `expand_model_embeddings` (new rows ~ N(0, 1), base rows untouched, fixed seed);
  * the dataset is built in memory from our frozen splits and the 24 kHz trimmed audio;
  * optional instrumentation (timestamps / loss per update, GPU + host sampling) for the probe;
    it wraps accelerator.backward without changing what it computes.

Usage (probe):
    python -m src.train.f5_train --rep BN-G --subset train_1h --run runs/probe/bn-g_b2000 \
        --batch-frames 2000 --grad-accum 1 --max-updates 300 --probe
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
import subprocess
import threading
import time
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[2]
from src.corpus.profile import ALLOW_G2P, AUDIO_INDEX, MANIFEST, SPLITS  # noqa: E402  (D-057 data profile)
BASE_CKPT = "hf://SWivid/F5-TTS/F5TTS_v1_Base/model_1250000.safetensors"
EMBED_KEY = "ema_model.transformer.text_embed.text_embed.weight"
ARCH = dict(dim=1024, depth=22, heads=16, ff_mult=2, text_dim=512, text_mask_padding=True, qk_norm=None,
            conv_layers=4, pe_attn_head=None, attn_backend="torch", attn_mask_enabled=False)
MEL = dict(target_sample_rate=24000, n_mel_channels=100, hop_length=256, win_length=1024, n_fft=1024,
           mel_spec_type="vocos")
EXPAND_SEED = 666  # same seed as the official expand_model_embeddings


class StopProbe(Exception):
    pass


def load_vocab(rep: str) -> tuple[dict[str, int], Path]:
    path = ROOT / f"configs/vocab/{rep}_v1.txt"
    vocab = path.read_text(encoding="utf-8").split("\n")[:-1]
    return {s: i for i, s in enumerate(vocab)}, path


def build_dataset(rep: str, subset: str, vocab_map: dict[str, int]):
    from datasets import Dataset as HFDataset

    from src.bnrep.reps import convert
    from src.train.vocab import encode
    with open(MANIFEST, encoding="utf-8", newline="") as f:
        raw = {r["utt_id"]: r["text"] for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE)}
    with open(AUDIO_INDEX, encoding="utf-8") as f:
        audio = {r["utt_id"]: r for r in csv.DictReader(f, delimiter="\t")}
    with open(SPLITS / f"{subset}.tsv", encoding="utf-8") as f:
        ids = [r["utt_id"] for r in csv.DictReader(f, delimiter="\t")]
    rows = []
    for u in ids:
        res = convert(rep, raw[u])
        assert ALLOW_G2P or not res.oov, (u, res.oov)  # C1 profile: out-of-lexicon words are G2P-filled (D-057)
        encode(res.text, vocab_map)  # raises on any unknown symbol
        rows.append({"audio_path": str(ROOT / audio[u]["path"]), "text": res.text,
                     "duration": float(audio[u]["duration_s"])})
    return HFDataset.from_list(rows), [r["duration"] for r in rows]


def expanded_checkpoint(vocab_size: int, run: Path, init: str = "official",
                        reinit_rows: list[int] | None = None) -> Path:
    """Base checkpoint with the text embedding resized to `vocab_size` (+1 filler row).

    init="official": new rows ~ N(0, 1) (as f5 expand_model_embeddings; trained rows have std ~0.62).
    init="matched":  new rows (and `reinit_rows`) ~ N(mu_d, sd_d), the per-dimension mean/std of the trained
                     rows 1..2545 (row 0 = filler excluded) (D-028).
    reinit_rows: embedding ROW indices (= vocab index + 1) to re-initialize (LAT-P-reinit control).
    """
    from cached_path import cached_path
    from safetensors.torch import load_file, save_file
    src = str(cached_path(BASE_CKPT))
    tag = "" if init == "official" and not reinit_rows else (
        f"_{init}" + (f"_reinit{len(reinit_rows)}" if reinit_rows else ""))
    dst = run / f"pretrained_model_1250000_vocab{vocab_size}{tag}.safetensors"
    if dst.exists():
        return dst
    sd = load_file(src, device="cpu")
    old = sd[EMBED_KEY]
    n_new = vocab_size + 1 - old.size(0)
    assert n_new >= 0, (vocab_size, old.shape)
    if n_new == 0 and not reinit_rows:
        shutil.copy2(src, dst)
        return dst
    g = torch.Generator().manual_seed(EXPAND_SEED)
    mu, sdv = old[1:].mean(dim=0), old[1:].std(dim=0)
    if init == "official":
        new = torch.randn((n_new, old.size(1)), generator=g, dtype=old.dtype)
    elif init == "matched":
        new = mu + sdv * torch.randn((n_new, old.size(1)), generator=g, dtype=old.dtype)
    else:
        raise ValueError(init)
    emb = torch.cat([old, new])
    if reinit_rows:
        assert init == "matched", "re-initialization is defined with matched statistics"
        assert all(1 <= r < old.size(0) for r in reinit_rows), "only pretrained rows (not the filler) can be re-initialized"
        emb[reinit_rows] = mu + sdv * torch.randn((len(reinit_rows), old.size(1)), generator=g, dtype=old.dtype)
    sd[EMBED_KEY] = emb.contiguous()
    save_file(sd, str(dst))
    return dst


class Sampler(threading.Thread):
    """Samples GPU utilisation/memory (nvidia-smi) and host CPU/RAM every `period` seconds."""

    def __init__(self, period: float = 2.0):
        super().__init__(daemon=True)
        import psutil
        self.proc, self.period, self.samples, self._halt = psutil.Process(os.getpid()), period, [], threading.Event()
        self.proc.cpu_percent(None)

    def run(self):
        while not self._halt.is_set():
            try:
                q = subprocess.run(["nvidia-smi", "--query-gpu=utilization.gpu,memory.used,power.draw",
                                    "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=5)
                util, mem, power = [float(x) for x in q.stdout.strip().split(",")]
            except Exception:
                util = mem = power = float("nan")
            try:
                rss = self.proc.memory_info().rss + sum(c.memory_info().rss
                                                        for c in self.proc.children(recursive=True))
            except Exception:
                rss = float("nan")
            self.samples.append({"t": time.time(), "gpu_util": util, "gpu_mem_mb": mem, "power_w": power,
                                 "cpu_pct": self.proc.cpu_percent(None), "host_rss_mb": rss / 2**20})
            self._halt.wait(self.period)

    def stop(self):
        self._halt.set()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rep", required=True)
    ap.add_argument("--subset", required=True)
    ap.add_argument("--run", type=Path, required=True)
    ap.add_argument("--batch-frames", type=int, default=2000)
    ap.add_argument("--max-samples", type=int, default=64)
    ap.add_argument("--grad-accum", type=int, default=1)
    ap.add_argument("--lr", type=float, default=1e-5)
    ap.add_argument("--warmup", type=int, default=100)
    ap.add_argument("--epochs", type=int, default=100)
    ap.add_argument("--max-updates", type=int, default=0, help="stop after this many updates (probe)")
    ap.add_argument("--checkpoint-activations", action="store_true")
    ap.add_argument("--bnb-optimizer", action="store_true")
    ap.add_argument("--num-workers", type=int, default=4)
    ap.add_argument("--save-per-updates", type=int, default=10**9)
    ap.add_argument("--seed", type=int, default=666)
    ap.add_argument("--probe", action="store_true")
    args = ap.parse_args()

    from f5_tts.model import CFM, DiT, Trainer
    from f5_tts.model.dataset import CustomDataset

    args.run.mkdir(parents=True, exist_ok=True)
    torch.manual_seed(args.seed)
    vocab_map, vocab_path = load_vocab(args.rep)
    train_hf, durations = build_dataset(args.rep, args.subset, vocab_map)
    ckpt = expanded_checkpoint(len(vocab_map), args.run)

    model = CFM(transformer=DiT(**ARCH, checkpoint_activations=args.checkpoint_activations,
                                text_num_embeds=len(vocab_map), mel_dim=MEL["n_mel_channels"]),
                mel_spec_kwargs=MEL, vocab_char_map=vocab_map)
    trainer = Trainer(model, args.epochs, args.lr, num_warmup_updates=args.warmup,
                      save_per_updates=args.save_per_updates, keep_last_n_checkpoints=1,
                      checkpoint_path=str(args.run), batch_size_per_gpu=args.batch_frames, batch_size_type="frame",
                      max_samples=args.max_samples, grad_accumulation_steps=args.grad_accum, max_grad_norm=1.0,
                      logger=None, log_samples=False, last_per_updates=10**9, bnb_optimizer=args.bnb_optimizer,
                      accelerate_kwargs={"mixed_precision": "bf16"})
    dataset = CustomDataset(train_hf, durations=durations, preprocessed_mel=False, **MEL)

    config = {**vars(args), "run": str(args.run), "vocab_file": str(vocab_path), "vocab_size": len(vocab_map),
              "pretrained": str(ckpt), "arch": ARCH, "mel": MEL, "n_utts": len(durations),
              "audio_hours": sum(durations) / 3600, "torch": torch.__version__,
              "gpu": torch.cuda.get_device_name(0)}
    (args.run / "config.json").write_text(json.dumps(config, indent=2, default=str), encoding="utf-8")

    log: list[dict] = []
    t_first = None
    sampler = Sampler() if args.probe else None
    if args.probe:
        orig_backward = trainer.accelerator.backward

        def backward(loss, **kw):
            nonlocal t_first
            out = orig_backward(loss, **kw)
            torch.cuda.synchronize()
            now = time.time()
            t_first = t_first or now
            log.append({"t": now, "loss": float(loss.detach())})
            if args.max_updates and len(log) >= args.max_updates * args.grad_accum:
                raise StopProbe
            return out

        trainer.accelerator.backward = backward
        sampler.start()
    torch.cuda.reset_peak_memory_stats()
    t0 = time.time()
    try:
        trainer.train(dataset, num_workers=args.num_workers, resumable_with_seed=args.seed)
    except StopProbe:
        pass
    wall = time.time() - t0
    if args.probe:
        sampler.stop()
        ts = time.time()
        trainer.save_checkpoint(len(log) // args.grad_accum, last=True)
        save_s = time.time() - ts
        ck = args.run / "model_last.pt"
        steady = [x for x in log if x["t"] - log[0]["t"] > 20]  # skip warm-up / dataloader start
        dt = (steady[-1]["t"] - steady[0]["t"]) / max(1, len(steady) - 1) if len(steady) > 2 else float("nan")
        gs = [s for s in sampler.samples if s["t"] >= (steady[0]["t"] if steady else t0)]

        def mean(key):
            vals = [s[key] for s in gs if s[key] == s[key]]
            return sum(vals) / len(vals) if vals else None

        stats = {
            "updates": len(log) // args.grad_accum, "micro_batches": len(log), "wall_s": wall,
            "time_to_first_update_s": (t_first - t0) if t_first else None,
            "steady_s_per_micro_batch": dt, "steady_s_per_update": dt * args.grad_accum,
            "updates_per_s": 1 / (dt * args.grad_accum) if dt == dt else None,
            "max_audio_s_per_micro_batch": args.batch_frames * MEL["hop_length"] / MEL["target_sample_rate"],
            "peak_vram_allocated_gb": torch.cuda.max_memory_allocated() / 2**30,
            "peak_vram_reserved_gb": torch.cuda.max_memory_reserved() / 2**30,
            "nvidia_smi_peak_mem_gb": max(s["gpu_mem_mb"] for s in sampler.samples) / 1024 if sampler.samples else None,
            "gpu_util_mean": mean("gpu_util"), "power_w_mean": mean("power_w"), "cpu_pct_mean": mean("cpu_pct"),
            "host_rss_peak_gb": max(s["host_rss_mb"] for s in sampler.samples) / 1024 if sampler.samples else None,
            "checkpoint_file_gb": ck.stat().st_size / 2**30 if ck.exists() else None,
            "checkpoint_save_s": save_s,
            "loss_first10_mean": sum(x["loss"] for x in log[:10]) / max(1, len(log[:10])),
            "loss_last10_mean": sum(x["loss"] for x in log[-10:]) / max(1, len(log[-10:])),
            "train_audio_hours": sum(durations) / 3600,
        }
        (args.run / "probe_stats.json").write_text(json.dumps(stats, indent=2), encoding="utf-8")
        with open(args.run / "probe_updates.tsv", "w", encoding="utf-8") as f:
            f.write("i\tt\tloss\n" + "".join(f"{i}\t{x['t']:.3f}\t{x['loss']:.5f}\n" for i, x in enumerate(log)))
        with open(args.run / "probe_sampler.tsv", "w", encoding="utf-8") as f:
            keys = list(sampler.samples[0]) if sampler.samples else []
            f.write("\t".join(keys) + "\n" + "".join("\t".join(f"{s[k]:.3f}" for k in keys) + "\n"
                                                    for s in sampler.samples))
        print(json.dumps(stats, indent=2))
        if ck.exists():
            ck.unlink()  # probe checkpoints are not kept (size recorded above)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
