"""Bangla ASR scoring used for every intelligibility measurement (real or synthetic audio).

Scoring normalization is fixed *before* looking at any output (decision D-015):
  NFC, ZWJ/ZWNJ removed, audited transcript corrections (same as the TTS input), all Unicode
  punctuation removed (incl. danda), whitespace collapsed, Latin lower-cased; digits kept.
CER = character edit distance / reference characters (spaces included);
WER = word edit distance / reference words. Corpus-level metrics are ratio-of-sums.

CLI (ASR floor on real audio):
    python -m src.eval.asr --split data/derived/splits/v1/test_seen.tsv \
        --models bengaliAI/tugstugi_bengaliai-asr_whisper-medium,ai4bharat/indicwav2vec_v1_bengali \
        --out data/derived/asr_floor_v1 --report docs/reports/asr_floor_v1.md
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import re
import statistics
import unicodedata
from pathlib import Path

import jiwer
import numpy as np
import soundfile as sf
import torch
import torchaudio.functional as AF

from src.bnrep.normalize import normalize

ROOT = Path(__file__).resolve().parents[2]
from src.corpus.profile import MANIFEST  # noqa: E402  (D-057 data profile)
SEED = 20261006


def score_text(text: str) -> str:
    t = normalize(text)  # NFC + ZW removal + corrections + danda -> "."
    t = "".join(" " if unicodedata.category(c).startswith("P") else c for c in t)
    t = re.sub(r"[A-Za-z]+", lambda m: m.group(0).lower(), t)
    return re.sub(r"\s+", " ", t).strip()


def load_audio_16k(path: str) -> np.ndarray:
    x, sr = sf.read(path, dtype="float32", always_2d=True)
    x = torch.from_numpy(x.mean(axis=1))
    if sr != 16000:
        x = AF.resample(x, sr, 16000)
    return x.numpy()


class ASR:
    def __init__(self, model_id: str, device: str = "cuda"):
        from transformers import AutoConfig
        self.model_id, self.device = model_id, device
        cfg = AutoConfig.from_pretrained(model_id)
        self.kind = "whisper" if cfg.model_type == "whisper" else "ctc"
        if self.kind == "whisper":
            from transformers import WhisperForConditionalGeneration, WhisperProcessor
            self.proc = WhisperProcessor.from_pretrained(model_id)
            self.model = WhisperForConditionalGeneration.from_pretrained(
                model_id, torch_dtype=torch.float16).to(device).eval()
            if not hasattr(self.model.generation_config, "lang_to_id"):
                # fine-tunes saved with an old generation config reject `language=`; use the base model's
                from transformers import GenerationConfig
                base = {"medium": "openai/whisper-medium", "small": "openai/whisper-small",
                        "large": "openai/whisper-large-v2"}
                size = next((k for k in base if k in model_id), "medium")
                self.model.generation_config = GenerationConfig.from_pretrained(base[size])
        else:
            from transformers import AutoModelForCTC, Wav2Vec2Processor
            self.proc = Wav2Vec2Processor.from_pretrained(model_id)  # greedy CTC; no external LM decoder
            self.model = AutoModelForCTC.from_pretrained(model_id).to(device).eval()

    @torch.no_grad()
    def transcribe(self, audios: list[np.ndarray], batch: int = 8) -> list[str]:
        out = []
        for i in range(0, len(audios), batch):
            chunk = audios[i:i + batch]
            if self.kind == "whisper":
                feats = self.proc(chunk, sampling_rate=16000, return_tensors="pt").input_features
                ids = self.model.generate(feats.to(self.device, torch.float16), language="bn", task="transcribe",
                                          num_beams=1, max_new_tokens=225)
                out += self.proc.batch_decode(ids, skip_special_tokens=True)
            else:
                enc = self.proc(chunk, sampling_rate=16000, return_tensors="pt", padding=True)
                am = enc.get("attention_mask")
                logits = self.model(enc.input_values.to(self.device),
                                    attention_mask=None if am is None else am.to(self.device)).logits
                out += self.proc.batch_decode(logits.argmax(-1))
        return out


def utt_scores(ref: str, hyp: str) -> dict:
    r, h = score_text(ref), score_text(hyp)
    co = jiwer.process_characters(r, h)
    wo = jiwer.process_words(r, h)
    c_err = co.substitutions + co.deletions + co.insertions
    w_err = wo.substitutions + wo.deletions + wo.insertions
    # secondary (D-015b): space-insensitive CER; SLR37 writes case markers as separate words ("ইন্টেল এর")
    # while ASRs join them, so word segmentation alone inflates CER/WER on real speech
    r_ns, h_ns = r.replace(" ", ""), h.replace(" ", "")
    cns = jiwer.process_characters(r_ns, h_ns) if h_ns else None
    cns_err = (cns.substitutions + cns.deletions + cns.insertions) if cns else len(r_ns)
    return {"ref": r, "hyp": h, "c_err": c_err, "c_ref": len(r), "w_err": w_err, "w_ref": len(r.split()),
            "cns_err": cns_err, "cns_ref": len(r_ns),
            "cer": c_err / max(1, len(r)), "wer": w_err / max(1, len(r.split())),
            "cer_nospace": cns_err / max(1, len(r_ns))}


def corpus(rows: list[dict]) -> dict:
    return {"CER": 100 * sum(r["c_err"] for r in rows) / sum(r["c_ref"] for r in rows),
            "WER": 100 * sum(r["w_err"] for r in rows) / sum(r["w_ref"] for r in rows),
            "CER_nospace": 100 * sum(r["cns_err"] for r in rows) / sum(r["cns_ref"] for r in rows)}


def bootstrap(rows: list[dict], n: int = 2000) -> dict:
    rng = random.Random(SEED)
    cer, wer, cns = [], [], []
    for _ in range(n):
        m = corpus([rows[rng.randrange(len(rows))] for _ in rows])
        cer.append(m["CER"])
        wer.append(m["WER"])
        cns.append(m["CER_nospace"])

    def q(v, p):
        return sorted(v)[int(p * (len(v) - 1))]

    return {"CER_ci95": (q(cer, .025), q(cer, .975)), "WER_ci95": (q(wer, .025), q(wer, .975)),
            "CER_nospace_ci95": (q(cns, .025), q(cns, .975))}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", type=Path, action="append", required=True)
    ap.add_argument("--models", required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--report", type=Path, required=True)
    args = ap.parse_args()

    with open(MANIFEST, encoding="utf-8", newline="") as f:
        man = {r["utt_id"]: r for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE)}
    args.out.mkdir(parents=True, exist_ok=True)
    summary = {}
    for model_id in args.models.split(","):
        asr = ASR(model_id)
        for split in args.split:
            with open(split, encoding="utf-8") as f:
                ids = [r["utt_id"] for r in csv.DictReader(f, delimiter="\t")]
            audio = [load_audio_16k(str(ROOT / man[u]["path"])) for u in ids]
            hyps = asr.transcribe(audio)
            rows = [{"utt_id": u, **utt_scores(man[u]["text"], h)} for u, h in zip(ids, hyps)]
            tag = f"{model_id.split('/')[-1]}__{split.stem}"
            with open(args.out / f"{tag}.tsv", "w", encoding="utf-8", newline="\n") as f:
                f.write("utt_id\tcer\twer\tref\thyp\n")
                for r in sorted(rows, key=lambda r: -r["cer"]):
                    f.write(f"{r['utt_id']}\t{r['cer']:.4f}\t{r['wer']:.4f}\t{r['ref']}\t{r['hyp']}\n")
            ucer = [100 * r["cer"] for r in rows]
            uwer = [100 * r["wer"] for r in rows]
            summary[tag] = {**corpus(rows), **bootstrap(rows), "n": len(rows),
                            "utt_cer_mean": statistics.mean(ucer), "utt_cer_median": statistics.median(ucer),
                            "utt_cer_p90": sorted(ucer)[int(.9 * (len(ucer) - 1))],
                            "utt_wer_mean": statistics.mean(uwer), "utt_wer_median": statistics.median(uwer),
                            "pct_utt_cer_zero": 100 * sum(x == 0 for x in ucer) / len(ucer),
                            "hyps_with_digits": sum(bool(re.search(r"[0-9০-৯]", r["hyp"])) for r in rows)}
            print(tag, json.dumps(summary[tag], default=lambda x: x), flush=True)
        del asr
        torch.cuda.empty_cache()

    lines = ["# ASR noise floor on real SLR37 audio", "",
             "Scoring normalization fixed in advance (see `src/eval/asr.py`, D-015). "
             "Corpus CER/WER = ratio of summed errors; 95 % CI = utterance bootstrap (2,000 resamples).", "",
             "| model | split | n | CER % [95 % CI] | CER no-space % [95 % CI] | WER % [95 % CI] | "
             "utt CER mean / median / p90 | utt WER mean / median | % utts CER=0 | hyps with digits |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    for tag, s in summary.items():
        m, sp = tag.split("__")
        lines.append(f"| {m} | {sp} | {s['n']} | {s['CER']:.2f} [{s['CER_ci95'][0]:.2f}, {s['CER_ci95'][1]:.2f}] | "
                     f"{s['CER_nospace']:.2f} [{s['CER_nospace_ci95'][0]:.2f}, {s['CER_nospace_ci95'][1]:.2f}] | "
                     f"{s['WER']:.2f} [{s['WER_ci95'][0]:.2f}, {s['WER_ci95'][1]:.2f}] | "
                     f"{s['utt_cer_mean']:.2f} / {s['utt_cer_median']:.2f} / {s['utt_cer_p90']:.2f} | "
                     f"{s['utt_wer_mean']:.2f} / {s['utt_wer_median']:.2f} | {s['pct_utt_cer_zero']:.1f} | "
                     f"{s['hyps_with_digits']} |")
    lines += ["", f"Per-utterance outputs (worst first): `{args.out.as_posix()}/<model>__<split>.tsv`."]
    (args.out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
