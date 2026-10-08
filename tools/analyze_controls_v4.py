"""Encoding-path analysis (pilot_v4 + earlier arms), pre-specified contrasts + gate G6 (D-034).

Path from Bengali Unicode to ITRANS structure, all arms with fresh matched-init content rows:
  BN-G-matched -> BN-G-iv -> BN-G-iv-vm -> BN-G-iv-vm-asp -> LAT-G-det-reinit
Contrasts (fixed before results), each step A - B with A the earlier arm:
  BN-G-matched - BN-G-iv              explicit inherent vowel, hasanta dropped (abugida -> alphabet)
  BN-G-iv - BN-G-iv-vm                vowel signs merged with independent vowels
  BN-G-iv-vm - BN-G-iv-vm-asp         aspirates split into unaspirated + h
  BN-G-iv-vm-asp - LAT-G-det-reinit   residual (remaining ITRANS conventions: sibilant/retroflex digraphs, etc.)
G6: |delta| > 95 % CI half-width and > 2 x max seed SD of the two arms.
Usage: python tools/analyze_controls_v4.py [--asr <tag>]
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from analyze_pilot_v1_1 import paired_diff, seed_mean  # noqa: E402

V4 = json.loads((ROOT / "configs/pilot_v4.json").read_text(encoding="utf-8"))
ARMS = {a: c["version"] for c in V4["compare_with"] for a in c["arms"]} | {a: "pilot_v4" for a in V4["arms"]}
PATH = ["BN-G-matched", "BN-G-iv", "BN-G-iv-vm", "BN-G-iv-vm-asp", "LAT-G-det-reinit"]
CONTRASTS = list(zip(PATH, PATH[1:]))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--asr", default=V4["eval"]["asr_primary"].split("/")[-1])
    args = ap.parse_args()
    seeds, subset, ev = V4["train"]["seeds"], V4["train_subset_pilot"], V4["eval"]
    runs = {a: [ROOT / "runs" / v / f"{a}__{subset}__s{s}" for s in seeds] for a, v in ARMS.items()}
    done = {a: [r for r in rs if (r / "eval_summary.json").exists()] for a, rs in runs.items()}
    final_u = max(ev["eval_updates"])
    lines = [f"# Encoding-path analysis (ASR `{args.asr}`)", "",
             "Complete runs: " + ", ".join(f"{a} {len(done[a])}/{len(seeds)}" for a in PATH) + ". Observations only.", "",
             "## Fixed set CER % by update (mean of seeds)", "",
             "| arm | " + " | ".join(f"u{u}" for u in ev["eval_updates"]) + " |",
             "|---|" + "---|" * len(ev["eval_updates"])]
    for a in PATH:
        if done[a]:
            lines.append(f"| {a} | " + " | ".join(
                f"{statistics.mean(seed_mean(done[a], u, 'fixed_v1', args.asr)[1]):.1f}"
                for u in ev["eval_updates"]) + " |")
    for split in ev["final_eval_sets"]:
        lines += ["", f"## {split} at u{final_u}" + (" (PRIMARY)" if split == "test_seen" else ""), "",
                  "| arm | CER mean | per-seed | seed SD |", "|---|---|---|---|"]
        avg, sd = {}, {}
        for a in PATH:
            if not done[a]:
                continue
            avg[a], per = seed_mean(done[a], final_u, split, args.asr)
            sd[a] = statistics.stdev(per) if len(per) > 1 else float("nan")
            lines.append(f"| {a} | {statistics.mean(per):.2f} | {', '.join(f'{x:.2f}' for x in per)} | {sd[a]:.2f} |")
        lines += ["", "| step A − B | ΔCER | paired 95 % CI | half-width | 2 × max seed SD | G6 |",
                  "|---|---|---|---|---|---|"]
        for a, b in CONTRASTS:
            if a in avg and b in avg:
                d, (lo, hi) = paired_diff(avg[a], avg[b])
                half, two_sd = (hi - lo) / 2, 2 * max(sd[a], sd[b])
                lines.append(f"| {a} − {b} | {d:+.2f} | [{lo:+.2f}, {hi:+.2f}] | {half:.2f} | {two_sd:.2f} | "
                             f"{'YES' if abs(d) > half and abs(d) > two_sd else 'no'} |")
    out = ROOT / "docs/reports" / f"controls_v4_analysis_{args.asr}.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
