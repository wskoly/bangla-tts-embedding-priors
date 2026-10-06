"""Training/eval audio for F5: edge-silence trim (0.1 s margin) + resample to 24 kHz mono PCM16 (D-018).

Silence rule is identical to slr37_stats.py (20 ms frames, RMS below -40 dBFS). No loudness change.
The same processed file is used by every representation arm.

Usage: python -m src.corpus.prep_audio --out data/derived/audio24k_v1
Writes <out>/<utt_id>.wav and <out>/index.tsv (utt_id, path, duration_s, trimmed_lead_s, trimmed_trail_s).
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np
import soundfile as sf
import torch
import torchaudio.functional as AF

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "data/derived/slr37_bn_bd/manifest.tsv"
TARGET_SR = 24000
SILENCE_DBFS = -40.0
FRAME_MS = 20
MARGIN_S = 0.10


def trim_bounds(x: np.ndarray, sr: int) -> tuple[int, int]:
    hop = int(sr * FRAME_MS / 1000)
    n = len(x) // hop
    frames = x[: n * hop].reshape(n, hop)
    db = 20 * np.log10(np.sqrt((frames ** 2).mean(axis=1)) + 1e-12)
    voiced = np.where(db > SILENCE_DBFS)[0]
    if voiced.size == 0:
        return 0, len(x)
    margin = int(MARGIN_S * sr)
    start = max(0, voiced[0] * hop - margin)
    end = min(len(x), (voiced[-1] + 1) * hop + margin)
    return start, end


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=ROOT / "data/derived/audio24k_v1")
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    with open(MANIFEST, encoding="utf-8", newline="") as f:
        rows = [r for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE) if "unreadable" not in r["flags"]]
    lines = ["utt_id\tpath\tduration_s\ttrimmed_lead_s\ttrimmed_trail_s"]
    for i, r in enumerate(rows):
        x, sr = sf.read(ROOT / r["path"], dtype="float32", always_2d=True)
        x = x.mean(axis=1)
        s, e = trim_bounds(x, sr)
        y = AF.resample(torch.from_numpy(x[s:e]), sr, TARGET_SR).numpy()
        y = np.clip(y, -1.0, 1.0)
        path = args.out / f"{r['utt_id']}.wav"
        sf.write(path, y, TARGET_SR, subtype="PCM_16")
        lines.append(f"{r['utt_id']}\t{path.relative_to(ROOT).as_posix()}\t{len(y) / TARGET_SR:.4f}\t"
                     f"{s / sr:.4f}\t{(len(x) - e) / sr:.4f}")
        if (i + 1) % 500 == 0:
            print(f"  {i + 1}/{len(rows)}", flush=True)
    (args.out / "index.tsv").write_text("\n".join(lines) + "\n", encoding="utf-8")
    durs = [float(line.split("\t")[2]) for line in lines[1:]]
    print(f"files {len(durs)}; total {sum(durs) / 3600:.3f} h; mean {np.mean(durs):.2f} s; "
          f"min {min(durs):.2f}; max {max(durs):.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
