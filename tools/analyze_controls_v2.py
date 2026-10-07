"""Control analysis (pilot_v2 arms + pilot_v1_1 baselines), pre-specified contrasts + gate G6 (D-029).

Contrasts (fixed before results; see D-028):
  BN-G-matched vs BN-G            initialization scale of new embeddings
  LAT-P vs LAT-P-reinit           reuse of pretrained embeddings (same symbols, same text)
  LAT-P vs LAT-P-rand             pretrained letter-to-sound prior (embeddings reused in both)
  LAT-P-rand vs LAT-P-reinit      reused-but-scrambled vs fresh embeddings
  BN-G-matched vs LAT-P-reinit    phonemic vs grapheme content, both fresh matched embeddings
  BN-G-matched vs LAT-G-det       grapheme content: fresh Bengali vs reused Latin embeddings
Usage: python tools/analyze_controls_v2.py [--asr <tag>]
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

V2 = json.loads((ROOT / "configs/pilot_v2.json").read_text(encoding="utf-8"))
ARMS = {a: "pilot_v1_1" for a in V2["compare_with"]["arms"]} | {a: "pilot_v2" for a in V2["arms"]}
CONTRASTS = [("BN-G-matched", "BN-G"), ("LAT-P", "LAT-P-reinit"), ("LAT-P", "LAT-P-rand"),
             ("LAT-P-rand", "LAT-P-reinit"), ("BN-G-matched", "LAT-P-reinit"), ("BN-G-matched", "LAT-G-det")]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--asr", default=V2["eval"]["asr_primary"].split("/")[-1])
    args = ap.parse_args()
    seeds, subset, ev = V2["train"]["seeds"], V2["train_subset_pilot"], V2["eval"]
    runs = {a: [ROOT / "runs" / v / f"{a}__{subset}__s{s}" for s in seeds] for a, v in ARMS.items()}
    done = {a: [r for r in rs if (r / "eval_summary.json").exists()] for a, rs in runs.items()}
    final_u = max(ev["eval_updates"])
    lines = [f"# Control analysis (ASR `{args.asr}`)", "",
             "Complete runs: " + ", ".join(f"{a} {len(done[a])}/{len(seeds)}" for a in ARMS) + ". Observations only.", "",
             "## Fixed set CER % by update (mean of seeds)", "",
             "| arm | " + " | ".join(f"u{u}" for u in ev["eval_updates"]) + " |",
             "|---|" + "---|" * len(ev["eval_updates"])]
    for a in ARMS:
        if done[a]:
            lines.append(f"| {a} | " + " | ".join(
                f"{statistics.mean(seed_mean(done[a], u, 'fixed_v1', args.asr)[1]):.1f}"
                for u in ev["eval_updates"]) + " |")
    for split in ev["final_eval_sets"]:
        lines += ["", f"## {split} at u{final_u}" + (" (PRIMARY)" if split == "test_seen" else ""), "",
                  "| arm | CER mean | per-seed | seed SD |", "|---|---|---|---|"]
        avg, sd = {}, {}
        for a in ARMS:
            if not done[a]:
                continue
            avg[a], per = seed_mean(done[a], final_u, split, args.asr)
            sd[a] = statistics.stdev(per) if len(per) > 1 else float("nan")
            lines.append(f"| {a} | {statistics.mean(per):.2f} | {', '.join(f'{x:.2f}' for x in per)} | {sd[a]:.2f} |")
        lines += ["", "| contrast A − B | ΔCER | paired 95 % CI | half-width | 2 × max seed SD | G6 |",
                  "|---|---|---|---|---|---|"]
        for a, b in CONTRASTS:
            if a in avg and b in avg:
                d, (lo, hi) = paired_diff(avg[a], avg[b])
                half, two_sd = (hi - lo) / 2, 2 * max(sd[a], sd[b])
                lines.append(f"| {a} − {b} | {d:+.2f} | [{lo:+.2f}, {hi:+.2f}] | {half:.2f} | {two_sd:.2f} | "
                             f"{'YES' if abs(d) > half and abs(d) > two_sd else 'no'} |")
    out = ROOT / "docs/reports" / f"controls_v2_analysis_{args.asr}.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
