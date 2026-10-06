import csv
import re
from importlib.resources import files
from pathlib import Path

import pytest

from src.bnrep.normalize import foreign_tokens, normalize
from src.bnrep.reps import OOV_MARK, REP_IDS, convert

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "derived" / "slr37_bn_bd" / "manifest.tsv"
BENGALI = re.compile(r"[ঀ-৿]")
LATIN_REPS = ["LAT-G-det", "LAT-G-iso", "LAT-G-colloq", "LAT-uroman", "LAT-P", "LAT-P-dots", "IPA-P"]


def slr37_texts():
    if not MANIFEST.exists():
        pytest.skip("SLR37 manifest not generated")
    with open(MANIFEST, encoding="utf-8", newline="") as f:
        return [r["text"] for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE)]


def f5_vocab():
    path = files("f5_tts").joinpath("infer/examples/vocab.txt")
    return {line.rstrip("\n") for line in path.read_text(encoding="utf-8").splitlines(keepends=True)}


# ---------------------------------------------------------------- normalization

def test_precomposed_and_decomposed_nukta_are_identical():
    assert normalize("বিদ্যালয়") == normalize("বিদ্যালয়")


def test_zero_width_removed_and_danda_mapped():
    assert normalize("শাহ্‌ আলম।") == "শাহ্ আলম."
    assert normalize("ক  খ ।") == "ক খ."


def test_foreign_tokens_detected():
    assert foreign_tokens(normalize("স্টক এর চিহ্ন GOOG।")) == ["GOOG"]


# ---------------------------------------------------------------- phonemic arm (Google lexicon)

@pytest.mark.parametrize("word,expected", [
    ("ভালো", "bhalo"), ("ক্ষমা", "khOma"), ("জ্ঞান", "gEn"), ("আত্মা", "atta"),
    ("স্বাগত", "shagoto"), ("করা", "kOra"), ("করুণ", "korun"), ("এক", "Ek"), ("একে", "eke"),
])
def test_lat_p_matches_google_lexicon(word, expected):
    assert convert("LAT-P", word).text == expected


def test_lat_p_separates_ambiguous_digraphs():
    out = convert("LAT-P", "অভিভাবকহীন").text
    assert "k-hin" in out


def test_lat_p_dots_and_ipa():
    assert convert("LAT-P-dots", "ভালো").text == "bha.lo"
    assert convert("IPA-P", "ভালো").text == "bʰalo"


def test_oov_is_reported_not_silently_dropped():
    res = convert("LAT-P", "ক্সযঝটঠ")  # nonsense word, not in lexicon
    assert res.oov == ["ক্সযঝটঠ"] and OOV_MARK in res.text


# ---------------------------------------------------------------- corpus-level invariants

@pytest.mark.parametrize("rep", LATIN_REPS)
def test_no_bengali_leaks_in_latin_reps(rep):
    leaks = [t for t in slr37_texts() if BENGALI.search(convert(rep, t).text)]
    assert not leaks, f"{rep}: {len(leaks)} utterances leak Bengali chars, e.g. {leaks[:2]}"


@pytest.mark.parametrize("rep", REP_IDS)
def test_deterministic(rep):
    texts = slr37_texts()[:50]
    assert [convert(rep, t).text for t in texts] == [convert(rep, t).text for t in texts]


@pytest.mark.parametrize("rep", ["LAT-G-det", "LAT-G-colloq", "LAT-uroman", "LAT-P"])
def test_ascii_reps_fit_f5_base_vocab(rep):
    vocab = f5_vocab()
    missing = set()
    for t in slr37_texts():
        res = convert(rep, t)
        missing |= {c for c in res.text if c not in vocab and c != OOV_MARK}
    assert not missing, f"{rep}: symbols absent from F5 base vocab: {sorted(missing)}"
