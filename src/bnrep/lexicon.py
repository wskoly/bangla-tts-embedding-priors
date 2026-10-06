"""Google bn pronunciation lexicon (CC BY 4.0) with canonical keys.

Pronunciations are kept as lists of syllables, each a list of Google ASCII
phonemes, e.g. ভালো -> [["bh", "a"], ["l", "o"]].
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from .normalize import normalize_word

ROOT = Path(__file__).resolve().parents[2]
LEX_DIR = ROOT / "data" / "external" / "google_language_resources_bn"

Pron = list[list[str]]


def parse_pron(s: str) -> Pron:
    return [syl.split() for syl in s.split(" . ")]


@lru_cache(maxsize=1)
def load_lexicon() -> tuple[dict[str, Pron], dict[str, int]]:
    """Returns (word -> first pronunciation, word -> number of distinct pronunciations)."""
    lex: dict[str, Pron] = {}
    n_prons: dict[str, int] = {}
    for line in (LEX_DIR / "lexicon.tsv").read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        cols = line.split("\t")
        if len(cols) < 2:
            continue
        w = normalize_word(cols[0])
        n_prons[w] = n_prons.get(w, 0) + 1
        lex.setdefault(w, parse_pron(cols[1]))
    return lex, n_prons


@lru_cache(maxsize=1)
def phoneme_to_ipa() -> dict[str, str]:
    table = {}
    for line in (LEX_DIR / "phonemes.txt").read_text(encoding="utf-8").splitlines():
        if line.strip():
            a, b = line.split("\t")
            table[a] = b
    return table


def lookup(word: str) -> Pron | None:
    return load_lexicon()[0].get(normalize_word(word))
