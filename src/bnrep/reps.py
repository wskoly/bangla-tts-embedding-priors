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


# Encoding-path arms (D-034): Bengali codepoints moved step by step toward ITRANS structure.
# Canonical (NFC) text keeps য়/ড়/ঢ় decomposed as base + nukta, as BN-G does; these arms keep that encoding.
_CONSONANTS = {chr(c) for c in range(0x0995, 0x09BA)}  # ৎ excluded: no inherent vowel
_NUKTA = "়"
_VOWEL_SIGNS = {"া": "আ", "ি": "ই", "ী": "ঈ", "ু": "উ", "ূ": "ঊ", "ৃ": "ঋ", "ৄ": "ৠ", "ে": "এ", "ৈ": "ঐ",
                "ো": "ও", "ৌ": "ঔ", "ৗ": "ঔ", "ৢ": "ঌ", "ৣ": "ৡ"}
_HASANTA = "্"
_ASPIRATES = {"খ": "কহ", "ঘ": "গহ", "ছ": "চহ", "ঝ": "জহ", "ঠ": "টহ", "ঢ": "ডহ", "থ": "তহ", "ধ": "দহ",
              "ফ": "পহ", "ভ": "বহ"}


def _bn_g_iv(word: str) -> str:
    """Explicit inherent vowel অ after every consonant (+ nukta) not followed by a vowel sign or hasanta;
    hasanta dropped."""
    out = []
    for i, ch in enumerate(word):
        if ch == _HASANTA:
            continue
        out.append(ch)
        j = i + 1
        if ch in _CONSONANTS and j < len(word) and word[j] == _NUKTA:
            continue  # decide after the nukta
        base = ch == _NUKTA and i > 0 and word[i - 1] in _CONSONANTS
        nxt = word[j] if j < len(word) else ""
        if (ch in _CONSONANTS or base) and nxt not in _VOWEL_SIGNS and nxt != _HASANTA:
            out.append("অ")
    return "".join(out)


def _bn_g_iv_vm(word: str) -> str:
    return "".join(_VOWEL_SIGNS.get(ch, ch) for ch in _bn_g_iv(word))


def _bn_g_iv_vm_asp(word: str) -> str:
    """Aspirates split into unaspirated + হ; the nukta stays on its base letter (ঢ় -> ড় + হ)."""
    s = _bn_g_iv_vm(word).replace("ঢ" + _NUKTA, "ড" + _NUKTA + "হ")
    return "".join(_ASPIRATES.get(ch, ch) for ch in s)


# LAT-G-asp (D-036): one-to-one relabeling of BN-G-iv-vm-asp onto single lowercase characters that already
# have pretrained F5 rows. Frequent symbols get plain ASCII with plausible English/pinyin priors; rare symbols
# and retroflexes get diacritic letters. No case pairs; the only digraphs are aspirates (C + h), as in the source.
_LAT_G_ASP_PAIRS = {"ড" + _NUKTA: "ṛ", "য" + _NUKTA: "ý"}
_LAT_G_ASP_MAP = {
    "অ": "o", "আ": "a", "ই": "i", "ঈ": "ī", "উ": "u", "ঊ": "ū", "ঋ": "ř", "এ": "e", "ঐ": "ê", "ও": "ō", "ঔ": "ô",
    "ক": "k", "গ": "g", "ঙ": "ṅ", "চ": "c", "জ": "j", "ঞ": "ñ", "ট": "ṭ", "ড": "ḍ", "ণ": "ṇ", "ত": "t", "দ": "d",
    "ন": "n", "প": "p", "ব": "b", "ম": "m", "য": "y", "র": "r", "ল": "l", "শ": "x", "ষ": "ṣ", "স": "s", "হ": "h",
    "ৎ": "ť", "ং": "ṁ", "ঃ": "ḥ", "ঁ": "ṃ",
}


def _lat_g_asp(word: str) -> str:
    s = _bn_g_iv_vm_asp(word)
    for k, v in _LAT_G_ASP_PAIRS.items():
        s = s.replace(k, v)
    out = "".join(_LAT_G_ASP_MAP.get(ch, ch) for ch in s)
    assert not any("ঀ" <= ch <= "৿" for ch in out), (word, out)
    return out


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
    "BN-G-iv": _bn_g_iv,
    "BN-G-iv-vm": _bn_g_iv_vm,
    "BN-G-iv-vm-asp": _bn_g_iv_vm_asp,
    "LAT-G-asp": _lat_g_asp,
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


_PROFILE_G2P: list = []


def _profile_g2p() -> G2P | None:
    """C1 (D-057): when the data profile allows G2P, lexical arms fill out-of-lexicon words with G2P v1
    (CPU, greedy, so identical in training, inference and vocab checks). SLR37 profile: None (unchanged)."""
    if not _PROFILE_G2P:
        from src.corpus.profile import ALLOW_G2P, ROOT
        g = None
        if ALLOW_G2P:
            from .g2p.model import G2P as G2PModel
            g = G2PModel(ROOT / "runs/g2p/v1", device="cpu")
        _PROFILE_G2P.append(g)
    return _PROFILE_G2P[0]


def convert(rep_id: str, text: str, g2p: G2P | None = None, already_normalized: bool = False) -> Result:
    if rep_id not in WORD_CONVERTERS and rep_id not in LEXICAL_CONVERTERS:
        raise KeyError(f"unknown representation {rep_id!r}; known: {REP_IDS}")
    if g2p is None and rep_id in LEXICAL_CONVERTERS:
        g2p = _profile_g2p()
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
