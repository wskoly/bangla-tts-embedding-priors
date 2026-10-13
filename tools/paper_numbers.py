"""Every number quoted in the paper, recomputed from the run outputs (paper plan Phase 1).

Writes paper/numbers.json (for figures) and paper/numbers.tex (LaTeX: \\V{key}), then checks the hypothesis-test
numbers against the frozen reports (docs/reports/c3_hypothesis_tests.md, c1_replication_tests.md) and fails on any
mismatch. No number in the paper is typed by hand.
    python tools/paper_numbers.py
"""

from __future__ import annotations

import json
import os
import re
import statistics
import sys
from pathlib import Path

os.environ["DATA_PROFILE"] = "rasa_bn_v1"  # analyze_c1 needs the Rasa manifest; analyze_c3 reads run dirs only
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import analyze_c1 as c1  # noqa: E402
import analyze_c3 as c3  # noqa: E402
import analyze_x1 as x1  # noqa: E402
from analyze_pilot_v1_1 import paired_diff, per_utt  # noqa: E402

ASRS = {"W": c3.PRIMARY, "V": c3.SECONDARY}
SPLITS = ("test_seen", "test_unseen")
OUT = ROOT / "paper"
TOL = 0.01


def fmt(x: float, signed: bool = False) -> str:
    s = f"{x:+.2f}" if signed else f"{x:.2f}"
    return s.replace("-", "$-$").replace("+", "$+$")


def summary_cer(run: Path, u: int, split: str, asr: str) -> float:
    s = json.loads((run / "eval_summary.json").read_text(encoding="utf-8"))
    return s["results"][f"{asr}|u{u}|{split}"]["CER"]


def tests_c3(num: dict) -> None:
    for tid, kind, arms, sign in c3.TESTS:
        prim = c3.evaluate(kind, arms, "test_seen", c3.PRIMARY)
        sec = c3.evaluate(kind, arms, "test_seen", c3.SECONDARY)
        unw = c3.evaluate(kind, arms, "test_unseen", c3.PRIMARY)
        unv = c3.evaluate(kind, arms, "test_unseen", c3.SECONDARY)
        d, lo, hi, half, two_sd = prim
        num[f"c3.{tid}"] = {"d": d, "lo": lo, "hi": hi, "half": half, "twosd": two_sd, "w2v": sec[0],
                            "unW": unw[0], "unV": unv[0], "verdict": c3.verdict(kind, sign, prim, sec)}


def derived_c3(num: dict) -> None:
    """C3 whole encoding path (BN-G-matched - BN-G-iv-vm-asp), for comparison with C1 H3-path. Derived from the C3
    runs with the same G6 machinery, but NOT one of the 13 frozen C3 tests: label it as derived in the paper."""
    arms = ("BN-G-matched", "BN-G-iv-vm-asp")
    prim = c3.evaluate("diff", arms, "test_seen", c3.PRIMARY)
    sec = c3.evaluate("diff", arms, "test_seen", c3.SECONDARY)
    d, lo, hi, half, two_sd = prim
    num["c3d.H3-path"] = {"d": d, "lo": lo, "hi": hi, "half": half, "twosd": two_sd, "w2v": sec[0],
                          "unW": c3.evaluate("diff", arms, "test_unseen", c3.PRIMARY)[0],
                          "unV": c3.evaluate("diff", arms, "test_unseen", c3.SECONDARY)[0],
                          "verdict": c3.verdict("diff", +1, prim, sec)}


def tests_c1(num: dict) -> None:
    for tid, kind, arms, sign, sub in c1.TESTS:
        other = "all" if sub == "covered" else "covered"
        prim = c1.evaluate(kind, arms, "test_seen", c1.PRIMARY, sub)
        sec = c1.evaluate(kind, arms, "test_seen", c1.SECONDARY, sub)
        alt = c1.evaluate(kind, arms, "test_seen", c1.PRIMARY, other)
        unw = c1.evaluate(kind, arms, "test_unseen", c1.PRIMARY, "all")
        unv = c1.evaluate(kind, arms, "test_unseen", c1.SECONDARY, "all")
        d, lo, hi, half, two_sd = prim
        num[f"c1.{tid}"] = {"d": d, "lo": lo, "hi": hi, "half": half, "twosd": two_sd, "w2v": sec[0], "alt": alt[0],
                            "unW": unw[0], "unV": unv[0], "sub": sub, "verdict": c1.verdict(sign, prim, sec)}


