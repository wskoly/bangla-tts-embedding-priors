"""C3 hypothesis tests (D-046; plan: docs/C3_analysis_plan.md). Written and frozen before the C3 runs.

Primary metric: Whisper (tugstugi_bengaliai-asr_whisper-medium) CER on test_seen at u3000.
Base arms use 3 seeds (666, 1234 from their original pilot version; 4242 from pilot_v8a).
Embedding-LR arms use 2 seeds (666, 1234): x10 from pilot_v7, x3 / x30 from pilot_v8b.
Gate G6: |delta| > 95 % paired-bootstrap CI half-width AND > 2 x max seed SD of the arms involved,
in the predicted direction. H3a is an equivalence test: the 95 % CI must lie within +-5 CER.
Secondary agreement: wav2vec2 test_seen must have the same sign for "supported";
otherwise "supported (primary only)". test_unseen (both ASRs) is reported, not used for decisions.
Usage: python tools/analyze_c3.py
"""

from __future__ import annotations

import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from analyze_controls_v3 import diff_of_diffs  # noqa: E402
from analyze_pilot_v1_1 import paired_diff, seed_mean  # noqa: E402

PRIMARY, SECONDARY = "tugstugi_bengaliai-asr_whisper-medium", "wav2vec2-xls-r-300m-bengali"
SUBSET, FINAL_U, EQ_MARGIN = "train_1h", 3000, 5.0
ORIG = {"LAT-P": "pilot_v1_1", "LAT-G-det": "pilot_v1_1", "LAT-P-reinit": "pilot_v2", "LAT-P-rand": "pilot_v2",
        "BN-G-matched": "pilot_v2", "LAT-G-det-reinit": "pilot_v3", "BN-G-iv": "pilot_v4", "BN-G-iv-vm": "pilot_v4",
        "BN-G-iv-vm-asp": "pilot_v4", "LAT-G-asp": "pilot_v5"}
FRESH = ["BN-G-matched", "BN-G-iv-vm-asp", "LAT-P-reinit"]


def run_dirs(arm: str) -> list[Path]:
    if "-elr" in arm:
        version = "pilot_v7" if arm.endswith("-elr10") else "pilot_v8b"
        pairs = [(version, s) for s in (666, 1234)]
    else:
        pairs = [(ORIG[arm], 666), (ORIG[arm], 1234), ("pilot_v8a", 4242)]
    return [ROOT / "runs" / v / f"{arm}__{SUBSET}__s{s}" for v, s in pairs]


def stats(arm, split, asr):
    rs = run_dirs(arm)
    missing = [r for r in rs if not (r / "eval_summary.json").exists()]
    if missing:
        return None
    avg, per = seed_mean(rs, FINAL_U, split, asr)
    return avg, per, statistics.stdev(per)


# (id, kind, arms, predicted sign of delta); kind "diff": A - B; "dd": (A - B) - (C - D); "eq": equivalence
TESTS = [("H1a", "diff", ("LAT-P", "LAT-P-reinit"), -1),
         ("H1b", "diff", ("LAT-G-det", "LAT-G-det-reinit"), -1),
         *[(f"H1c-x{m}", "diff", ("LAT-P", f"LAT-P-reinit-elr{m}"), -1) for m in (3, 10, 30)],
         ("H2", "diff", ("LAT-P-rand", "LAT-P-reinit"), +1),
         ("H3a", "eq", ("BN-G-matched", "BN-G-iv"), 0),
         ("H3b", "diff", ("BN-G-iv", "BN-G-iv-vm"), +1),
         ("H3c", "diff", ("BN-G-iv-vm", "BN-G-iv-vm-asp"), +1),
         ("H4", "dd", ("BN-G-iv-vm-asp", "LAT-G-asp", "LAT-G-det-reinit", "LAT-G-det"), -1),
         *[(f"H5-x{m}", "diff", (f"BN-G-matched-elr{m}", f"BN-G-iv-vm-asp-elr{m}"), +1) for m in (3, 10, 30)]]


