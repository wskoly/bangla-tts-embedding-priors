"""Data-size curves (pilot_v6 + train_1h runs from pilot_v1_1/v4), pre-specified contrasts + gate G6 (D-039).

Fixed budget of 3000 updates at every size. Arms: BN-G, LAT-G-det, LAT-P, BN-G-iv-vm-asp.
Pre-specified, at each size (0.25 / 0.5 / 1 / 1.58 h), A - B on test_seen and test_unseen at u3000:
  LAT-G-det - LAT-P                 grapheme vs phonemic, both pretrained rows
  BN-G - LAT-G-det                  Bengali Unicode (fresh) vs ITRANS (pretrained)
  BN-G-iv-vm-asp - BN-G             improved Bengali encoding vs Bengali Unicode, both fresh
  BN-G-iv-vm-asp - LAT-G-det        best fresh-row arm vs ITRANS (pretrained)
Trend contrasts (does a gap change with data?), (A - B at 1.58 h) - (A - B at 0.25 h), for:
  LAT-G-det - LAT-P;  BN-G-iv-vm-asp - LAT-G-det
G6: |delta| > 95 % CI half-width and > 2 x max seed SD over the runs involved.
Usage: python tools/analyze_curves_v6.py [--asr <tag>]
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from analyze_controls_v3 import diff_of_diffs  # noqa: E402
from analyze_pilot_v1_1 import paired_diff, seed_mean  # noqa: E402

V6 = json.loads((ROOT / "configs/pilot_v6.json").read_text(encoding="utf-8"))
ARMS = list(V6["arms"])
SIZES = ["train_0.25h", "train_0.5h", "train_1h", "train_full"]
ONE_H = {a: c["version"] for c in V6["compare_with"] for a in c["arms"]}
CONTRASTS = [("LAT-G-det", "LAT-P"), ("BN-G", "LAT-G-det"), ("BN-G-iv-vm-asp", "BN-G"), ("BN-G-iv-vm-asp", "LAT-G-det")]
TRENDS = [("LAT-G-det", "LAT-P"), ("BN-G-iv-vm-asp", "LAT-G-det")]


def runs(arm: str, size: str) -> list[Path]:
    version = ONE_H[arm] if size == "train_1h" else V6["version"]
    rs = [ROOT / "runs" / version / f"{arm}__{size}__s{s}" for s in V6["train"]["seeds"]]
    return [r for r in rs if (r / "eval_summary.json").exists()]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--asr", default=V6["eval"]["asr_primary"].split("/")[-1])
    args = ap.parse_args()
    n_seeds, final_u, hours = len(V6["train"]["seeds"]), max(V6["eval"]["eval_updates"]), V6["subset_hours"]
    lines = [f"# Data-size curves (ASR `{args.asr}`)", "", "Fixed budget: 3000 updates at every size. Observations only.", "",
             "Complete runs: " + ", ".join(f"{a}@{hours[s]}h {len(runs(a, s))}/{n_seeds}" for s in SIZES for a in ARMS), ""]
    for split in V6["eval"]["final_eval_sets"]:
        avg, sd = {}, {}
        for a in ARMS:
            for s in SIZES:
                rs = runs(a, s)
                if len(rs) == n_seeds:
                    avg[a, s], per = seed_mean(rs, final_u, split, args.asr)
                    sd[a, s] = (statistics.stdev(per), statistics.mean(per), per)
        lines += [f"## {split} at u{final_u}" + (" (PRIMARY)" if split == "test_seen" else ""), "",
                  "| arm | " + " | ".join(f"{hours[s]} h" for s in SIZES) + " |", "|---|" + "---|" * len(SIZES)]
        for a in ARMS:
            lines.append(f"| {a} | " + " | ".join(
                f"{sd[a, s][1]:.2f} (±{sd[a, s][0]:.2f})" if (a, s) in sd else "—" for s in SIZES) + " |")
        lines += ["", "| size | contrast A − B | ΔCER | paired 95 % CI | half-width | 2 × max seed SD | G6 |",
                  "|---|---|---|---|---|---|---|"]

        def row(label, size, d, lo, hi, keys):
            half, two_sd = (hi - lo) / 2, 2 * max(sd[k][0] for k in keys)
            lines.append(f"| {size} | {label} | {d:+.2f} | [{lo:+.2f}, {hi:+.2f}] | {half:.2f} | {two_sd:.2f} | "
                         f"{'YES' if abs(d) > half and abs(d) > two_sd else 'no'} |")

        for s in SIZES:
            for a, b in CONTRASTS:
                if (a, s) in avg and (b, s) in avg:
                    d, (lo, hi) = paired_diff(avg[a, s], avg[b, s])
                    row(f"{a} − {b}", f"{hours[s]} h", d, lo, hi, [(a, s), (b, s)])
        lines += ["", "| scope | trend (A − B at 1.58 h) − (A − B at 0.25 h) | ΔΔCER | paired 95 % CI | half-width | 2 × max seed SD | G6 |",
                  "|---|---|---|---|---|---|---|"]
        hi_s, lo_s = SIZES[-1], SIZES[0]
        for a, b in TRENDS:
            keys = [(a, hi_s), (b, hi_s), (a, lo_s), (b, lo_s)]
            if all(k in avg for k in keys):
                d, (lo, hi) = diff_of_diffs(*(avg[k] for k in keys))
                row(f"{a} − {b}", "trend", d, lo, hi, keys)
        lines.append("")
    out = ROOT / "docs/reports" / f"curves_v6_analysis_{args.asr}.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
