"""Paper figures from paper/numbers.json (run tools/paper_numbers.py first). Static PDFs for LaTeX.

Colour = embedding-row condition, fixed across figures (validated palette, slots 1-3 pass all-pairs CVD):
pretrained rows = blue, fresh (matched-init) rows = orange, scrambled relabeling = aqua. The Bengali-codepoint
encoding path is an ordinal one-hue ramp (validated --ordinal). Every series also has a marker/linestyle and a
direct label, so identity never depends on colour alone (aqua is below 3:1 contrast on white).
    python tools/paper_figs.py
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
NUM = json.loads((ROOT / "paper/numbers.json").read_text(encoding="utf-8"))
OUT = ROOT / "paper/figs"
PRE, FRESH, SCR = "#2a78d6", "#eb6834", "#1baf7a"
RAMP = ["#86b6ef", "#3987e5", "#1c5cab", "#0d366b"]  # BN-G-matched -> BN-G-iv -> -iv-vm -> -iv-vm-asp
INK, INK2, MUTED, GRID, AXIS = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 8, "axes.titlesize": 8.5, "axes.labelsize": 8,
    "axes.edgecolor": AXIS, "axes.labelcolor": INK2, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.axisbelow": True,
    "axes.spines.top": False, "axes.spines.right": False, "lines.linewidth": 1.6, "lines.markersize": 4.5,
    "legend.frameon": False, "legend.fontsize": 7.5, "pdf.fonttype": 42, "savefig.bbox": "tight",
})


def fixed_curve(key: str) -> tuple[list[int], list[float]]:
    f = NUM[key]["fixed"]
    us = sorted(int(u) for u in f)
    return us, [f[str(u)] for u in us]


def label_end(ax, x, y, text, dy=0.0):
    ax.annotate(text, (x, y), xytext=(4, dy), textcoords="offset points", va="center", fontsize=6.5, color=INK2)


def floor(ax, value, text="ASR floor (real audio)"):
    ax.axhline(value, color=MUTED, lw=0.9, ls=(0, (2, 2)))
    ax.annotate(text, (ax.get_xlim()[0], value), xytext=(2, 3), textcoords="offset points", fontsize=6.5, color=MUTED)


def fig_curves():
    """Fixed-set CER over training (SLR37, mean of 3 seeds): reuse controls | grapheme Latin | encoding path."""
    panels = [
        ("(a) Phonemic Latin (LAT-P text)", [("LAT-P", "pretrained rows", PRE, "o", "-"),
                                             ("LAT-P-reinit", "fresh rows", FRESH, "s", "-"),
                                             ("LAT-P-rand", "scrambled", SCR, "^", "-")]),
        ("(b) Grapheme Latin", [("LAT-G-det", "ITRANS, pretrained", PRE, "o", "-"),
                                ("LAT-G-det-reinit", "ITRANS, fresh", FRESH, "s", "-"),
                                ("LAT-G-asp", "LAT-G-asp", PRE, "D", "--")]),
        ("(c) Bengali codepoints, fresh rows", [("BN-G-matched", "BN-G", RAMP[0], "o", "-"),
                                                 ("BN-G-iv", "+ inh. vowel", RAMP[1], "s", "-"),
                                                 ("BN-G-iv-vm", "+ vowel merge", RAMP[2], "^", "-"),
                                                 ("BN-G-iv-vm-asp", "+ aspirates", RAMP[3], "D", "-")]),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(7.0, 2.6), sharey=True)
    for ax, (title, series) in zip(axes, panels):
        ax.set_title(title, loc="left", color=INK)
        ends = []
        for arm, lab, col, mk, ls in series:
            us, ys = fixed_curve(f"c3arm.{arm}")
            ax.plot(us, ys, color=col, marker=mk, ls=ls, markeredgecolor="white", markeredgewidth=0.6)
            ends.append((ys[-1], lab))
        ax.set_xlim(-150, 5200)
        ax.set_xticks([0, 1000, 2000, 3000])
        ax.set_xlabel("update")
        last = -99.0
        for y, lab in sorted(ends):  # direct labels at the line ends, nudged apart
            y_txt = max(y, last + 7)
            ax.annotate(lab, (3000, y), xytext=(3120, y_txt), textcoords="data", fontsize=6.3, color=INK2, va="center")
            last = y_txt
        floor(ax, NUM["floor"]["slr37.W.test_seen"], "ASR floor")
    axes[0].set_ylabel("CER % (Whisper, fixed set)")
    axes[0].set_ylim(0, 125)
    axes[0].set_yticks([0, 25, 50, 75, 100, 125])
    fig.tight_layout(w_pad=0.6)
    fig.savefig(OUT / "curves.pdf")
    plt.close(fig)


def fig_tests():
    """Forest plot: Delta CER [95 % CI] per hypothesis, SLR37 (C3) vs Rasa (C1)."""
    rows = [("H1a reuse, phonemic\nLAT-P − LAT-P-reinit", "c3.H1a", "c1.H1a"),
            ("H1b reuse, ITRANS\nLAT-G-det − LAT-G-det-reinit", "c3.H1b", "c1.H1b"),
            ("H2 interference\nLAT-P-rand − LAT-P-reinit", "c3.H2", "c1.H2"),
            ("H3 encoding path\nBN-G − BN-G-iv-vm-asp", "c3d.H3-path", "c1.H3-path"),
            ("H4 interaction\n(BN-G-iv-vm-asp − LAT-G-asp)\n− (LAT-G-det-reinit − LAT-G-det)", "c3.H4", "c1.H4")]
    fig, ax = plt.subplots(figsize=(5.8, 3.1))
    for i, (_, k3, k1) in enumerate(rows):
        y = len(rows) - 1 - i
        for key, off, col, mk, name in ((k3, 0.15, PRE, "o", "SLR37, bn-BD (C3)"), (k1, -0.15, FRESH, "s", "Rasa, bn-IN (C1)")):
            t = NUM[key]
            hollow = key.startswith("c3d.")
            ax.errorbar(t["d"], y + off, xerr=[[t["d"] - t["lo"]], [t["hi"] - t["d"]]], fmt=mk, color=col, ms=5,
                        mfc="white" if hollow else col, capsize=2, lw=1.2, label=name if i == 0 else None)
            ax.annotate(f"{t['d']:+.1f}", (t["hi"], y + off), xytext=(4, 0), textcoords="offset points",
                        va="center", fontsize=6.5, color=INK2)
    ax.axvline(0, color=AXIS, lw=1)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([r[0] for r in rows][::-1], fontsize=6.8, color=INK2)
    ax.set_xlabel("Δ CER, percentage points (Whisper, test_seen, mean of 3 seeds)")
    ax.set_xlim(-55, 62)
    ax.grid(axis="y", visible=False)
    ax.legend(loc="upper center", fontsize=7)
    fig.savefig(OUT / "tests.pdf")
    plt.close(fig)


def fig_lr():
    """test_seen CER vs embedding-LR multiplier for the three fresh-row arms (SLR37)."""
    mults = [1, 3, 10, 30]
    series = [("BN-G-matched", "BN-G", RAMP[0], "o", 0), ("BN-G-iv-vm-asp", "BN-G-iv-vm-asp", RAMP[3], "D", -4),
              ("LAT-P-reinit", "LAT-P-reinit", FRESH, "s", 4)]
    fig, ax = plt.subplots(figsize=(3.4, 2.5))
    for arm, lab, col, mk, dy in series:
        ys = [NUM[f"c3arm.{arm}" + ("" if m == 1 else f"-elr{m}")]["test_seen.W"]["mean"] for m in mults]
        ax.plot(mults, ys, color=col, marker=mk, markeredgecolor="white", markeredgewidth=0.6)
        label_end(ax, 30, ys[-1], lab, dy=dy)
    lp = NUM["c3arm.LAT-P"]["test_seen.W"]["mean"]
    ax.axhline(lp, color=PRE, lw=1.2, ls="--")
    ax.annotate("LAT-P, pretrained rows (1×)", (1, lp), xytext=(2, 3), textcoords="offset points", fontsize=6.5, color=INK2)
    ax.set_xscale("log")
    ax.set_xticks(mults)
    ax.set_xticklabels([f"{m}×" for m in mults])
    ax.minorticks_off()
    ax.set_xlim(0.85, 130)
    ax.set_ylim(0, 75)
    ax.set_xlabel("embedding-table LR multiplier (fresh-row arms)")
    ax.set_ylabel("CER % (Whisper, test_seen)")
    fig.savefig(OUT / "lr.pdf")
    plt.close(fig)


def fig_long():
    """Long training (exploratory, 1 seed): fixed-set CER and the চ→ক confusion over 15k updates."""
    fig, (a, b) = plt.subplots(1, 2, figsize=(6.4, 2.4))
    for arm, lab, mk, col in (("LAT-G-det", "ITRANS (LAT-G-det)", "s", FRESH), ("LAT-P", "LAT-P", "o", PRE)):
        f, ck = NUM["x1"][arm]["fixed"], NUM["x1"][arm]["fixed_ck"]
        us = sorted(int(u) for u in f)
        a.plot(us, [f[str(u)] for u in us], color=col, marker=mk, label=lab, markeredgecolor="white", markeredgewidth=0.6)
        b.plot(us, [ck[str(u)] for u in us], color=col, marker=mk, label=lab, markeredgecolor="white", markeredgewidth=0.6)
    a.set_ylim(0, 70)
    a.set_title("(a) CER on the fixed set", loc="left", color=INK)
    b.set_ylim(-1, 20)
    b.set_title("(b) words with চ transcribed with ক (%)", loc="left", color=INK, fontfamily=["Nirmala UI", "DejaVu Sans"])
    for ax in (a, b):
        ax.set_xlim(-400, 15600)
        ax.axvline(3000, color=AXIS, lw=0.9)
        ax.annotate("usual budget", (3000, ax.get_ylim()[1]), xytext=(3, -8), textcoords="offset points",
                    fontsize=6.5, color=MUTED)
        ax.set_xlabel("update")
        ax.set_xticks([0, 3000, 6000, 10000, 15000])
        ax.set_xticklabels(["0", "3k", "6k", "10k", "15k"])
    floor(a, NUM["floor"]["slr37.W.test_seen"], "ASR floor")
    a.set_ylabel("CER % (Whisper)")
    h, lab = b.get_legend_handles_labels()
    b.legend(h[::-1], lab[::-1], loc="upper right")
    fig.tight_layout(w_pad=1.2)
    fig.savefig(OUT / "long.pdf")
    plt.close(fig)


def fig_size():
    """Fixed-budget data-size curves (D-042), test_seen CER, mean of 2 seeds with min-max bars."""
    hours = {"train_0.25h": 0.252, "train_0.5h": 0.500, "train_1h": 1.000, "train_full": 1.577}
    series = [("BN-G", "BN-G, N(0,1) rows", RAMP[0], "o", 0), ("BN-G-iv-vm-asp", "BN-G-iv-vm-asp, fresh", RAMP[3], "D", 0),
              ("LAT-G-det", "ITRANS, pretrained", FRESH, "s", 4), ("LAT-P", "LAT-P, pretrained", PRE, "^", -4)]
    fig, ax = plt.subplots(figsize=(3.4, 2.5))
    for arm, lab, col, mk, dy in series:
        xs, ys, lo, hi = [], [], [], []
        for sub, h in hours.items():
            e = NUM["curves"][f"{arm}.{sub}.test_seen.W"]
            xs.append(h)
            ys.append(e["mean"])
            lo.append(e["mean"] - min(e["per_seed"]))
            hi.append(max(e["per_seed"]) - e["mean"])
        ax.errorbar(xs, ys, yerr=[lo, hi], color=col, marker=mk, capsize=2, markeredgecolor="white", markeredgewidth=0.6)
        label_end(ax, xs[-1], ys[-1], lab, dy=dy)
    ax.set_xscale("log")
    ax.set_xticks(list(hours.values()))
    ax.set_xticklabels(["0.25", "0.5", "1", "1.58"])
    ax.minorticks_off()
    ax.set_xlim(0.2, 8)
    ax.set_ylim(0, 80)
    ax.set_xlabel("training speech (h), 3,000 updates each")
    ax.set_ylabel("CER % (Whisper, test_seen)")
    fig.savefig(OUT / "size.pdf")
    plt.close(fig)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for f in (fig_curves, fig_tests, fig_lr, fig_long, fig_size):
        f()
    print("figures:", sorted(p.name for p in OUT.glob("*.pdf")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