def arms_c3(num: dict) -> None:
    arms = list(c3.ORIG) + [f"{a}-elr{m}" for m in (3, 10, 30) for a in c3.FRESH]
    for a in arms:
        rd = c3.run_dirs(a)
        e = {"seeds": len(rd), "fixed": {}}
        for k, asr in ASRS.items():
            for sp in SPLITS:
                _, per, sd = c3.stats(a, sp, asr)
                e[f"{sp}.{k}"] = {"mean": statistics.mean(per), "sd": sd, "per_seed": per}
        for u in (0, 500, 1000, 2000, 3000):
            e["fixed"][u] = statistics.mean(summary_cer(r, u, "fixed_v1", c3.PRIMARY) for r in rd)
        num[f"c3arm.{a}"] = e


def arms_c1(num: dict) -> None:
    for a in c1.ARMS:
        rd = c1.run_dirs(a)
        e = {"seeds": len(rd), "fixed": {}}
        for k, asr in ASRS.items():
            for sp in SPLITS:
                for sub in ("all", "covered"):
                    _, per, sd = c1.stats(a, sp, asr, sub)
                    e[f"{sp}.{k}.{sub}"] = {"mean": statistics.mean(per), "sd": sd, "per_seed": per}
        for u in (0, 500, 1000, 2000, 3000):
            e["fixed"][u] = statistics.mean(summary_cer(r, u, "fixed_v1", c1.PRIMARY) for r in rd)
        num[f"c1arm.{a}"] = e


def long_training(num: dict) -> None:
    runs = {a: ROOT / f"runs/pilot_x1/{a}__train_full__s666" for a in x1.ARMS}
    v6 = {a: [ROOT / f"runs/pilot_v6/{a}__train_full__s{s}" for s in (666, 1234)] for a in x1.ARMS}
    us = (0, 1000, 3000, 6000, 10000, 15000)
    e = {}
    for a in x1.ARMS:
        e[a] = {"fixed": {u: x1.cer(runs[a], u, "fixed_v1") for u in us},
                "fixed_ck": {u: x1.c_to_k(x1.rows(runs[a], u, "fixed_v1"))[0] for u in us}}
        for sp in SPLITS:
            e[a][f"{sp}.15k"] = x1.cer(runs[a], 15000, sp)
            e[a][f"{sp}.3k"] = [x1.cer(r, 3000, sp) for r in v6[a]]
            e[a][f"{sp}.ck15k"] = x1.c_to_k(x1.rows(runs[a], 15000, sp))[0]
            e[a][f"{sp}.ck3k"] = [x1.c_to_k(x1.rows(r, 3000, sp))[0] for r in v6[a]]
    for sp in SPLITS:
        for tag, rs, u in (("15k", runs, 15000), ("3k", {a: v6[a][0] for a in x1.ARMS}, 3000)):
            d, (lo, hi) = paired_diff(per_utt(rs["LAT-G-det"], u, sp, c3.PRIMARY), per_utt(rs["LAT-P"], u, sp, c3.PRIMARY))
            e[f"gap.{sp}.{tag}"] = {"d": d, "lo": lo, "hi": hi}
    num["x1"] = e


def c_to_k_rates(num: dict) -> None:
    """Share of reference words containing চ whose ক-substituted form appears in the hypothesis (D-063)."""
    e = {}
    for corpus, mod in (("slr37", c3), ("rasa", c1)):
        for a in ("LAT-P", "LAT-G-asp", "LAT-G-det", "BN-G-iv-vm-asp"):
            rs = [r for d in mod.run_dirs(a) for r in x1.rows(d, 3000, "test_seen")]
            e[f"{corpus}.{a}"] = x1.c_to_k(rs)[0]
    num["ck"] = e


