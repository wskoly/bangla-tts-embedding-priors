"""Canonical text normalization shared by every representation (decision D-009).

Canonical form:
  * Unicode NFC. Note: NFC *decomposes* the precomposed letters য় ড় ঢ়
    (U+09DF/09DC/09DD are composition exclusions), which matches the Google
    bn lexicon's own storage; we keep that form.
  * ZWJ / ZWNJ removed (rendering-only; no pronunciation content).
  * Danda / double danda -> "." ; runs of whitespace -> single space.
  * Non-Bengali tokens (e.g. Latin "GOOG") pass through unchanged and are
    reported by `foreign_tokens()` so every arm treats them identically.
"""

from __future__ import annotations

import re
import unicodedata

ZW = "‌‍"
DANDA = {"।": ".", "॥": "."}
BENGALI_RE = re.compile(r"[ঀ-৿]+")
PUNCT_RE = re.compile(r"[.,!?;:]")
TOKEN_RE = re.compile(r"[ঀ-৿]+|[^\sঀ-৿.,!?;:]+|[.,!?;:]")


def normalize(text: str) -> str:
    t = unicodedata.normalize("NFC", text)
    t = "".join(ch for ch in t if ch not in ZW)
    for k, v in DANDA.items():
        t = t.replace(k, v)
    t = re.sub(r"\s+", " ", t).strip()
    t = re.sub(r"\s+([.,!?;:])", r"\1", t)  # no space before punctuation
    return t


def normalize_word(word: str) -> str:
    return "".join(ch for ch in unicodedata.normalize("NFC", word) if ch not in ZW)


def tokens(text: str) -> list[str]:
    """Split canonical text into Bengali words, other words and punctuation (spaces implied)."""
    return TOKEN_RE.findall(text)


def is_bengali(tok: str) -> bool:
    return bool(BENGALI_RE.fullmatch(tok))


def is_punct(tok: str) -> bool:
    return bool(PUNCT_RE.fullmatch(tok))


def foreign_tokens(text: str) -> list[str]:
    return [t for t in tokens(text) if not is_bengali(t) and not is_punct(t)]


def detokenize(toks: list[str]) -> str:
    out = ""
    for t in toks:
        if is_punct(t):
            out += t
        else:
            out += (" " if out else "") + t
    return out
