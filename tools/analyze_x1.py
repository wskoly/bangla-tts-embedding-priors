"""Exploratory long-training check (D-064): CER and the চ→ক confusion rate over 15k updates (pilot_x1) vs the
3k-update runs on the same data (pilot_v6 train_full). Whisper only; observations, no tests.
    python tools/analyze_x1.py
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASR = "tugstugi_bengaliai-asr_whisper-medium"
ARMS = ["LAT-P", "LAT-G-det"]


def rows(run: Path, u: int, split: str) -> list[dict]:
    with open(run / f"eval/u{u}/{split}/asr_{ASR}.tsv", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE))


def c_to_k(rs: list[dict]) -> tuple[float, int]:
    n = k = 0
    for r in rs:
        hyp = set(r["hyp"].split())
        for w in r["ref"].split():
            if "চ" in w:
                n += 1
                k += w.replace("চ", "ক") in hyp
    return 100 * k / max(n, 1), n


def cer(run: Path, u: int, split: str) -> float:
    s = json.loads((run / "eval_summary.json").read_text(encoding="utf-8"))
    return s["results"][f"{ASR}|u{u}|{split}"]["CER"]


def main() -> int:
    x1 = {a: ROOT / f"runs/pilot_x1/{a}__train_full__s666" for a in ARMS}
    v6 = {a: [ROOT / f"runs/pilot_v6/{a}__train_full__s{s}" for s in (666, 1234)] for a in ARMS}
    us = [0, 1000, 3000, 6000, 10000, 15000]
    L = ["# Long-training check (D-064, exploratory): SLR37 train_full, seed 666, Whisper", "",
         "## Fixed set (50 utts): CER % / চ→ক % by update (15k-update schedule)", "",
         "| arm | " + " | ".join(f"u{u}" for u in us) + " |", "|---|" + "---|" * len(us)]
    for a in ARMS:
        L.append(f"| {a} | " + " | ".join(f"{cer(x1[a], u, 'fixed_v1'):.2f} / {c_to_k(rows(x1[a], u, 'fixed_v1'))[0]:.1f}"
                                          for u in us) + " |")
    L += ["", "## test_seen / test_unseen: 3k-update runs (pilot_v6, s666 and s1234) vs 15k (pilot_x1, s666)", "",
          "| arm | split | 3k CER s666 / s1234 | 15k CER s666 | 3k চ→ক s666 / s1234 | 15k চ→ক s666 (n words) |",
          "|---|---|---|---|---|---|"]
    for a in ARMS:
        for sp in ("test_seen", "test_unseen"):
            c3 = " / ".join(f"{cer(r, 3000, sp):.2f}" for r in v6[a])
            k3 = " / ".join(f"{c_to_k(rows(r, 3000, sp))[0]:.1f}" for r in v6[a])
            k15, n = c_to_k(rows(x1[a], 15000, sp))
            L.append(f"| {a} | {sp} | {c3} | {cer(x1[a], 15000, sp):.2f} | {k3} | {k15:.1f} ({n}) |")
    out = ROOT / "docs/reports/long_training_x1.md"
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