def baseline_and_curves(num: dict) -> None:
    """Native-script baseline (BN-G, official N(0,1) init of new rows; pilot_v1_1) and the fixed-budget data-size
    curves (D-042: pilot_v6 at 0.25 h / 0.5 h / full; 1 h from pilot_v1_1 or pilot_v4), seeds 666 + 1234."""
    one_h = {"BN-G": "pilot_v1_1", "LAT-G-det": "pilot_v1_1", "LAT-P": "pilot_v1_1", "BN-G-iv-vm-asp": "pilot_v4"}
    e = {}
    for a, v in one_h.items():
        for sub in ("train_0.25h", "train_0.5h", "train_1h", "train_full"):
            ver = v if sub == "train_1h" else "pilot_v6"
            rd = [ROOT / "runs" / ver / f"{a}__{sub}__s{s}" for s in (666, 1234)]
            for k, asr in ASRS.items():
                for sp in SPLITS:
                    per = [summary_cer(r, 3000, sp, asr) for r in rd]
                    e[f"{a}.{sub}.{sp}.{k}"] = {"mean": statistics.mean(per), "sd": statistics.stdev(per), "per_seed": per}
        rd = [ROOT / "runs" / v / f"{a}__train_1h__s{s}" for s in (666, 1234)]
        e[f"{a}.fixed"] = {u: statistics.mean(summary_cer(r, u, "fixed_v1", c3.PRIMARY) for r in rd)
                           for u in (0, 500, 1000, 2000, 3000)}
    num["curves"] = e


def vocab(num: dict) -> None:
    """Per-arm vocabulary facts on SLR37 (configs/vocab/<rep>_v1.json, built over the SLR37 splits)."""
    e = {}
    for rep in ("BN-G", "BN-G-iv", "BN-G-iv-vm", "BN-G-iv-vm-asp", "LAT-G-det", "LAT-G-asp", "LAT-P", "LAT-P-rand"):
        m = json.loads((ROOT / f"configs/vocab/{rep}_v1.json").read_text(encoding="utf-8"))
        sp = m["splits"]["train_full"]
        e[rep] = {"new": m["n_new_embeddings"], "used": m["symbols_used"], "used_base": m["symbols_used_from_base"],
                  "tok_per_utt": sp["tokens"] / sp["utterances"]}
    num["vocab"] = e


def floors(num: dict) -> None:
    out = {}
    for tag, path in (("slr37", "docs/reports/asr_floor_v1.md"), ("rasa", "docs/reports/asr_floor_rasa_v1.md")):
        for line in (ROOT / path).read_text(encoding="utf-8").splitlines():
            m = re.match(r"\| (\S+) \| (test_seen|test_unseen) \| \d+ \| ([\d.]+) ", line)
            if m:
                out[f"{tag}.{'W' if 'whisper' in m[1] else 'V'}.{m[2]}"] = float(m[3])
    num["floor"] = out


def sensitivity(num: dict) -> None:
    """Post hoc sensitivity statistics (D-070), produced by tools/sensitivity_stats.py."""
    num["sens"] = json.loads((OUT / "sensitivity.json").read_text(encoding="utf-8"))


