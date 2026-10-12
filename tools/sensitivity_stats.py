"""Post hoc sensitivity analyses for the frozen C3 and C1 tests (D-070). These do NOT replace the frozen verdicts.

For every frozen test (C3: 13, C1: 5), on the same primary data as the frozen analysis
(Whisper, test_seen, u3000; C1 H1a/H2 on the lexicon-covered subset):
  1. two-level bootstrap: resample seeds (per arm, with replacement) and sentences (shared across arms), 2,000 draws;
     95 % interval and a two-sided bootstrap p-value (equivalence test H3a: interval only);
  2. Holm adjustment of those p-values across all 17 directional tests;
  3. per-seed consistency: number of training seeds whose own contrast has the predicted sign;
  4. effect sizes: relative change in CER (Delta / CER of the comparison arm) and Cohen's d_z on per-sentence
     differences of seed-mean CER;
  5. a paired t-test on per-sentence differences of seed-mean CER (second inferential route).
     A linear mixed model was tried first (statsmodels MixedLM, run variance component) and dropped: its standard
     errors were implausibly small (e.g. 0.05 pp for H3b where the paired SD implies ~0.7), i.e. misspecified.
    python tools/sensitivity_stats.py   -> docs/reports/sensitivity_stats.md, paper/sensitivity.json
"""

from __future__ import annotations

import json
import os
import sys
import warnings
from pathlib import Path

import numpy as np

os.environ["DATA_PROFILE"] = "rasa_bn_v1"
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import analyze_c1 as c1  # noqa: E402
import analyze_c3 as c3  # noqa: E402
from analyze_pilot_v1_1 import per_utt  # noqa: E402

ASR, SPLIT, U, B, SEED = c3.PRIMARY, "test_seen", 3000, 2000, 20261012


def tests() -> list[dict]:
    out = [{"study": "C3", "id": t, "kind": k, "arms": a, "sign": s, "mod": c3, "sub": "all"} for t, k, a, s in c3.TESTS]
    out += [{"study": "C1", "id": t, "kind": k, "arms": a, "sign": s, "mod": c1, "sub": sub} for t, k, a, s, sub in c1.TESTS]
    return out


def matrices(t: dict) -> tuple[list[np.ndarray], np.ndarray, list[str]]:
    per = [[per_utt(r, U, SPLIT, ASR) for r in t["mod"].run_dirs(a)] for a in t["arms"]]
    ids = set.intersection(*(set(p) for seeds in per for p in seeds))
    if t["sub"] == "covered":
        ids = c1.covered(SPLIT, ids)
    ids = sorted(ids)
    E = [np.array([[p[i][0] for i in ids] for p in seeds]) for seeds in per]  # arms x (seeds, utts)
    N = np.array([per[0][0][i][1] for i in ids], dtype=float)
    return E, N, ids


def combine(kind: str, c: list[float]) -> float:
    return c[0] - c[1] if kind in ("diff", "eq") else (c[0] - c[1]) - (c[2] - c[3])


def two_level(t, E, N, rng) -> np.ndarray:
    n, out = len(N), np.empty(B)
    for b in range(B):
        u = rng.integers(n, size=n)
        cs = []
        for e in E:
            s = rng.integers(e.shape[0], size=e.shape[0])
            cs.append(100 * e[s][:, u].mean(0).sum() / N[u].sum())
        out[b] = combine(t["kind"], cs)
    return out


def holm(ps: dict[str, float]) -> dict[str, float]:
    order, m, out, run = sorted(ps, key=ps.get), len(ps), {}, 0.0
    for i, k in enumerate(order):
        run = max(run, min(1.0, (m - i) * ps[k]))
        out[k] = run
    return out


def main() -> int:
    rng = np.random.default_rng(SEED)
    res = {}
    for t in tests():
        E, N, ids = matrices(t)
        cer = [100 * e.mean(0).sum() / N.sum() for e in E]
        d = combine(t["kind"], cer)
        bs = two_level(t, E, N, rng)
        lo, hi = np.percentile(bs, [2.5, 97.5])
        p = None if t["kind"] == "eq" else float(max(2 * min((bs <= 0).mean(), (bs >= 0).mean()), 1 / B))
        k = min(e.shape[0] for e in E)
        per_seed = [combine(t["kind"], [100 * e[j].sum() / N.sum() for e in E]) for j in range(k)]
        agree = sum(1 for x in per_seed if x * t["sign"] > 0) if t["sign"] else None
        ref = cer[1] if t["kind"] != "dd" else None
        diffs = (E[0].mean(0) - E[1].mean(0)) / N * 100 if t["kind"] != "dd" else \
            ((E[0].mean(0) - E[1].mean(0)) - (E[2].mean(0) - E[3].mean(0))) / N * 100
        dz = float(diffs.mean() / diffs.std(ddof=1))
        from scipy.stats import t as tdist
        tstat = dz * np.sqrt(len(diffs))
        pt = float(2 * tdist.sf(abs(tstat), len(diffs) - 1))
        res[f"{t['study']}.{t['id']}"] = {
            "study": t["study"], "id": t["id"], "kind": t["kind"], "sign": t["sign"], "n_utts": len(ids),
            "seeds": [e.shape[0] for e in E], "d": d, "boot2_lo": float(lo), "boot2_hi": float(hi), "p_boot2": p,
            "per_seed": per_seed, "seeds_agree": agree, "rel_change_pct": (100 * d / ref) if ref else None,
            "dz": dz, "t": float(tstat), "p_t": pt}
        print(t["study"], t["id"], f"{d:+.2f} [{lo:+.2f}, {hi:+.2f}]", flush=True)
    adj = holm({k: v["p_boot2"] for k, v in res.items() if v["p_boot2"] is not None})
    for k, v in res.items():
        v["p_holm"] = adj.get(k)
    (ROOT / "paper/sensitivity.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    L = ["# Post hoc sensitivity analyses (D-070)", "",
         "Do not replace the frozen C3/C1 verdicts. Primary data as frozen (Whisper, test_seen, u3000; C1 H1a/H2 on "
         "the covered subset). Two-level bootstrap resamples seeds and sentences (2,000 draws); Holm adjustment over "
         "the 17 directional tests (p floor 1/2000, so Holm values of 0.009 are the resolution limit); paired t-test on "
         "per-sentence differences of seed-mean CER (weights sentences equally, unlike corpus CER).", "",
         "| test | Δ | two-level 95 % CI | p (boot) | p (Holm) | seeds agreeing | rel. change | d_z | t | p (t) |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    fmtp = lambda x: "—" if x is None else ("<0.001" if x < 0.001 else f"{x:.3f}")  # noqa: E731
    for k, v in res.items():
        agree = "—" if v["seeds_agree"] is None else f"{v['seeds_agree']}/{min(v['seeds'])}"
        rel = "—" if v["rel_change_pct"] is None else f"{v['rel_change_pct']:+.0f} %"
        L.append(f"| {k} | {v['d']:+.2f} | [{v['boot2_lo']:+.2f}, {v['boot2_hi']:+.2f}] | {fmtp(v['p_boot2'])} | "
                 f"{fmtp(v['p_holm'])} | {agree} | {rel} | {v['dz']:+.2f} | {v['t']:+.1f} | {fmtp(v['p_t'])} |")
    (ROOT / "docs/reports/sensitivity_stats.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
