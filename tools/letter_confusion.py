"""Letter-prior confusions in the ASR transcripts (post hoc, exploratory; extends the চ→ক check of D-063).

For each Bengali letter whose Latin spelling in some arm clashes with an English or pinyin reading, count reference
words containing the letter whose substituted form (every occurrence replaced) appears in the hypothesis, and the
share of those reference words recovered exactly. The pairs below were fixed before any rate was computed (D-076).
The key control is the same text on fresh rows: if a confusion comes from the pretrained letter prior, the
pretrained arm (LAT-P, LAT-G-det) should show it more than its fresh twin (LAT-P-reinit, LAT-G-det-reinit).
ASR on the real recordings gives the floor. Whisper, test_seen, 3,000 updates, all seeds pooled.
    python tools/letter_confusion.py
"""

from __future__ import annotations

import csv
import random
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import analyze_c1 as c1  # noqa: E402
import analyze_c3 as c3  # noqa: E402

ASR = "tugstugi_bengaliai-asr_whisper-medium"
OUT = ROOT / "docs/reports/letter_confusion.md"
B, BOOT_SEED = 2000, 20261013

# (source letter, substituted letter, spellings that motivate the check)
PAIRS = [
    ("চ", "ক", "LAT-P / LAT-G-asp `c` (English /k/); ITRANS `ch`"),
    ("থ", "ত", "`th` in all Latin arms (English /θ/)"),
    ("খ", "ক", "control: generic loss of aspiration; `kh` has no English clash"),
    ("ছ", "চ", "ITRANS `Ch` vs `ch` (case); LAT-P / LAT-G-asp `ch` (English /tʃ/ = চ)"),
    ("ট", "ত", "LAT-P / ITRANS `T` vs `t` (case); LAT-G-asp `ṭ`"),
    ("ড", "দ", "LAT-P / ITRANS `D` vs `d` (case); LAT-G-asp `ḍ`"),
    ("ত", "ট", "reverse of `T`/`t`"),
    ("দ", "ড", "reverse of `D`/`d`"),
    ("ব", "ভ", "ITRANS `v` (English /v/)"),
    ("ং", "ন", "LAT-P `N` vs `n` (case)"),
]
ARMS = ["LAT-P", "LAT-P-reinit", "LAT-G-det", "LAT-G-det-reinit", "LAT-G-asp", "BN-G-iv-vm-asp", "BN-G-matched"]
TWINS = [("LAT-P", "LAT-P-reinit"), ("LAT-G-det", "LAT-G-det-reinit")]
CORPORA = {"SLR37": (c3, ROOT / "data/derived/asr_floor_v1"), "Rasa": (c1, ROOT / "data/derived/asr_floor_rasa_v1")}


def read(path: Path) -> list[dict]:
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE))


def counts(rows: list[dict], src: str, tgt: str) -> dict[str, list[int]]:
    """Per utterance: [reference words with src, of which substituted form in hyp, of which exact word in hyp]."""
    per = defaultdict(lambda: [0, 0, 0])
    for r in rows:
        hyp = set(r["hyp"].split())
        for w in r["ref"].split():
            if src in w:
                c = per[r["utt_id"]]
                c[0] += 1
                c[1] += w.replace(src, tgt) in hyp
                c[2] += w in hyp
    return per


def rate(per: dict[str, list[int]], i: int) -> float:
    n = sum(v[0] for v in per.values())
    return 100 * sum(v[i] for v in per.values()) / n if n else float("nan")


def diff_ci(a: dict, b: dict, i: int) -> tuple[float, float, float]:
    """Rate(a) - rate(b) with a 95 % bootstrap interval over utterances (seeds pooled within an utterance)."""
    utts = sorted(set(a) | set(b))
    rng = random.Random(BOOT_SEED)
    z = [0, 0, 0]
    d = []
    for _ in range(B):
        s = [utts[rng.randrange(len(utts))] for _ in utts]
        na, ka = sum(a.get(u, z)[0] for u in s), sum(a.get(u, z)[i] for u in s)
        nb, kb = sum(b.get(u, z)[0] for u in s), sum(b.get(u, z)[i] for u in s)
        if na and nb:
            d.append(100 * (ka / na - kb / nb))
    d.sort()
    return rate(a, i) - rate(b, i), d[int(0.025 * len(d))], d[int(0.975 * len(d)) - 1]


def main() -> int:
    L = ["# Letter-prior confusions (D-076; post hoc, exploratory)", "",
         "Whisper transcripts, test_seen, 3,000 updates, all training seeds pooled (SLR37: 3 seeds, C3 runs; Rasa: "
         "3 seeds, C1 runs; Rasa uses all seen sentences, including words filled by G2P for LAT-P). *sub*: share of "
         "reference words containing the source letter whose substituted form appears in the hypothesis. *ok*: share "
         "recovered exactly. *floor*: ASR on the real recordings. Word matching is exact and order-free, so *sub* "
         "is a lower bound on the confusion. The pairs were fixed before any rate was computed. Twin differences "
         "(pretrained minus fresh rows on identical text) carry a 95 % bootstrap interval over sentences "
         f"({B} resamples). Not corrected for multiple comparisons.", ""]
    for corpus, (mod, floor_dir) in CORPORA.items():
        rows = {a: [r for d in mod.run_dirs(a) for r in read(d / f"eval/u3000/test_seen/asr_{ASR}.tsv")]
                for a in ARMS}
        rows["floor"] = read(floor_dir / f"{ASR}__test_seen.tsv")
        cols = ARMS + ["floor"]
        L += [f"## {corpus}", "", "### Substitution rate *sub* % (n reference words)", "",
              "| pair | motivated by | " + " | ".join(cols) + " |", "|---|---|" + "---|" * len(cols)]
        per = {(s, t, a): counts(rows[a], s, t) for s, t, _ in PAIRS for a in cols}
        for s, t, why in PAIRS:
            n = sum(v[0] for v in per[(s, t, "floor")].values())
            L.append(f"| {s}→{t} (n={n}) | {why} | "
                     + " | ".join(f"{rate(per[(s, t, a)], 1):.1f}" for a in cols) + " |")
        L += ["", "### Exact recovery *ok* % of words containing the source letter", "",
              "| letter | " + " | ".join(cols) + " |", "|---|" + "---|" * len(cols)]
        for s, t, _ in PAIRS:
            L.append(f"| {s} | " + " | ".join(f"{rate(per[(s, t, a)], 2):.1f}" for a in cols) + " |")
        L += ["", "### Pretrained minus fresh rows on identical text: *sub* difference, pp [95 % CI]", "",
              "| pair | " + " | ".join(f"{p} − {f}" for p, f in TWINS) + " |", "|---|" + "---|" * len(TWINS)]
        for s, t, _ in PAIRS:
            cells = []
            for p, f in TWINS:
                d, lo, hi = diff_ci(per[(s, t, p)], per[(s, t, f)], 1)
                cells.append(f"{d:+.1f} [{lo:+.1f}, {hi:+.1f}]")
            L.append(f"| {s}→{t} | " + " | ".join(cells) + " |")
        L.append("")
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
