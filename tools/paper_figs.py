"""Paper figures from paper/numbers.json (run tools/paper_numbers.py first). Static PDFs for LaTeX.

Every figure is drawn at its final printed size (full text width = 6.5 in), so the 8 pt text is printed at 8 pt.
Colour = embedding-row condition, fixed across figures (validated palette, slots 1-3 pass all-pairs CVD):
pretrained rows = blue, fresh (matched-init) rows = orange, scrambled relabeling = aqua. The Bengali-codepoint
encoding path is an ordinal one-hue ramp (validated --ordinal). Every series also has its own marker and a legend
or direct label, so identity never depends on colour alone (aqua is below 3:1 contrast on white).
    python tools/paper_figs.py
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
NUM = json.loads((ROOT / "paper/numbers.json").read_text(encoding="utf-8"))
OUT = ROOT / "paper/figs"
W = 6.5  # text width, inches
PRE, FRESH, SCR = "#2a78d6", "#eb6834", "#1baf7a"
RAMP = ["#86b6ef", "#3987e5", "#1c5cab", "#0d366b"]  # BN-G -> +iv -> +vm -> +asp
SEQ = ["#e8f1fc", "#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#1c5cab", "#0d366b"]  # CER: light = low, dark = high
INK, INK2, MUTED, GRID, AXIS = "#0b0b0b", "#52514e", "#898781", "#e6e5df", "#b9b8ae"

plt.rcParams.update({
    "font.family": ["Arial", "DejaVu Sans"], "font.size": 8, "axes.titlesize": 8.5, "axes.titleweight": "bold",
    "axes.labelsize": 8, "xtick.labelsize": 7.5, "ytick.labelsize": 7.5, "legend.fontsize": 7.5,
    "axes.edgecolor": AXIS, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.axisbelow": True,
    "axes.spines.top": False, "axes.spines.right": False, "lines.linewidth": 1.5, "lines.markersize": 4.5,
    "legend.frameon": False, "legend.handlelength": 1.6, "pdf.fonttype": 42,
    "savefig.bbox": "tight", "savefig.pad_inches": 0.02, "axes.titlelocation": "left", "axes.titlepad": 6,
})


def arm(a: str, split: str = "test_seen.W") -> float:
    return NUM[f"c3arm.{a}"][split]["mean"]


def fixed_curve(key: str) -> tuple[list[int], list[float]]:
    f = NUM[key]["fixed"]
    us = sorted(int(u) for u in f)
    return us, [f[str(u)] for u in us]


def floor(ax, value, text="ASR floor"):
    ax.axhline(value, color=MUTED, lw=0.8, ls=(0, (3, 2)), zorder=1)
    ax.annotate(text, (0, value), xycoords=("axes fraction", "data"), xytext=(3, 2.5), textcoords="offset points",
                ha="left", va="bottom", fontsize=7, color=MUTED)


def mk(**kw):
    return {"markeredgecolor": "white", "markeredgewidth": 0.6, **kw}


# --------------------------------------------------------------------------------------------- 1. design + outcomes
def fig_design():
    """The arms as a grid: columns = text encoding, rows = embedding rows; each cell shows its SLR37 CER."""
    fig, ax = plt.subplots(figsize=(W, 2.45))
    ax.set_xlim(-1.45, 10.05)
    ax.set_ylim(-0.62, 3.2)
    ax.axis("off")
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    bw, bh, gap = 1.12, 0.6, 1.27
    order = ["BN-G", "BN-G-iv", "BN-G-iv-vm", "BN-G-iv-vm-asp", "LAT-G-asp", "LAT-G-det", "LAT-P", "LAT-P-rand"]
    cols = {a: i * gap + (0.45 if i >= 4 else 0) for i, a in enumerate(order)}
    y_pre, y_fresh = 1.75, 0.5

    def shade(cer):
        return SEQ[min(len(SEQ) - 1, int(cer / 90 * (len(SEQ) - 1) + 0.5))]

    def box(x, y, w=bw, dashed=False, fc="white"):
        ax.add_patch(FancyBboxPatch((x - w / 2, y - bh / 2), w, bh, boxstyle="round,pad=0.0,rounding_size=0.06",
                                    fc=fc, ec=AXIS if dashed else "none", lw=0.8, ls=(0, (3, 2))))

    def cell(a, y, cer):
        fc = shade(cer)
        box(cols[a], y, fc=fc)
        ax.text(cols[a], y, f"{cer:.1f}", ha="center", va="center", fontsize=9, fontweight="bold",
                color="white" if SEQ.index(fc) >= 4 else INK)

    heads = {"BN-G": "canonical", "BN-G-iv": "+ inherent\nvowel", "BN-G-iv-vm": "+ vowel\nmerge",
             "BN-G-iv-vm-asp": "+ aspirate\nsplit", "LAT-G-asp": "1:1 Latin\nrelabel", "LAT-G-det": "ITRANS",
             "LAT-P": "lexicon\nphonemes", "LAT-P-rand": "phonemes,\nscrambled"}
    for a, sub in heads.items():
        ax.text(cols[a], 2.55, a, ha="center", va="bottom", fontsize=6.9, color=INK, fontweight="bold")
        ax.text(cols[a], 2.5, sub, ha="center", va="top", fontsize=6.6, color=INK2, linespacing=1.05)
    for lo, hi, text in (("BN-G", "BN-G-iv-vm-asp", "Bengali codepoints  (cumulative encoding path →)"),
                         ("LAT-G-asp", "LAT-P-rand", "Latin characters F5 already knows")):
        x0, x1 = cols[lo] - bw / 2, cols[hi] + bw / 2
        ax.plot([x0, x1], [2.98, 2.98], color=AXIS, lw=0.8)
        ax.text((x0 + x1) / 2, 3.03, text, ha="center", va="bottom", fontsize=7.5, color=INK, fontweight="bold")
    ax.text(-0.75, y_pre, "pretrained\nrows", ha="right", va="center", fontsize=7.5, color=PRE, fontweight="bold")
    ax.text(-0.75, y_fresh, "fresh rows", ha="right", va="center", fontsize=7.5, color=FRESH, fontweight="bold")
    span = cols["BN-G-iv-vm-asp"] - cols["BN-G"] + bw
    box((cols["BN-G"] + cols["BN-G-iv-vm-asp"]) / 2, y_pre, w=span, dashed=True)
    ax.text((cols["BN-G"] + cols["BN-G-iv-vm-asp"]) / 2, y_pre, "no pretrained rows exist for Bengali symbols",
            ha="center", va="center", fontsize=7, color=MUTED)
    for a in ("LAT-G-asp", "LAT-G-det", "LAT-P", "LAT-P-rand"):
        cell(a, y_pre, arm(a))
    for a, src in (("BN-G", "BN-G-matched"), ("BN-G-iv", "BN-G-iv"), ("BN-G-iv-vm", "BN-G-iv-vm"),
                   ("BN-G-iv-vm-asp", "BN-G-iv-vm-asp"), ("LAT-G-det", "LAT-G-det-reinit"), ("LAT-P", "LAT-P-reinit")):
        cell(a, y_fresh, arm(src))
    box(cols["LAT-G-asp"], y_fresh, dashed=True)
    ax.text(cols["LAT-G-asp"], y_fresh, "n/a", ha="center", va="center", fontsize=7, color=MUTED,
            linespacing=1.1)
    box(cols["LAT-P-rand"], y_fresh, dashed=True)
    ax.text(cols["LAT-P-rand"], y_fresh, "n/a", ha="center", va="center", fontsize=7, color=MUTED,
            linespacing=1.1)

    def arrow(p, q):
        ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=7, lw=0.9, color=INK2, shrinkA=0,
                                     shrinkB=0, zorder=5))

    d = lambda k: NUM[k]["d"]  # noqa: E731
    fmt = lambda v: f"{v:+.1f}".replace("-", "−")  # noqa: E731
    for a, b, k in (("BN-G", "BN-G-iv", "c3.H3a"), ("BN-G-iv", "BN-G-iv-vm", "c3.H3b"),
                    ("BN-G-iv-vm", "BN-G-iv-vm-asp", "c3.H3c")):
        arrow((cols[a] + bw / 2 + 0.02, y_fresh), (cols[b] - bw / 2 - 0.02, y_fresh))
        ax.text((cols[a] + cols[b]) / 2, y_fresh - bh / 2 - 0.08, f"{k[3:]} {fmt(-d(k))}", ha="center", va="top",
                fontsize=6.6, color=INK)
    for c, k, lab in (("LAT-G-det", "c3.H1b", "H1b"), ("LAT-P", "c3.H1a", "H1a")):
        arrow((cols[c], y_fresh + bh / 2 + 0.02), (cols[c], y_pre - bh / 2 - 0.02))
        ax.text(cols[c] - 0.06, (y_pre + y_fresh) / 2, f"{lab} {fmt(d(k))}", ha="right", va="center", fontsize=6.6,
                color=INK)
    arrow((cols["LAT-P"] + bw / 2 + 0.02, y_fresh + 0.08), (cols["LAT-P-rand"] - bw / 2 + 0.05, y_pre - bh / 2 - 0.02))
    ax.text(cols["LAT-P-rand"] + 0.06, (y_pre + y_fresh) / 2 + 0.02, f"H2 {fmt(d('c3.H2'))}", ha="left",
            va="center", fontsize=6.6, color=INK)
    ax.text(cols["LAT-P-rand"] + bw / 2, -0.55, "cells: CER %, SLR37 test_seen (Whisper, mean of 3 seeds); "
            "darker = higher error.  Arrows: change in CER, pp", ha="right", va="center", fontsize=6.5, color=MUTED)
    fig.savefig(OUT / "design.pdf")
    plt.close(fig)


# ------------------------------------------------------------------------------------------------ 2. training curves
def fig_curves():
    panels = [
        ("(a) Phonemic Latin text", [("LAT-P", "pretrained rows", PRE, "o"), ("LAT-P-reinit", "fresh rows", FRESH, "s"),
                                     ("LAT-P-rand", "scrambled relabel", SCR, "^")]),
        ("(b) Grapheme Latin text", [("LAT-G-det", "ITRANS, pretrained", PRE, "o"),
                                     ("LAT-G-asp", "LAT-G-asp, pretrained", PRE, "D"),
                                     ("LAT-G-det-reinit", "ITRANS, fresh", FRESH, "s")]),
        ("(c) Bengali codepoints, fresh rows", [("BN-G-matched", "BN-G", RAMP[0], "o"),
                                                ("BN-G-iv", "+ inherent vowel", RAMP[1], "s"),
                                                ("BN-G-iv-vm", "+ vowel merge", RAMP[2], "^"),
                                                ("BN-G-iv-vm-asp", "+ aspirate split", RAMP[3], "D")]),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(W, 2.3), sharey=True)
    for ax, (title, series) in zip(axes, panels):
        ax.set_title(title, color=INK)
        for a, lab, col, m in series:
            us, ys = fixed_curve(f"c3arm.{a}")
            ax.plot(us, ys, color=col, marker=m, ls="--" if a == "LAT-G-asp" else "-", label=lab, **mk())
        ax.set_xticks([0, 1000, 2000, 3000])
        ax.set_xticklabels(["0", "1k", "2k", "3k"])
        ax.set_xlim(-150, 3150)
        ax.set_xlabel("fine-tuning update")
        floor(ax, NUM["floor"]["slr37.W.test_seen"])
        ax.legend(loc="upper right", borderaxespad=0.2, handletextpad=0.5, labelspacing=0.3)
    axes[0].set_ylabel("CER % (fixed set)")
    axes[0].set_ylim(0, 128)
    axes[0].set_yticks([0, 25, 50, 75, 100, 125])
    fig.tight_layout(w_pad=0.8)
    fig.savefig(OUT / "curves.pdf")
    plt.close(fig)


# ----------------------------------------------------------------------------------------------------- 3. the tests
def fig_tests():
    rows = [("H1a  reuse, phonemic", "c3.H1a", "c1.H1a"), ("H1b  reuse, ITRANS", "c3.H1b", "c1.H1b"),
            ("H2  scrambled vs fresh", "c3.H2", "c1.H2"), ("H3  encoding path", "c3d.H3-path", "c1.H3-path"),
            ("H4  interaction", "c3.H4", "c1.H4")]
    fig, ax = plt.subplots(figsize=(W, 2.2))
    for i, (_, k3, k1) in enumerate(rows):
        y = len(rows) - 1 - i
        for key, off, col, m, name in ((k3, 0.16, PRE, "o", "SLR37, bn-BD (C3, robustness)"),
                                       (k1, -0.16, FRESH, "s", "Rasa, bn-IN (C1, replication)")):
            t = NUM[key]
            ax.errorbar(t["d"], y + off, xerr=[[t["d"] - t["lo"]], [t["hi"] - t["d"]]], fmt=m, color=col, ms=4.8,
                        mfc="white" if key.startswith("c3d.") else col, mew=1.1, capsize=2.2, lw=1.1,
                        label=name if i == 0 else None)
            right = t["d"] >= 0
            ax.annotate(f"{t['d']:+.1f}", (t["hi"] if right else t["lo"], y + off), xytext=(4 if right else -4, 0),
                        textcoords="offset points", va="center", ha="left" if right else "right", fontsize=7,
                        color=INK2)
    ax.axvline(0, color=INK2, lw=0.8)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([r[0] for r in rows][::-1], color=INK)
    ax.set_ylim(-0.6, len(rows) - 0.4)
    ax.set_xlim(-45, 62)
    ax.set_xlabel("Δ CER, percentage points (A − B; Whisper test_seen, mean of 3 seeds, 95% CI)")
    ax.grid(axis="y", visible=False)
    ax.tick_params(axis="y", length=0)
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2, handletextpad=0.4, columnspacing=2.0)
    fig.savefig(OUT / "tests.pdf")
    plt.close(fig)


# -------------------------------------------------------------------------------- 4. learning rate and data size
def fig_lr_size():
    fig, (a, b) = plt.subplots(1, 2, figsize=(W, 2.3))
    mults = [1, 3, 10, 30]
    for name, lab, col, m in (("BN-G-matched", "BN-G (fresh)", RAMP[0], "o"),
                              ("LAT-P-reinit", "LAT-P-reinit (fresh)", FRESH, "s"),
                              ("BN-G-iv-vm-asp", "BN-G-iv-vm-asp (fresh)", RAMP[3], "D")):
        ys = [NUM[f"c3arm.{name}" + ("" if x == 1 else f"-elr{x}")]["test_seen.W"]["mean"] for x in mults]
        a.plot(mults, ys, color=col, marker=m, label=lab, **mk())
    a.axhline(arm("LAT-P"), color=PRE, lw=1.2, ls="--", label="LAT-P (pretrained, 1×)")
    a.set_xscale("log")
    a.set_xticks(mults)
    a.set_xticklabels([f"{x}×" for x in mults])
    a.minorticks_off()
    a.set_xlim(0.85, 36)
    a.set_ylim(0, 100)
    a.set_title("(a) Embedding-table learning rate", color=INK)
    a.set_xlabel("multiplier on the base learning rate")
    a.set_ylabel("CER % (test_seen)")
    a.legend(loc="upper right", borderaxespad=0.2, labelspacing=0.3)

    hours = {"train_0.25h": 0.252, "train_0.5h": 0.500, "train_1h": 1.000, "train_full": 1.577}
    for name, lab, col, m in (("BN-G", "BN-G, N(0,1) rows", RAMP[0], "o"),
                              ("BN-G-iv-vm-asp", "BN-G-iv-vm-asp, fresh", RAMP[3], "D"),
                              ("LAT-G-det", "ITRANS, pretrained", FRESH, "s"),
                              ("LAT-P", "LAT-P, pretrained", PRE, "^")):
        es = [NUM["curves"][f"{name}.{s}.test_seen.W"] for s in hours]
        err = [[e["mean"] - min(e["per_seed"]) for e in es], [max(e["per_seed"]) - e["mean"] for e in es]]
        b.errorbar(list(hours.values()), [e["mean"] for e in es], yerr=err, color=col, marker=m, capsize=2,
                   label=lab, **mk())
    b.set_xscale("log")
    b.set_xticks(list(hours.values()))
    b.set_xticklabels(["0.25", "0.5", "1", "1.58"])
    b.minorticks_off()
    b.set_ylim(0, 80)
    b.set_title("(b) Training data at a fixed 3k updates", color=INK)
    b.set_xlabel("training speech (hours)")
    b.legend(loc="center right", borderaxespad=0.2, labelspacing=0.3)
    fig.tight_layout(w_pad=1.5)
    fig.savefig(OUT / "lr_size.pdf")
    plt.close(fig)


# ---------------------------------------------------------------------------------------------- 5. long training
def fig_long():
    fig, (a, b) = plt.subplots(1, 2, figsize=(W, 2.2))
    for name, lab, m, col in (("LAT-G-det", "ITRANS (LAT-G-det)", "s", FRESH), ("LAT-P", "LAT-P", "o", PRE)):
        f, ck = NUM["x1"][name]["fixed"], NUM["x1"][name]["fixed_ck"]
        us = sorted(int(u) for u in f)
        a.plot(us, [f[str(u)] for u in us], color=col, marker=m, label=lab, **mk())
        b.plot(us, [ck[str(u)] for u in us], color=col, marker=m, label=lab, **mk())
    for ax, top in ((a, 82), (b, 20)):
        ax.set_xlim(-400, 15400)
        ax.set_ylim(-0.5 if ax is b else 0, top)
        ax.axvspan(-400, 3000, color="#f2f1ec", zorder=0, lw=0)
        ax.text(1300, top * 0.95, "usual budget", ha="center", va="top", fontsize=7, color=MUTED)
        ax.set_xticks([0, 3000, 6000, 10000, 15000])
        ax.set_xticklabels(["0", "3k", "6k", "10k", "15k"])
        ax.set_xlabel("fine-tuning update")
    floor(a, NUM["floor"]["slr37.W.test_seen"])
    a.set_title("(a) CER on the fixed set", color=INK)
    a.set_ylabel("CER %")
    b.set_title("(b) Words with চ heard with ক", color=INK, fontfamily=["Nirmala UI", "Arial"])
    b.set_ylabel("% of such words")
    h, lab = a.get_legend_handles_labels()
    a.legend(h[::-1], lab[::-1], loc="center right")
    fig.tight_layout(w_pad=1.5)
    fig.savefig(OUT / "long.pdf")
    plt.close(fig)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for old in ("lr.pdf", "size.pdf"):
        (OUT / old).unlink(missing_ok=True)
    for f in (fig_design, fig_curves, fig_tests, fig_lr_size, fig_long):
        f()
    print("figures:", sorted(p.name for p in OUT.glob("*.pdf")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