def controls_c5(num: dict) -> None:
    """Frozen C5 controls (D-072, D-073), parsed from the report written by tools/analyze_c5.py."""
    t, spread, der = {}, {}, {}
    for line in (ROOT / "docs/reports/c5_controls.md").read_text(encoding="utf-8").splitlines():
        m = re.match(r"\| (C5[ab]-[\w-]+) \| ([+-]?[\d.]+) \[([+-]?[\d.]+), ([+-]?[\d.]+)\] \| ([\d.]+) \| ([\d.]+) \| "
                     r"([+-]?[\d.]+) \| (\w+) \|", line)
        if m:
            t[m[1]] = dict(zip(("d", "lo", "hi", "half", "twosd", "w2v"), map(float, m.groups()[1:7])), verdict=m[8])
            continue
        m = re.match(r"\| ([\w-]+) \| ([\d.]+) / ([\d.]+) / ([\d.]+) \| ([\d.]+) \| ([\d.]+) / ([\d.]+) / ([\d.]+) \| "
                     r"([\d.]+) \|", line)
        if m:
            v = list(map(float, m.groups()[1:]))
            spread[m[1]] = {"init": v[0:3], "init_sd": v[3], "train": v[4:7], "train_sd": v[7]}
            continue
        m = re.match(r"- (LAT-P-rand\d?): ([\d.]+) / ([\d.]+)", line)
        if m:
            der[m[1]] = [float(m[2]), float(m[3])]
    assert len(t) == 6 and len(spread) == 3 and len(der) == 3, (len(t), len(spread), len(der))
    num["c5"] = {"tests": t, "spread": spread, "der": der}


def check(num: dict) -> list[str]:
    bad = []
    for prefix, path in (("c3", "docs/reports/c3_hypothesis_tests.md"), ("c1", "docs/reports/c1_replication_tests.md")):
        for line in (ROOT / path).read_text(encoding="utf-8").splitlines():
            m = re.match(r"\| (H[\w-]+) \|.*?\| ([+-]?[\d.]+) \[([+-]?[\d.]+), ([+-]?[\d.]+)\]", line)
            if not m:
                continue
            got = num[f"{prefix}.{m[1]}"]
            for key, ref in zip(("d", "lo", "hi"), map(float, m.groups()[1:])):
                if abs(got[key] - ref) > TOL:
                    bad.append(f"{prefix}.{m[1]}.{key}: report {ref} vs recomputed {got[key]:.3f}")
    return bad


