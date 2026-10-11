"""F5-TTS inference wrapper for the representation experiments (D-022).

Same model classes, checkpoint loading (f5_tts.infer.utils_infer.load_checkpoint, EMA weights, fp16),
vocoder and sampler (CFM.sample, NFE 32, CFG 2.0, sway -1) as the official infer path, with three
deliberate differences that remove arm-dependent confounds:
  1. text is passed as a plain string -> one token per code point through the arm's vocab
     (convert_char_to_pinyin bypassed, D-016); zero unknown symbols is asserted before sampling;
  2. duration = reference duration + ground-truth (trimmed) duration of the target utterance,
     identical for every arm (the official estimate uses a UTF-8 *byte*-length ratio, and a
     speed=0.3 rule for texts < 10 bytes, both of which depend on the script);
  3. reference and target text are always joined with exactly one space (the official path adds a
     space only when the reference ends in a 1-byte character, i.e. only for Latin text).

The synthesize functions accept text already converted to the arm's representation (`synth`), or
convert canonical Bengali via src.bnrep.reps (`synthesize_set`).

CLI (synthesize an eval set and measure speed):
    python -m src.infer.f5_infer --rep LAT-P --ckpt <ckpt> --out runs/infer/x [--eval-set fixed_v1] [--limit N]
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import time
from pathlib import Path

import numpy as np
import soundfile as sf
import torch

ROOT = Path(__file__).resolve().parents[2]
CONFIG = json.loads((ROOT / "configs/pilot_v1_1.json").read_text(encoding="utf-8"))
from src.corpus.profile import AUDIO_INDEX, EVAL_DIR  # noqa: E402  (D-057 data profile)
SR, HOP, TARGET_RMS = 24000, 256, 0.1


def utt_seed(utt_id: str) -> int:
    return int(hashlib.sha256(utt_id.encode()).hexdigest()[:8], 16)


class F5Synth:
    def __init__(self, rep: str, ckpt: str, device: str = "cuda", use_ema: bool = True):
        from f5_tts.infer.utils_infer import load_checkpoint, load_vocoder
        from f5_tts.model import CFM, DiT

        from src.train.f5_train import ARCH, MEL, load_vocab
        self.rep, self.device = rep, device
        self.vocab_map, self.vocab_path = load_vocab(rep)
        model = CFM(transformer=DiT(**ARCH, text_num_embeds=len(self.vocab_map), mel_dim=MEL["n_mel_channels"]),
                    mel_spec_kwargs=MEL, vocab_char_map=self.vocab_map)
        # use_ema=True for EMA checkpoints (official pretrained); False for online-weight snapshots (D-024)
        self.model = load_checkpoint(model, str(ckpt), device, use_ema=use_ema).eval()
        self.vocoder = load_vocoder("vocos", device=device)
        ev = CONFIG["eval"]
        self.nfe, self.cfg, self.sway = ev["nfe_step"], ev["cfg_strength"], ev["sway_sampling_coef"]

    @torch.inference_mode()
    def synth(self, ref_wav: str, ref_text: str, gen_text: str, gen_seconds: float, seed: int) -> np.ndarray:
        """ref_text / gen_text must already be in this arm's representation."""
        from src.train.vocab import encode
        text = ref_text.rstrip() + " " + gen_text.strip()
        encode(text, self.vocab_map)  # raises UnknownSymbolError on any unknown symbol
        audio, sr = sf.read(ref_wav, dtype="float32", always_2d=True)
        assert sr == SR, (ref_wav, sr)
        audio = torch.from_numpy(audio.mean(axis=1))[None].to(self.device)
        rms = torch.sqrt(torch.mean(audio ** 2))
        if rms < TARGET_RMS:
            audio = audio * TARGET_RMS / rms
        ref_frames = audio.shape[-1] // HOP
        duration = ref_frames + int(round(gen_seconds * SR / HOP))
        generated, _ = self.model.sample(cond=audio, text=[text], duration=duration, steps=self.nfe,
                                         cfg_strength=self.cfg, sway_sampling_coef=self.sway, seed=seed)
        mel = generated.to(torch.float32)[:, ref_frames:, :].permute(0, 2, 1)
        wave = self.vocoder.decode(mel)
        if rms < TARGET_RMS:
            wave = wave * rms / TARGET_RMS
        return wave.squeeze().cpu().numpy()


