"""Representation modules (IDs fixed in docs/D3 §6, decision D-005).

Every converter maps *canonical* text (see normalize.py) to the string that the
TTS model receives. Shared conventions across all arms:
  * word separator = single space; punctuation = "." etc., attached to the previous word;
  * non-Bengali tokens (e.g. "GOOG") pass through unchanged;
  * lexicon-based arms (LAT-P, IPA-P, BN-P later) need a G2P for out-of-lexicon
    words; without one, `convert` records them in `Result.oov` and emits the
    placeholder OOV_MARK so callers can refuse the utterance.
"""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass, field
from typing import Callable, Protocol

from .lexicon import Pron, lookup, phoneme_to_ipa
from .normalize import detokenize, is_bengali, normalize, tokens

OOV_MARK = "⁇"  # ⁇ ; never valid model input

# Multi-letter Google phonemes that can be mis-read when phonemes are concatenated.
_DIGRAPHS = {"kh", "gh", "ch", "jh", "Th", "Dh", "th", "dh", "bh", "sh"}
_PRECOMPOSE = {"য়": "য়", "ড়": "ড়", "ঢ়": "ঢ়"}


class G2P(Protocol):
    def __call__(self, word: str) -> Pron | None: ...


@dataclass
class Result:
    text: str
    oov: list[str] = field(default_factory=list)  # words not in the lexicon (G2P-filled or OOV_MARK)


def _precompose(word: str) -> str:
    for k, v in _PRECOMPOSE.items():
        word = word.replace(k, v)
    return word


# ---------------------------------------------------------------- grapheme arms

def _bn_g(word: str) -> str:
    return word


def _lat_g_itrans(word: str) -> str:
    from indic_transliteration import sanscript
    return sanscript.transliterate(_precompose(word), sanscript.BENGALI, sanscript.ITRANS)


def _lat_g_iso(word: str) -> str:
    from indic_transliteration import sanscript
    return unicodedata.normalize("NFC", sanscript.transliterate(_precompose(word), sanscript.BENGALI, sanscript.ISO))


def _lat_g_colloq(word: str) -> str:
    # Placeholder until Dakshina-attested romanizations are wired in (D4 3.3).
    from aksharamukha import transliterate
    return transliterate.process("Bengali", "RomanColloquial", _precompose(word))


_UROMAN = None


def _lat_uroman(word: str) -> str:
    global _UROMAN
    if _UROMAN is None:
        import uroman
        _UROMAN = uroman.Uroman()
    return _UROMAN.romanize_string(word)


# ---------------------------------------------------------------- phonemic arms

GLIDE_ASCII = "'"  # Google marks non-syllabic glides with "^" (absent from the F5 vocab)


def _needs_sep(left: str, ph: str) -> bool:
    """True if appending `ph` after `left` would read as a digraph phoneme."""
    return bool(left) and ph.startswith("h") and (left[-1:] + "h") in _DIGRAPHS


def pron_to_lat_p(pron: Pron, dots: bool = False) -> str:
    syllables = []
    for syl in pron:
        s = ""
        for ph in syl:
            ph = ph.replace("^", GLIDE_ASCII)
            if _needs_sep(s, ph):
                s += "-"  # disambiguate e.g. /k h/ vs /kh/ (0.1 % of lexicon words)
            s += ph
        syllables.append(s)
    if dots:
        return ".".join(syllables)
    out = ""
    for s in syllables:
        if _needs_sep(out, s):
            out += "-"
        out += s
    return out


def pron_to_ipa(pron: Pron) -> str:
    table = phoneme_to_ipa()
    return "".join(table[ph] for syl in pron for ph in syl)


def _make_lexical(render: Callable[[Pron], str]) -> Callable[[str, G2P | None], tuple[str, bool]]:
    def conv(word: str, g2p: G2P | None) -> tuple[str, bool]:
        pron = lookup(word)
        if pron is not None:
            return render(pron), False
        pron = g2p(word) if g2p is not None else None
        return (render(pron) if pron is not None else OOV_MARK), True
    return conv


# ---------------------------------------------------------------- registry

WORD_CONVERTERS: dict[str, Callable[[str], str]] = {
    "BN-G": _bn_g,
    "LAT-G-det": _lat_g_itrans,
    "LAT-G-iso": _lat_g_iso,
    "LAT-G-colloq": _lat_g_colloq,
    "LAT-uroman": _lat_uroman,
}
# LAT-P-rand control (D-028): fixed derangement of the full 27-symbol LAT-P alphabet (lexicon + supplement),
# generated with random.Random(20261007), no fixed points. Same embedding rows, same length and same information
# as LAT-P; only the sound-to-letter correspondence learned in pretraining is scrambled. Space / "." unchanged.
LAT_P_RAND_MAP = {"'": "E", "-": "e", "D": "O", "E": "c", "N": "m", "O": "i", "T": "r", "a": "N", "b": "j",
                  "c": "u", "d": "f", "e": "p", "f": "g", "g": "h", "h": "t", "i": "D", "j": "s", "k": "n",
                  "l": "o", "m": "T", "n": "-", "o": "k", "p": "b", "r": "d", "s": "l", "t": "'", "u": "a"}
_LAT_P_RAND_TABLE = str.maketrans(LAT_P_RAND_MAP)


def pron_to_lat_p_rand(pron: Pron) -> str:
    return pron_to_lat_p(pron).translate(_LAT_P_RAND_TABLE)


LEXICAL_CONVERTERS = {
    "LAT-P-rand": _make_lexical(pron_to_lat_p_rand),
    "LAT-P": _make_lexical(pron_to_lat_p),
    "LAT-P-dots": _make_lexical(lambda p: pron_to_lat_p(p, dots=True)),
    "IPA-P": _make_lexical(pron_to_ipa),
}
REP_IDS = list(WORD_CONVERTERS) + list(LEXICAL_CONVERTERS)


def convert(rep_id: str, text: str, g2p: G2P | None = None, already_normalized: bool = False) -> Result:
    if rep_id not in WORD_CONVERTERS and rep_id not in LEXICAL_CONVERTERS:
        raise KeyError(f"unknown representation {rep_id!r}; known: {REP_IDS}")
    canon = text if already_normalized else normalize(text)
    out, oov = [], []
    for tok in tokens(canon):
        if not is_bengali(tok):
            out.append(tok)
        elif rep_id in WORD_CONVERTERS:
            out.append(WORD_CONVERTERS[rep_id](tok))
        else:
            s, was_oov = LEXICAL_CONVERTERS[rep_id](tok, g2p)
            if was_oov:
                oov.append(tok)
            out.append(s)
    return Result(detokenize(out), oov)
