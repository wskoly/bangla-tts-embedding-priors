"""Embedding-LR check (pilot_v7 + base-LR arms), pre-specified contrasts + gate G6 (D-043).

Arms with the text-embedding table at 10x base LR ("-elr10") vs the same arms at base LR.
Contrasts (fixed before results), A - B:
  per arm: <arm>-elr10 - <arm>                does a higher embedding LR change the fresh-row arm?
  BN-G-matched-elr10 - BN-G-iv-vm-asp-elr10   encoding gap (D-035) at the higher embedding LR
  LAT-P-reinit-elr10 - LAT-P                  reuse gap (D-031) at the higher embedding LR (LAT-P at base LR)
  interaction (BN-G-matched-elr10 - BN-G-iv-vm-asp-elr10) - (BN-G-matched - BN-G-iv-vm-asp)
                                              does the encoding gap shrink with the higher embedding LR?
G6: |delta| > 95 % CI half-width and > 2 x max seed SD over the arms involved.
Usage: python tools/analyze_controls_v7.py [--asr <tag>]
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

V7 = json.loads((ROOT / "configs/pilot_v7.json").read_text(encoding="utf-8"))
ARMS = {a: c["version"] for c in V7["compare_with"] for a in c["arms"]} | {a: "pilot_v7" for a in V7["arms"]}
SHOW = ["BN-G-matched", "BN-G-matched-elr10", "BN-G-iv-vm-asp", "BN-G-iv-vm-asp-elr10",
        "LAT-P-reinit", "LAT-P-reinit-elr10", "LAT-P"]
CONTRASTS = [("BN-G-matched-elr10", "BN-G-matched"), ("BN-G-iv-vm-asp-elr10", "BN-G-iv-vm-asp"),
             ("LAT-P-reinit-elr10", "LAT-P-reinit"), ("BN-G-matched-elr10", "BN-G-iv-vm-asp-elr10"),
             ("LAT-P-reinit-elr10", "LAT-P")]
INTERACTION = (("BN-G-matched-elr10", "BN-G-iv-vm-asp-elr10"), ("BN-G-matched", "BN-G-iv-vm-asp"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--asr", default=V7["eval"]["asr_primary"].split("/")[-1])
    args = ap.parse_args()
    seeds, subset, ev = V7["train"]["seeds"], V7["train_subset_pilot"], V7["eval"]
    runs = {a: [ROOT / "runs" / ARMS[a] / f"{a}__{subset}__s{s}" for s in seeds] for a in SHOW}
    done = {a: [r for r in rs if (r / "eval_summary.json").exists()] for a, rs in runs.items()}
    final_u = max(ev["eval_updates"])
    lines = [f"# Embedding-LR check (ASR `{args.asr}`)", "",
             "Complete runs: " + ", ".join(f"{a} {len(done[a])}/{len(seeds)}" for a in SHOW) + ". Observations only.", "",
             "## Fixed set CER % by update (mean of seeds)", "",
             "| arm | " + " | ".join(f"u{u}" for u in ev["eval_updates"]) + " |",
             "|---|" + "---|" * len(ev["eval_updates"])]
    for a in SHOW:
        if done[a]:
            lines.append(f"| {a} | " + " | ".join(
                f"{statistics.mean(seed_mean(done[a], u, 'fixed_v1', args.asr)[1]):.1f}"
                for u in ev["eval_updates"]) + " |")
    for split in ev["final_eval_sets"]:
        lines += ["", f"## {split} at u{final_u}" + (" (PRIMARY)" if split == "test_seen" else ""), "",
                  "| arm | CER mean | per-seed | seed SD |", "|---|---|---|---|"]
        avg, sd = {}, {}
        for a in SHOW:
            if not done[a]:
                continue
            avg[a], per = seed_mean(done[a], final_u, split, args.asr)
            sd[a] = statistics.stdev(per) if len(per) > 1 else float("nan")
            lines.append(f"| {a} | {statistics.mean(per):.2f} | {', '.join(f'{x:.2f}' for x in per)} | {sd[a]:.2f} |")
        lines += ["", "| contrast | ΔCER | paired 95 % CI | half-width | 2 × max seed SD | G6 |",
                  "|---|---|---|---|---|---|"]
        rows = [(f"{a} − {b}", (a, b), paired_diff(avg[a], avg[b]) if a in avg and b in avg else None)
                for a, b in CONTRASTS]
        (a1, b1), (a2, b2) = INTERACTION
        arms4 = (a1, b1, a2, b2)
        rows.append((f"({a1} − {b1}) − ({a2} − {b2})", arms4,
                     diff_of_diffs(*(avg[x] for x in arms4)) if all(x in avg for x in arms4) else None))
        for label, involved, res in rows:
            if res is None:
                continue
            d, (lo, hi) = res
            half, two_sd = (hi - lo) / 2, 2 * max(sd[x] for x in involved)
            lines.append(f"| {label} | {d:+.2f} | [{lo:+.2f}, {hi:+.2f}] | {half:.2f} | {two_sd:.2f} | "
                         f"{'YES' if abs(d) > half and abs(d) > two_sd else 'no'} |")
    out = ROOT / "docs/reports" / f"controls_v7_analysis_{args.asr}.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