def load_eval(eval_set: str) -> tuple[list[dict], dict[str, dict]]:
    with open(EVAL_DIR / f"{eval_set}.tsv", encoding="utf-8") as f:
        items = list(csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE))
    with open(EVAL_DIR / "refs_v1.tsv", encoding="utf-8") as f:
        refs = {r["speaker"]: r for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE)}
    return items, refs


def synthesize_set(synth: F5Synth, items: list[dict], refs: dict[str, dict], out: Path) -> dict:
    from src.bnrep.reps import convert
    with open(AUDIO_INDEX, encoding="utf-8") as f:
        audio = {r["utt_id"]: r for r in csv.DictReader(f, delimiter="\t")}
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    torch.cuda.reset_peak_memory_stats()
    for it in items:
        ref = refs[it["speaker"]]
        ref_res, gen_res = convert(synth.rep, ref["text"]), convert(synth.rep, it["text"])
        assert not ref_res.oov and not gen_res.oov, (it["utt_id"], ref_res.oov, gen_res.oov)
        gen_s = float(audio[it["utt_id"]]["duration_s"])
        torch.cuda.synchronize()
        t0 = time.time()
        wav = synth.synth(str(ROOT / audio[ref["ref_utt_id"]]["path"]), ref_res.text, gen_res.text, gen_s,
                          utt_seed(it["utt_id"]))
        torch.cuda.synchronize()
        dt = time.time() - t0
        sf.write(out / f"{it['utt_id']}.wav", wav, SR, subtype="PCM_16")
        rows.append({"utt_id": it["utt_id"], "gen_s": dt, "audio_s": len(wav) / SR, "rtf": dt / (len(wav) / SR),
                     "text_chars": len(gen_res.text), "gen_text": gen_res.text})
    with open(out / "timing.tsv", "w", encoding="utf-8", newline="\n") as f:
        f.write("utt_id\tgen_s\taudio_s\trtf\ttext_chars\tgen_text\n")
        for r in rows:
            f.write(f"{r['utt_id']}\t{r['gen_s']:.3f}\t{r['audio_s']:.3f}\t{r['rtf']:.3f}\t{r['text_chars']}\t"
                    f"{r['gen_text']}\n")
    steady = rows[2:] if len(rows) > 4 else rows  # first calls include CUDA/cudnn warm-up
    tot_gen, tot_audio = sum(r["gen_s"] for r in steady), sum(r["audio_s"] for r in steady)
    summary = {"rep": synth.rep, "n": len(rows), "n_steady": len(steady),
               "gen_s_total_all": sum(r["gen_s"] for r in rows), "audio_s_total_all": sum(r["audio_s"] for r in rows),
               "gen_s_per_utt_median": float(np.median([r["gen_s"] for r in steady])),
               "audio_s_per_utt_median": float(np.median([r["audio_s"] for r in steady])),
               "rtf_corpus": tot_gen / tot_audio, "rtf_median": float(np.median([r["rtf"] for r in steady])),
               "first_call_s": rows[0]["gen_s"],
               "peak_vram_allocated_gb": torch.cuda.max_memory_allocated() / 2**30,
               "peak_vram_reserved_gb": torch.cuda.max_memory_reserved() / 2**30}
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rep", required=True)
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--eval-set", default="fixed_v1")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    t0 = time.time()
    synth = F5Synth(args.rep, args.ckpt)
    load_s = time.time() - t0
    items, refs = load_eval(args.eval_set)
    if args.limit:
        items = items[: args.limit]
    s = synthesize_set(synth, items, refs, args.out)
    s["model_load_s"] = load_s
    (args.out / "summary.json").write_text(json.dumps(s, indent=2), encoding="utf-8")
    print(json.dumps(s, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
