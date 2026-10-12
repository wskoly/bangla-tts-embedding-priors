"""C5 causal controls (D-067; plan docs/C5_analysis_plan.md). Written and frozen before the C5 runs.

C5a: fresh-row initialization seeds 1001/1002 (training seed 666) for H1a and the H3 path.
C5b: two further derangements of the LAT-P alphabet for H2 (training seeds 666 and 1234).
    python tools/analyze_c5.py
"""

from __future__ import annotations

import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import analyze_c3 as c3  # noqa: E402
from analyze_pilot_v1_1 import corpus_cer, paired_diff, per_utt, seed_mean  # noqa: E402

PRIMARY, SECONDARY = c3.PRIMARY, c3.SECONDARY
U, SPLIT, SUB = 3000, "test_seen", "train_1h"
C5 = ROOT / "runs/pilot_c5"
INIT_SEEDS = (1001, 1002)


def ref(arm: str, seed: int) -> Path:
    """Original run (initialization seed 666) of an arm at a training seed."""
    return dict(zip((666, 1234, 4242), c3.run_dirs(arm)))[seed]


def c5(arm: str, seed: int) -> Path:
    return C5 / f"{arm}__{SUB}__s{seed}"


def done(*runs: Path) -> bool:
    return all((r / "eval_summary.json").exists() for r in runs)


def c3_sd(arm: str) -> float:
    return c3.stats(arm, SPLIT, PRIMARY)[2]


def gate(d, lo, hi, two_sd, sign, w2v):
    half = (hi - lo) / 2
    big = abs(d) > half and abs(d) > two_sd
    if big and d * sign > 0:
        return half, "pass" if w2v * sign > 0 else "pass (primary only)"
    return half, "reversed" if big else "not passed"


def single(a: Path, b: Path, sign: int, two_sd: float):
    d, (lo, hi) = paired_diff(per_utt(a, U, SPLIT, PRIMARY), per_utt(b, U, SPLIT, PRIMARY))
    w2v = paired_diff(per_utt(a, U, SPLIT, SECONDARY), per_utt(b, U, SPLIT, SECONDARY))[0]
    half, v = gate(d, lo, hi, two_sd, sign, w2v)
    return f"{d:+.2f} [{lo:+.2f}, {hi:+.2f}] | {half:.2f} | {two_sd:.2f} | {w2v:+.2f} | {v}"


def cer(run: Path) -> float:
    return corpus_cer(per_utt(run, U, SPLIT, PRIMARY))


def main() -> int:
    L = ["# C5 causal controls (D-067)", "",
         "Plan: `docs/C5_analysis_plan.md` (frozen before the runs). Whisper test_seen u3000, SLR37 train_1h.", "",
         "## C5a: fresh-row initialization seed", "",
         "| test | Δ [95% CI] | half | 2σ (C3) | w2v Δ | verdict |", "|---|---|---|---|---|---|"]
    for k in INIT_SEEDS:
        b = c5(f"LAT-P-reinit-is{k}", 666)
        L.append(f"| C5a-H1a-{k} | " + (single(ref("LAT-P", 666), b, -1, 2 * max(c3_sd("LAT-P"), c3_sd("LAT-P-reinit")))
                                        if done(b) else "pending | | | | pending") + " |")
        a, b = c5(f"BN-G-matched-is{k}", 666), c5(f"BN-G-iv-vm-asp-is{k}", 666)
        L.append(f"| C5a-H3path-{k} | " + (single(a, b, +1, 2 * max(c3_sd("BN-G-matched"), c3_sd("BN-G-iv-vm-asp")))
                                           if done(a, b) else "pending | | | | pending") + " |")
    L += ["", "Spread of the fresh-row arms (CER %, Whisper test_seen):", "",
          "| arm | init seeds 666 / 1001 / 1002 (train seed 666) | SD | train seeds 666 / 1234 / 4242 (init 666) | SD |",
          "|---|---|---|---|---|"]
    for a in ("BN-G-matched", "LAT-P-reinit", "BN-G-iv-vm-asp"):
        tr = [cer(r) for r in c3.run_dirs(a)]
        runs = [ref(a, 666)] + [c5(f"{a}-is{k}", 666) for k in INIT_SEEDS]
        ini = [cer(r) for r in runs] if done(*runs) else None
        L.append(f"| {a} | " + (f"{' / '.join(f'{x:.2f}' for x in ini)} | {statistics.stdev(ini):.2f}" if ini
                                else "pending | ") + f" | {' / '.join(f'{x:.2f}' for x in tr)} | {statistics.stdev(tr):.2f} |")

    L += ["", "## C5b: choice of scrambled alphabet (H2)", "",
          "| test | Δ [95% CI] | half | 2σ | w2v Δ | verdict |", "|---|---|---|---|---|---|"]
    reinit = [ref("LAT-P-reinit", s) for s in (666, 1234)]
    for r in ("LAT-P-rand2", "LAT-P-rand3"):
        runs = [c5(r, s) for s in (666, 1234)]
        if not done(*runs):
            L.append(f"| C5b-H2-{r[-1]} | pending | | | | pending |")
            continue
        a, pa = seed_mean(runs, U, SPLIT, PRIMARY)
        b, pb = seed_mean(reinit, U, SPLIT, PRIMARY)
        d, (lo, hi) = paired_diff(a, b)
        w2v = paired_diff(seed_mean(runs, U, SPLIT, SECONDARY)[0], seed_mean(reinit, U, SPLIT, SECONDARY)[0])[0]
        two_sd = 2 * max(statistics.stdev(pa), statistics.stdev(pb))
        half, v = gate(d, lo, hi, two_sd, +1, w2v)
        L.append(f"| C5b-H2-{r[-1]} | {d:+.2f} [{lo:+.2f}, {hi:+.2f}] | {half:.2f} | {two_sd:.2f} | {w2v:+.2f} | {v} |")
    L += ["", "CER of every derangement (Whisper test_seen, training seeds 666 / 1234):", ""]
    for r in ("LAT-P-rand", "LAT-P-rand2", "LAT-P-rand3"):
        runs = [ref(r, s) for s in (666, 1234)] if r == "LAT-P-rand" else [c5(r, s) for s in (666, 1234)]
        L.append(f"- {r}: " + (" / ".join(f"{cer(x):.2f}" for x in runs) if done(*runs) else "pending"))
    out = ROOT / "docs/reports/c5_controls.md"
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
