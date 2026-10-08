"""LAT-G-det-reinit analysis (pilot_v3 + pilot_v1_1 + pilot_v2 arms), pre-specified contrasts + gate G6 (D-032).

Contrasts (fixed before results):
  LAT-G-det - LAT-G-det-reinit          reuse of pretrained rows, grapheme text (cf. LAT-P - LAT-P-reinit)
  LAT-G-det-reinit - LAT-P-reinit       grapheme vs phonemic content, both fresh rows, similar inventory/length
  BN-G-matched - LAT-G-det-reinit       same grapheme content, Bengali vs ITRANS tokenization, both fresh rows
  interaction  (LAT-G-det-reinit - LAT-G-det) - (LAT-P-reinit - LAT-P)
                                        does pretrained reuse help graphemes and phonemes equally?
G6: |delta| > 95 % CI half-width and > 2 x max seed SD over the arms involved.
Usage: python tools/analyze_controls_v3.py [--asr <tag>]
"""

from __future__ import annotations

import argparse
import json
import random
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from analyze_pilot_v1_1 import N_BOOT, SEED, corpus_cer, paired_diff, seed_mean  # noqa: E402

V3 = json.loads((ROOT / "configs/pilot_v3.json").read_text(encoding="utf-8"))
ARMS = {a: c["version"] for c in V3["compare_with"] for a in c["arms"]} | {a: "pilot_v3" for a in V3["arms"]}
CONTRASTS = [("LAT-G-det", "LAT-G-det-reinit"), ("LAT-G-det-reinit", "LAT-P-reinit"),
             ("BN-G-matched", "LAT-G-det-reinit")]
INTERACTION = (("LAT-G-det-reinit", "LAT-G-det"), ("LAT-P-reinit", "LAT-P"))


def diff_of_diffs(a1: dict, b1: dict, a2: dict, b2: dict) -> tuple[float, tuple[float, float]]:
    """(a1 - b1) - (a2 - b2) in corpus CER points, paired bootstrap over utterances."""
    ids = sorted(set(a1) & set(b1) & set(a2) & set(b2))
    sub = lambda d, s: {i: d[i] for i in s}  # noqa: E731
    point = (corpus_cer(sub(a1, ids)) - corpus_cer(sub(b1, ids))) - (corpus_cer(sub(a2, ids)) - corpus_cer(sub(b2, ids)))
    rng, boots = random.Random(SEED), []
    for _ in range(N_BOOT):
        s = [ids[rng.randrange(len(ids))] for _ in ids]
        c = [100 * sum(d[i][0] for i in s) / sum(d[i][1] for i in s) for d in (a1, b1, a2, b2)]
        boots.append((c[0] - c[1]) - (c[2] - c[3]))
    boots.sort()
    return point, (boots[int(.025 * (N_BOOT - 1))], boots[int(.975 * (N_BOOT - 1))])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--asr", default=V3["eval"]["asr_primary"].split("/")[-1])
    args = ap.parse_args()
    seeds, subset, ev = V3["train"]["seeds"], V3["train_subset_pilot"], V3["eval"]
    runs = {a: [ROOT / "runs" / v / f"{a}__{subset}__s{s}" for s in seeds] for a, v in ARMS.items()}
    done = {a: [r for r in rs if (r / "eval_summary.json").exists()] for a, rs in runs.items()}
    final_u = max(ev["eval_updates"])
    lines = [f"# LAT-G-det-reinit analysis (ASR `{args.asr}`)", "",
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
    out = ROOT / "docs/reports" / f"controls_v3_analysis_{args.asr}.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