def tex(num: dict) -> str:
    L = ["% Generated by tools/paper_numbers.py. Do not edit by hand.", "\\makeatletter",
         "\\newcommand{\\V}[1]{\\@ifundefined{V@#1}{\\textbf{??#1??}}{\\@nameuse{V@#1}}}"]

    def put(k, v):
        L.append(f"\\@namedef{{V@{k}}}{{{v}}}")

    for k, t in num.items():
        if k.startswith(("c3.", "c1.", "c3d.")):
            for f in ("d", "lo", "hi", "w2v", "unW", "unV", "alt"):
                if f in t:
                    put(f"{k}.{f}", fmt(t[f], signed=True))
            put(f"{k}.half", fmt(t["half"]))
            put(f"{k}.twosd", fmt(t["twosd"]))
            put(f"{k}.verdict", t["verdict"])
        elif k.startswith(("c3arm.", "c1arm.")):
            for f, v in t.items():
                if isinstance(v, dict) and "mean" in v:
                    put(f"{k}.{f}", fmt(v["mean"]))
                    put(f"{k}.{f}.sd", fmt(v["sd"]))
            for u, v in t["fixed"].items():
                put(f"{k}.fixed.u{u}", fmt(v))
    for a, v in num["x1"].items():
        if a.startswith("gap."):
            for f in ("d", "lo", "hi"):
                put(f"x1.{a}.{f}", fmt(v[f], signed=True))
            continue
        for u, c in v["fixed"].items():
            put(f"x1.{a}.fixed.u{u}", fmt(c))
        for u, c in v["fixed_ck"].items():
            put(f"x1.{a}.fixedck.u{u}", f"{c:.1f}")
        for sp in SPLITS:
            put(f"x1.{a}.{sp}.15k", fmt(v[f"{sp}.15k"]))
            put(f"x1.{a}.{sp}.ck15k", f"{v[f'{sp}.ck15k']:.1f}")
            for i, s in enumerate((666, 1234)):
                put(f"x1.{a}.{sp}.3k.s{s}", fmt(v[f"{sp}.3k"][i]))
                put(f"x1.{a}.{sp}.ck3k.s{s}", f"{v[f'{sp}.ck3k'][i]:.1f}")
    for k, v in num["ck"].items():
        put(f"ck.{k}", f"{v:.1f}")
    for k, v in num["curves"].items():
        if k.endswith(".fixed"):
            for u, c in v.items():
                put(f"curves.{k}.u{u}", fmt(c))
        else:
            put(f"curves.{k}", fmt(v["mean"]))
            put(f"curves.{k}.sd", fmt(v["sd"]))
    for rep, v in num["vocab"].items():
        put(f"vocab.{rep}.new", str(v["new"]))
        put(f"vocab.{rep}.used", str(v["used"]))
        put(f"vocab.{rep}.usedbase", str(v["used_base"]))
        put(f"vocab.{rep}.tok", f"{v['tok_per_utt']:.1f}")
    for k, v in num["floor"].items():
        put(f"floor.{k}", fmt(v))
    pv = lambda x: "n/a" if x is None else ("$<$0.001" if x < 0.001 else f"{x:.3f}")  # noqa: E731
    for k, v in num["sens"].items():
        put(f"sens.{k}.d", fmt(v["d"], signed=True))
        put(f"sens.{k}.lo", fmt(v["boot2_lo"], signed=True))
        put(f"sens.{k}.hi", fmt(v["boot2_hi"], signed=True))
        put(f"sens.{k}.p", pv(v["p_boot2"]))
        put(f"sens.{k}.holm", pv(v["p_holm"]))
        put(f"sens.{k}.agree", "n/a" if v["seeds_agree"] is None else f"{v['seeds_agree']}/{min(v['seeds'])}")
        put(f"sens.{k}.rel", "n/a" if v["rel_change_pct"] is None else
            f"{v['rel_change_pct']:+.0f}".replace("-", "$-$").replace("+", "$+$") + "\\%")
        put(f"sens.{k}.dz", fmt(v["dz"], signed=True))
    for k, v in num["c5"]["tests"].items():
        for f in ("d", "lo", "hi", "w2v"):
            put(f"c5.{k}.{f}", fmt(v[f], signed=True))
        put(f"c5.{k}.half", fmt(v["half"]))
        put(f"c5.{k}.twosd", fmt(v["twosd"]))
        put(f"c5.{k}.verdict", v["verdict"])
    for a, v in num["c5"]["spread"].items():
        for i, s in enumerate((666, 1001, 1002)):
            put(f"c5.{a}.init{s}", fmt(v["init"][i]))
        for i, s in enumerate((666, 1234, 4242)):
            put(f"c5.{a}.train{s}", fmt(v["train"][i]))
        put(f"c5.{a}.initsd", fmt(v["init_sd"]))
        put(f"c5.{a}.trainsd", fmt(v["train_sd"]))
        put(f"c5.{a}.ratio", f"{v['init_sd'] / v['train_sd']:.0f}")
        put(f"c5.{a}.twoinitsd", fmt(2 * v["init_sd"]))
    for a, v in num["c5"]["der"].items():
        for i, s in enumerate((666, 1234)):
            put(f"c5.{a}.s{s}", fmt(v[i]))
    L.append("\\makeatother")
    return "\n".join(L) + "\n"


def main() -> int:
    num: dict = {}
    for f in (tests_c3, derived_c3, tests_c1, arms_c3, arms_c1, long_training, c_to_k_rates, baseline_and_curves, vocab,
              floors, sensitivity, controls_c5):
        f(num)
    bad = check(num)
    if bad:
        print("MISMATCH vs frozen reports:\n  " + "\n  ".join(bad))
        return 1
    OUT.mkdir(exist_ok=True)
    (OUT / "numbers.json").write_text(json.dumps(num, indent=1, ensure_ascii=False), encoding="utf-8")
    body = tex(num)
    (OUT / "numbers.tex").write_text(body, encoding="utf-8")
    n = sum(1 for line in body.splitlines() if line.startswith("\\@namedef"))
    print(f"ok: {n} macros; hypothesis-test numbers match the frozen reports (tol {TOL})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
