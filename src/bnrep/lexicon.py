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


SUPPLEMENT_FILE = ROOT / "data" / "curation" / "lexicon_supplement_v1.tsv"


@lru_cache(maxsize=1)
def load_supplement() -> dict[str, Pron]:
    """Audited pronunciations for SLR37 words missing from the Google lexicon (D-014)."""
    if not SUPPLEMENT_FILE.exists():
        return {}
    supp = {}
    for line in SUPPLEMENT_FILE.read_text(encoding="utf-8").splitlines():
        if line.strip() and not line.startswith("#"):
            w, p, _src = line.split("\t")
            supp[normalize_word(w)] = parse_pron(p)
    return supp


def compound_lookup(word: str, table: dict[str, Pron], min_part: int = 2) -> Pron | None:
    """Two-part compound fallback: split into two dictionary words, preferring the longest first part.

    Targets the dominant systematic G2P v1 error class (compounds whose parts are known, D-014).
    """
    w = normalize_word(word)
    for i in range(len(w) - min_part, min_part - 1, -1):
        left, right = w[:i], w[i:]
        if left in table and right in table and not right.startswith("্") and not _is_dependent(right[0]):
            return table[left] + table[right]
    return None


def _is_dependent(ch: str) -> bool:
    # vowel signs, virama, nukta, candrabindu/anusvara/visarga cannot start a word
    return 0x09BC <= ord(ch) <= 0x09D7 or ch in "ঁংঃ"


def lookup(word: str, use_supplement: bool = True) -> Pron | None:
    w = normalize_word(word)
    pron = load_lexicon()[0].get(w)
    if pron is None and use_supplement:
        pron = load_supplement().get(w)
    return pron