def evaluate(kind, arms, split, asr):
    st = [stats(a, split, asr) for a in arms]
    if any(s is None for s in st):
        return None
    d, (lo, hi) = (paired_diff(st[0][0], st[1][0]) if kind in ("diff", "eq")
                   else diff_of_diffs(*(s[0] for s in st)))
    return d, lo, hi, (hi - lo) / 2, 2 * max(s[2] for s in st)


def verdict(kind, sign, prim, sec):
    if prim is None:
        return "pending"
    d, lo, hi, half, two_sd = prim
    if kind == "eq":
        if -EQ_MARGIN <= lo and hi <= EQ_MARGIN:
            return "supported (equivalent within ±5)"
        return "falsified" if (lo > 0 or hi < 0) and abs(d) > EQ_MARGIN else "inconclusive"
    gated = abs(d) > half and abs(d) > two_sd
    if gated and d * sign > 0:
        return "supported" if sec is not None and sec[0] * sign > 0 else "supported (primary only)"
    return "falsified (gated, wrong sign)" if gated else "not supported (not gated)"


def main() -> int:
    lines = ["# C3 hypothesis tests (D-046)", "", "Plan: `docs/C3_analysis_plan.md` (frozen before runs). "
             "Primary: Whisper test_seen u3000. Observations on SLR37 (same data as exploration): robustness, not replication.", "",
             "## Arms", "", "| arm | seeds | Whisper seen CER (per seed) | SD |", "|---|---|---|---|"]
    arms = list(ORIG) + [f"{a}-elr{m}" for m in (3, 10, 30) for a in FRESH]
    for a in arms:
        s = stats(a, "test_seen", PRIMARY)
        lines.append(f"| {a} | {len(run_dirs(a))} | " + ("pending | — |" if s is None else
                     f"{statistics.mean(s[1]):.2f} ({', '.join(f'{x:.2f}' for x in s[1])}) | {s[2]:.2f} |"))
    lines += ["", "## Tests", "", "| id | contrast | predicted | Δ primary [95 % CI] | half | 2×SD | wav2vec2 seen Δ | "
              "Whisper unseen Δ | wav2vec2 unseen Δ | verdict |", "|---|---|---|---|---|---|---|---|---|---|"]
    for tid, kind, arms_, sign in TESTS:
        label = (f"{arms_[0]} − {arms_[1]}" if kind != "dd" else f"({arms_[0]} − {arms_[1]}) − ({arms_[2]} − {arms_[3]})")
        pred = {1: "> 0", -1: "< 0", 0: "|Δ| ≤ 5"}[sign]
        prim = evaluate(kind, arms_, "test_seen", PRIMARY)
        sec = evaluate(kind, arms_, "test_seen", SECONDARY)
        un = [evaluate(kind, arms_, "test_unseen", a) for a in (PRIMARY, SECONDARY)]
        f = lambda r: "—" if r is None else f"{r[0]:+.2f}"  # noqa: E731
        p = "pending" if prim is None else f"{prim[0]:+.2f} [{prim[1]:+.2f}, {prim[2]:+.2f}] | {prim[3]:.2f} | {prim[4]:.2f}"
        if prim is None:
            p += " | — | —"
        lines.append(f"| {tid} | {label} | {pred} | {p} | {f(sec)} | {f(un[0])} | {f(un[1])} | {verdict(kind, sign, prim, sec)} |")
    lines += ["", "Hypothesis-level: H1 = H1a ∧ H1b ∧ H1c-x3/x10/x30; H2; H3 = H3a ∧ H3b ∧ H3c; H4; "
              "H5 (LR stability) = H5-x3/x10/x30 ∧ H1c-x3/x10/x30 all supported with the same sign."]
    out = ROOT / "docs/reports/c3_hypothesis_tests.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
