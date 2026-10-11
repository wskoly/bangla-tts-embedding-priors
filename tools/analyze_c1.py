"""C1 replication tests (D-061; plan: docs/C1_analysis_plan.md). Written and frozen before the full C1 runs.

Primary metric: Whisper (tugstugi_bengaliai-asr_whisper-medium) CER on Rasa test_seen at u3000, mean over 3 seeds.
Seed 666 of the five pilot arms comes from pilot_c1a; everything else from pilot_c1b.
Tests involving a LAT-P arm (H1a, H2) use the coverage-restricted subset (every word in lexicon + supplement) as
primary; the others use all of test_seen. Gate G6 and the verdict rules are identical to C3 (tools/analyze_c3.py).
    DATA_PROFILE=rasa_bn_v1 python tools/analyze_c1.py
"""

from __future__ import annotations

import csv
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
from analyze_controls_v3 import diff_of_diffs  # noqa: E402
from analyze_pilot_v1_1 import corpus_cer, paired_diff, per_utt  # noqa: E402
from src.bnrep.reps import convert  # noqa: E402
from src.corpus.profile import MANIFEST, NAME  # noqa: E402

assert NAME == "rasa_bn_v1", NAME
PRIMARY, SECONDARY = "tugstugi_bengaliai-asr_whisper-medium", "wav2vec2-xls-r-300m-bengali"
SUBSET, FINAL_U, SEEDS = "train_1h", 3000, (666, 1234, 4242)
PILOT_ARMS = ["LAT-P", "LAT-P-reinit", "LAT-P-rand", "BN-G-matched", "BN-G-iv-vm-asp"]
ARMS = PILOT_ARMS + ["LAT-G-det", "LAT-G-det-reinit", "LAT-G-asp"]

# (id, kind, arms, predicted sign, primary subset); kind "diff": A - B; "dd": (A - B) - (C - D)
TESTS = [("H1a", "diff", ("LAT-P", "LAT-P-reinit"), -1, "covered"),
         ("H1b", "diff", ("LAT-G-det", "LAT-G-det-reinit"), -1, "all"),
         ("H2", "diff", ("LAT-P-rand", "LAT-P-reinit"), +1, "covered"),
         ("H3-path", "diff", ("BN-G-matched", "BN-G-iv-vm-asp"), +1, "all"),
         ("H4", "dd", ("BN-G-iv-vm-asp", "LAT-G-asp", "LAT-G-det-reinit", "LAT-G-det"), -1, "all")]


def run_dirs(arm: str) -> list[Path]:
    return [ROOT / "runs" / ("pilot_c1a" if arm in PILOT_ARMS and s == 666 else "pilot_c1b") / f"{arm}__{SUBSET}__s{s}"
            for s in SEEDS]


_COVERED: dict[str, set[str]] = {}


def covered(split: str, ids: set[str]) -> set[str]:
    if split not in _COVERED:
        with open(MANIFEST, encoding="utf-8", newline="") as f:
            text = {r["utt_id"]: r["text"] for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE)}
        _COVERED[split] = {u for u in ids if not convert("LAT-P", text[u]).oov}
    return _COVERED[split] & ids


def stats(arm, split, asr, sub):
    rs = run_dirs(arm)
    if any(not (r / "eval_summary.json").exists() for r in rs):
        return None
    per_seed = [per_utt(r, FINAL_U, split, asr) for r in rs]
    ids = set.intersection(*(set(p) for p in per_seed))
    if sub == "covered":
        ids = covered(split, ids)
    per_seed = [{i: p[i] for i in ids} for p in per_seed]
    avg = {i: (statistics.mean(p[i][0] for p in per_seed), per_seed[0][i][1]) for i in ids}
    cers = [corpus_cer(p) for p in per_seed]
    return avg, cers, statistics.stdev(cers)


def evaluate(kind, arms, split, asr, sub):
    st = [stats(a, split, asr, sub) for a in arms]
    if any(s is None for s in st):
        return None
    d, (lo, hi) = paired_diff(st[0][0], st[1][0]) if kind == "diff" else diff_of_diffs(*(s[0] for s in st))
    return d, lo, hi, (hi - lo) / 2, 2 * max(s[2] for s in st)


def verdict(sign, prim, sec):
    if prim is None:
        return "pending"
    d, lo, hi, half, two_sd = prim
    gated = abs(d) > half and abs(d) > two_sd
    if gated and d * sign > 0:
        return "replicated" if sec is not None and sec[0] * sign > 0 else "replicated (primary only)"
    return "reversed (gated, wrong sign)" if gated else "not replicated (not gated)"


def main() -> int:
    lines = ["# C1 replication tests (D-061)", "",
             "Plan: `docs/C1_analysis_plan.md` (frozen before the full runs). Corpus: Rasa bn (neutral), train_1h rasaF. "
             "Primary: Whisper test_seen u3000, mean of seeds 666/1234/4242; H1a/H2 primary on the coverage-restricted "
             "subset. Gate G6 as in C3.", "",
             "## Arms (Whisper test_seen CER, per seed)", "",
             "| arm | all (n=160): mean (per seed) | SD | covered: mean (per seed) | SD |", "|---|---|---|---|---|"]
    for a in ARMS:
        cells = []
        for sub in ("all", "covered"):
            s = stats(a, "test_seen", PRIMARY, sub)
            cells.append("pending | —" if s is None else
                         f"{statistics.mean(s[1]):.2f} ({', '.join(f'{x:.2f}' for x in s[1])}) | {s[2]:.2f}")
        lines.append(f"| {a} | " + " | ".join(cells) + " |")
    lines += ["", "## Tests", "", "| id | contrast | predicted | primary subset | Δ primary [95 % CI] | half | 2×SD | "
              "wav2vec2 Δ | Whisper Δ other subset | Whisper unseen Δ (all / covered) | wav2vec2 unseen Δ (all / covered) "
              "| verdict |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    f = lambda r: "—" if r is None else f"{r[0]:+.2f}"  # noqa: E731
    for tid, kind, arms_, sign, sub in TESTS:
        label = (f"{arms_[0]} − {arms_[1]}" if kind != "dd" else f"({arms_[0]} − {arms_[1]}) − ({arms_[2]} − {arms_[3]})")
        pred = {1: "> 0", -1: "< 0"}[sign]
        other = "all" if sub == "covered" else "covered"
        prim = evaluate(kind, arms_, "test_seen", PRIMARY, sub)
        sec = evaluate(kind, arms_, "test_seen", SECONDARY, sub)
        alt = evaluate(kind, arms_, "test_seen", PRIMARY, other)
        un = {(asr, s): evaluate(kind, arms_, "test_unseen", asr, s) for asr in (PRIMARY, SECONDARY) for s in ("all", "covered")}
        p = ("pending | — | —" if prim is None else
             f"{prim[0]:+.2f} [{prim[1]:+.2f}, {prim[2]:+.2f}] | {prim[3]:.2f} | {prim[4]:.2f}")
        lines.append(f"| {tid} | {label} | {pred} | {sub} | {p} | {f(sec)} | {f(alt)} | "
                     f"{f(un[(PRIMARY, 'all')])} / {f(un[(PRIMARY, 'covered')])} | "
                     f"{f(un[(SECONDARY, 'all')])} / {f(un[(SECONDARY, 'covered')])} | {verdict(sign, prim, sec)} |")
    lines += ["", "Hypothesis-level: H1 = H1a ∧ H1b; H2; H3-path; H4. 5 tests, no correction beyond G6."]
    out = ROOT / "docs/reports/c1_replication_tests.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
