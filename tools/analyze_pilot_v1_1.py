"""Pilot v1_1 analysis: per-arm CER, seed variance, paired arm differences, gate G6 (D-025).

Gate G6 (pre-registered in D4 §5): an arm difference is a "measurable signal" if |ΔCER| exceeds BOTH
2 × the between-seed SD and the half-width of the paired-bootstrap 95 % CI. Primary set = test_seen
(decision D-013); test_unseen and the fixed-set checkpoints are reported alongside.

Paired bootstrap: per utterance, char errors are averaged over seeds, then utterances are resampled
jointly for both arms (same items), giving a CI on ΔCER = CER(A) − CER(B) (ratio of sums).

Usage: python tools/analyze_pilot_v1_1.py [--asr tugstugi_bengaliai-asr_whisper-medium]
"""

from __future__ import annotations

import argparse
import csv
import itertools
import json
import random
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "configs/pilot_v1_1.json").read_text(encoding="utf-8"))
RUNS = ROOT / "runs" / CONFIG["version"]
SEED = 20261006
N_BOOT = 2000


def per_utt(run: Path, update: int, split: str, asr: str) -> dict[str, tuple[float, int]]:
    """utt_id -> (char errors, ref chars), recovered exactly from stored CER × reference length."""
    path = run / "eval" / f"u{update}" / split / f"asr_{asr}.tsv"
    out = {}
    with open(path, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
            n = len(r["ref"])
            out[r["utt_id"]] = (float(r["cer"]) * max(1, n), n)
    return out


def corpus_cer(d: dict[str, tuple[float, int]]) -> float:
    return 100 * sum(e for e, _ in d.values()) / sum(n for _, n in d.values())


def paired_diff(a: dict, b: dict) -> tuple[float, tuple[float, float]]:
    ids = sorted(set(a) & set(b))
    rng = random.Random(SEED)
    point = corpus_cer({i: a[i] for i in ids}) - corpus_cer({i: b[i] for i in ids})
    boots = []
    for _ in range(N_BOOT):
        s = [ids[rng.randrange(len(ids))] for _ in ids]
        ea = sum(a[i][0] for i in s) / sum(a[i][1] for i in s)
        eb = sum(b[i][0] for i in s) / sum(b[i][1] for i in s)
        boots.append(100 * (ea - eb))
    boots.sort()
    return point, (boots[int(.025 * (N_BOOT - 1))], boots[int(.975 * (N_BOOT - 1))])


def seed_mean(runs: list[Path], update: int, split: str, asr: str) -> tuple[dict, list[float]]:
    per_seed = [per_utt(r, update, split, asr) for r in runs]
    ids = sorted(set.intersection(*(set(p) for p in per_seed)))
    avg = {i: (statistics.mean(p[i][0] for p in per_seed), per_seed[0][i][1]) for i in ids}
    return avg, [corpus_cer(p) for p in per_seed]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--asr", default=CONFIG["eval"]["asr_primary"].split("/")[-1])
    args = ap.parse_args()
    arms, seeds = CONFIG["arms"], CONFIG["train"]["seeds"]
    subset = CONFIG["train_subset_pilot"]
    runs = {a: [RUNS / f"{a}__{subset}__s{s}" for s in seeds] for a in arms}
    complete = {a: [r for r in rs if (r / "eval_summary.json").exists()] for a, rs in runs.items()}
    missing = [r.name for a in arms for r in runs[a] if r not in complete[a]]
    final_u = max(CONFIG["eval"]["eval_updates"])
    lines = [f"# Pilot {CONFIG['version']} analysis (ASR: `{args.asr}`)", "",
             f"Runs complete: {sum(len(v) for v in complete.values())}/{len(arms) * len(seeds)}"
             + (f"; missing: {missing}" if missing else "") + ". Observations only, no claims.", ""]

    lines += ["## Fixed eval set (50 utts): CER % by update (mean over seeds; per-seed in brackets)", "",
              "| arm | " + " | ".join(f"u{u}" for u in CONFIG["eval"]["eval_updates"]) + " |",
              "|---|" + "---|" * len(CONFIG["eval"]["eval_updates"])]
    for a in arms:
        if not complete[a]:
            continue
        cells = []
        for u in CONFIG["eval"]["eval_updates"]:
            _, per = seed_mean(complete[a], u, "fixed_v1", args.asr)
            cells.append(f"{statistics.mean(per):.1f} [{', '.join(f'{x:.1f}' for x in per)}]")
        lines.append(f"| {a} | " + " | ".join(cells) + " |")

    for split in CONFIG["eval"]["final_eval_sets"] + ["fixed_v1"]:
        lines += ["", f"## {split} at update {final_u}" + (" (PRIMARY)" if split == "test_seen" else ""), "",
                  "| arm | CER mean | per-seed CER | seed SD |", "|---|---|---|---|"]
        avgs, sds = {}, {}
        for a in arms:
            if not complete[a]:
                continue
            avg, per = seed_mean(complete[a], final_u, split, args.asr)
            avgs[a] = avg
            sds[a] = statistics.stdev(per) if len(per) > 1 else float("nan")
            lines.append(f"| {a} | {statistics.mean(per):.2f} | {', '.join(f'{x:.2f}' for x in per)} | {sds[a]:.2f} |")
        lines += ["", "| A − B | ΔCER | paired 95 % CI | CI half-width | 2 × max seed SD | G6 signal? |",
                  "|---|---|---|---|---|---|"]
        for a, b in itertools.combinations([x for x in arms if x in avgs], 2):
            d, (lo, hi) = paired_diff(avgs[a], avgs[b])
            half = (hi - lo) / 2
            two_sd = 2 * max(sds[a], sds[b])
            signal = abs(d) > half and abs(d) > two_sd
            lines.append(f"| {a} − {b} | {d:+.2f} | [{lo:+.2f}, {hi:+.2f}] | {half:.2f} | {two_sd:.2f} | "
                         f"{'YES' if signal else 'no'} |")
    lines += ["", "Notes: seed SD from n = 2 seeds is a weak variance estimate (NaN with one seed, so G6 cannot pass); "
                  "ΔCER < 0 means A has lower CER.",
              "G6 wording in D4 named the unseen-speaker set; D-013 made test_seen primary, so both are reported."]
    out = ROOT / "docs/reports" / f"{CONFIG['version']}_analysis_{args.asr}.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
