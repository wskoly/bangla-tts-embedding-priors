"""G2P v1 audit of the 188 SLR37 out-of-lexicon word types (decision D-014).

Single source of truth for the audit judgments. Produces:
  data/curation/text_corrections_v1.tsv   transcript typo fixes + abbreviation expansions (applied by normalize())
  data/curation/lexicon_supplement_v1.tsv  frozen pronunciations for every SLR37 word missing from the Google lexicon
  docs/reports/g2p_v1_audit.md             category counts, examples, structure / frequency analysis

Judgments were made against (a) Google's transcription guide (bn/transcription.md) and (b) the
lexicon's own conventions for related stems (looked up per case; see notes). They are a careful
model-assisted audit, NOT native-speaker verification; items marked `needs_native_check` are the ones
where Bangladeshi Standard Colloquial pronunciation is genuinely uncertain.

Usage: python tools/curation/g2p_audit_v1.py
"""

from __future__ import annotations

import collections
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.bnrep.lexicon import load_lexicon, parse_pron  # noqa: E402
from src.bnrep.normalize import normalize_word  # noqa: E402

PRED = ROOT / "data/derived/g2p/slr37_oov_g2p_v1.tsv"
OUT_CORR = ROOT / "data/curation/text_corrections_v1.tsv"
OUT_SUPP = ROOT / "data/curation/lexicon_supplement_v1.tsv"
OUT_REPORT = ROOT / "docs/reports/g2p_v1_audit.md"
N_SLR37_WORD_TOKENS = 15394

CATS = {
    1: "Correct",
    2: "Minor phonological variation",
    3: "Genuine phoneme error",
    4: "Stress/prosody/diacritic issue",
    5: "Word-boundary / compound segmentation issue",
    6: "Lexicon/G2P disagreement",
    7: "Clearly incorrect pronunciation",
    8: "Unhandled input (abbreviation)",
    9: "Transcript misspelling (G2P faithful to the misspelled input)",
}
ERROR_CATS = {3, 5, 6, 7}

# word -> (category, corrected Google pronunciation or None, phenomenon tags, note)
AUDIT: dict[str, tuple[int, str | None, list[str], str]] = {
    # ---- 2: minor variation (vowel quality o/O, glide-vs-syllable, syllabification only)
    "সুন্দরবনে": (2, "sh u n . d o r . b o . n e", ["inherent_vowel"], "lexicon বনে = b o . n e (G2P: b O)"),
    "পোঁছাবে": (2, None, ["nonstandard_spelling", "nasalization"],
                "nonstandard spelling of পৌঁছাবে (lexicon p o u^ . ch a . b e); G2P follows spelling; "
                "speaker reading unknown -> kept; needs_native_check"),
    "ওয়েস্ট": (2, "o^ e s T", ["glide"], "guide: ওয়া -> o^ a (on-glide); G2P split into two syllables"),
    "নরওয়ের": (2, "n O r . o^ e r", ["glide"], "glide vs extra syllable"),
    "পার্কওয়ের": (2, "p a r k . o^ e r", ["glide", "compound"], "glide vs extra syllable"),
    "ওয়েবসাইটের": (2, "o^ e b . s a i^ . T e r", ["glide"], "glide vs extra syllable"),
    "বিষয়ে": (2, "b i . sh o . e", ["glide", "inherent_vowel"], "lexicon বিষয় = b i . sh o e^; G2P sh O e^ . e"),
    "ডেট্রয়েটে": (2, None, ["glide"], "Detroit: r O . e vs r O e^; acceptable"),
    "এংগ্রি": (2, None, ["loanword"], "English 'angry'; spelled এ -> e; E arguably closer; kept spelling-faithful"),
    "কাজাখস্তানের": (2, None, ["syllabification"],
                     "phones correct; syllable boundary kh . s t unusual; harmless for LAT-P (no dots)"),
    # ---- 3: genuine phoneme errors
    "পদ্মা": (3, "p O d . d a", ["conjunct"],
              "দ্ম assimilates to geminate dd (/pɔd.da/); lexicon has no দ্ম precedent except English রিদ্মিক"),
    "ব্রাহ্মণবাড়িয়া": (3, "b r a m . m o n . b a . r i . a", ["conjunct", "compound", "proper_name"],
                        "হ্ম -> mm (/bram.mon/); G2P copied spelling-style h m from Arabic names (আহ্মদ)"),
    "টাচডাঊন": (3, None, ["rare_char", "loanword"],
                "dropped u^ (rare independent ঊ); handled via spelling correction to টাচডাউন"),
    "অস্ট্রেলিয়ায়": (3, "O s . T r e . l i . a e^", ["suffix", "glide"],
                      "locative -য় dropped; lexicon অস্ট্রেলিয়া = O s . T r e . l i . a"),
    "সক্রিয়": (3, "sh O k . r i . o", ["sibilant"], "স -> sh word-initially before k (/ʃɔkrio/); needs_native_check"),
    "ইইউ": (3, "i . i u^", ["initialism"], "initialism EU; G2P merged the two vowels"),
    "হার্ডওয়্যার": (3, "h a r D . o^ E r", ["ya_phala", "glide", "compound"],
                    "must match সফটওয়্যার / ফুটওয়্যার (o^ E r); G2P o . a r"),
    "আশ্রয়স্থল": (3, "a sh . r o e^ . s th O l", ["conjunct", "glide", "compound"],
                  "lost য় glide; শ্র is s/sh-inconsistent in the lexicon itself; needs_native_check"),
    "দোলেস্বর": (3, None, ["conjunct", "proper_name"],
                 "medial স্ব -> geminate sh (ঈশ্বর = i sh . sh O r); handled via spelling correction to দোলেশ্বর"),
    # ---- 5: compound segmentation
    "সফটব্যাংক": (5, "s O f T . b E N k", ["compound", "loanword"],
                  "both parts in lexicon (সফট = s O f T); G2P invented a vowel (sh O . f o T)"),
    # ---- 6: lexicon / G2P disagreement
    "ইয়েমেনের": (6, "i^ e . m e . n e r", ["glide", "proper_name"], "guide example ইয়েমেন = i^ e . m e n; G2P i . e"),
    # ---- 7: clearly incorrect
    "ডাক্তারবাড়ির": (7, "D a k . t a r . b a . r i r", ["compound", "retroflex"],
                      "initial D -> r; ডাক্তার = D a k . t a r in lexicon"),
    # ---- 8: abbreviations (expanded in text normalization for ALL arms)
    "মোঃ": (8, None, ["abbreviation"], "expanded to মোহাম্মদ (lexicon m o . h a m . m o d); needs ASR/listening check"),
    "লিঃ": (8, None, ["abbreviation"], "expanded to লিমিটেড (spelled out earlier in the same sentence)"),
    "ডঃ": (8, None, ["abbreviation"], "expanded to ডক্টর (lexicon D O k . T o r)"),
    # ---- 9: transcript misspellings where the G2P is faithful to the wrong spelling
    "চট্রগ্রাম": (9, None, ["typo", "conjunct", "proper_name"], "-> চট্টগ্রাম (lexicon); 11 tokens, 1 speaker"),
    "সরবারহ": (9, None, ["typo"], "-> সরবরাহ (lexicon)"),
    "নিমার্ণকারী": (9, None, ["typo"], "-> নির্মাণকারী"),
    "গুলাশানে": (9, None, ["typo", "proper_name"], "-> গুলশানে"),
    "রিকাের": (9, None, ["typo", "proper_name"], "-> রিকার (কোস্টা রিকার রাজধানী)"),
    "জীবনান্নদ": (9, None, ["typo", "proper_name"], "-> জীবনানন্দ"),
    "কলম্বিয়াের": (9, None, ["typo", "proper_name"], "-> কলম্বিয়ার"),
}

# Typos the G2P happened to handle correctly (category 1, but the transcript is still fixed for every arm)
ROBUST_TYPOS = {
    "শুুক্রবার": "শুক্রবার", "পাাসিং": "পাসিং", "ধরেে": "ধরে", "না্ম": "নাম",
    "ম্যা্নচেস্টার": "ম্যানচেস্টার", "আজকেে": "আজকে",
}

# Text corrections applied in normalize() to every representation (original -> corrected)
CORRECTIONS = {
    "চট্রগ্রাম": ("চট্টগ্রাম", "typo"), "সরবারহ": ("সরবরাহ", "typo"), "নিমার্ণকারী": ("নির্মাণকারী", "typo"),
    "গুলাশানে": ("গুলশানে", "typo"), "রিকাের": ("রিকার", "typo"), "জীবনান্নদ": ("জীবনানন্দ", "typo"),
    "কলম্বিয়াের": ("কলম্বিয়ার", "typo"), "টাচডাঊন": ("টাচডাউন", "typo"), "দোলেস্বর": ("দোলেশ্বর", "typo"),
    **{k: (v, "typo") for k, v in ROBUST_TYPOS.items()},
    "মোঃ": ("মোহাম্মদ", "abbreviation"), "লিঃ": ("লিমিটেড", "abbreviation"), "ডঃ": ("ডক্টর", "abbreviation"),
}

# Pronunciations for corrected spellings that are not in the Google lexicon
MANUAL = {
    "নির্মাণকারী": "n i r . m a n . k a . r i",
    "গুলশানে": "g u l . sh a . n e",
    "রিকার": "r i . k a r",
    "জীবনানন্দ": "j i . b o . n a . n O n . d o",
    "কলম্বিয়ার": "k O . l o m . b i . a r",
    "টাচডাউন": "T a c . D a u^ n",
    "পাসিং": "p a . s i N",
    "ম্যানচেস্টার": "m E n . c e s . T a r",
    "দোলেশ্বর": "d o . l e sh . sh O r",
    "লিমিটেড": "l i . m i . T e D",
}

# orthographic structure tags inferred for every word (for the structure analysis)
TAG_CHARS = {
    "conjunct (virama)": "্", "chandrabindu": "ঁ", "anusvara": "ং", "visarga": "ঃ",
    "aspirate letter": "খঘছঝঠঢথধফভ", "retroflex letter": "টঠডঢণ",
}


def ortho_tags(w: str) -> set[str]:
    tags = {t for t, chars in TAG_CHARS.items() if any(c in w for c in chars)}
    if "্য" in w:
        tags.add("ya-phala")
    return tags


def main() -> int:
    lex = load_lexicon()[0]
    with open(PRED, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE))
    assert len(rows) == 188, len(rows)
    missing = set(AUDIT) - {r["word"] for r in rows}
    assert not missing, f"audit keys not in predictions: {missing}"

    # ---- corrections table
    OUT_CORR.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_CORR, "w", encoding="utf-8", newline="\n") as f:
        f.write("original\tcorrected\ttype\n")
        for k, (v, t) in sorted(CORRECTIONS.items()):
            f.write(f"{k}\t{v}\t{t}\n")

    # ---- supplement lexicon: every SLR37 word that remains out-of-lexicon after corrections
    supp: dict[str, tuple[str, str]] = {}
    for r in rows:
        w = r["word"]
        if w in CORRECTIONS:
            target = CORRECTIONS[w][0]
            if normalize_word(target) not in lex:
                supp[target] = (MANUAL[target], "manual_for_corrected_spelling")
            continue
        cat, fixed, _, _ = AUDIT.get(w, (1, None, [], ""))
        supp[w] = (fixed, f"audit_override_cat{cat}") if fixed else (r["g2p_google"], f"g2p_v1_audited_cat{cat}")
    with open(OUT_SUPP, "w", encoding="utf-8", newline="\n") as f:
        f.write("# Supplement to the Google bn lexicon for SLR37 words (D-014). Same notation as lexicon.tsv.\n")
        f.write("# Columns: word, pronunciation, source. Generated by tools/curation/g2p_audit_v1.py\n")
        for w, (p, src) in sorted(supp.items()):
            parse_pron(p)
            f.write(f"{w}\t{p}\t{src}\n")

    # ---- report
    pred = {r["word"]: r for r in rows}
    cat_of = {w: AUDIT.get(w, (1, None, [], ""))[0] for w in pred}
    n_types = collections.Counter(cat_of.values())
    n_tok = collections.Counter()
    for w, r in pred.items():
        n_tok[cat_of[w]] += int(r["count"])
    tot_types, tot_tok = len(rows), sum(int(r["count"]) for r in rows)
    lines = ["# G2P v1 audit: 188 SLR37 out-of-lexicon word types", "",
             "Method: each prediction compared with Google's transcription guide and with the lexicon's own "
             "pronunciations of related stems. Model-assisted audit, **not native-speaker verification**; "
             "items marked `needs_native_check` should get a native spot check.", "",
             "| # | Category | Types | % types | Tokens | % tokens |", "|---|---|---|---|---|---|"]
    for c, name in CATS.items():
        lines.append(f"| {c} | {name} | {n_types[c]} | {100 * n_types[c] / tot_types:.1f} | {n_tok[c]} | "
                     f"{100 * n_tok[c] / tot_tok:.1f} |")
    lines += [f"| | **Total** | {tot_types} | 100 | {tot_tok} | 100 |", "", "## Examples by category", ""]
    for c, name in CATS.items():
        if c == 1:
            correct = sorted((r for w, r in pred.items() if cat_of[w] == 1), key=lambda r: -int(r["count"]))[:8]
            lines.append(f"**{c}. {name}:** " + "; ".join(f"{r['word']} `{r['g2p_google']}` (×{r['count']})"
                                                         for r in correct))
            lines += [f"Robust to transcript typos (also category 1): {', '.join(ROBUST_TYPOS)}", ""]
            continue
        ex = [(w, a) for w, a in AUDIT.items() if a[0] == c]
        if not ex:
            lines += [f"**{c}. {name}:** none (Google notation has no stress/tone marks).", ""]
            continue
        lines.append(f"**{c}. {name}:**")
        for w, (_, fixed, tags, note) in ex:
            lines.append(f"- {w} (×{pred[w]['count']}): G2P `{pred[w]['g2p_google']}`"
                         + (f" → `{fixed}`" if fixed else "") + f" — {note} [{', '.join(tags)}]")
        lines.append("")
    all_tags, err_tags = collections.Counter(), collections.Counter()
    for w in pred:
        t = ortho_tags(w)
        all_tags.update(t)
        if cat_of[w] in ERROR_CATS:
            err_tags.update(t)
    n_err = sum(n_types[c] for c in ERROR_CATS)
    lines += [f"## Orthographic structure of the {n_err} G2P errors (categories 3, 5, 6, 7)", "",
              "| structure | OOV words with it (of 188) | among errors | error rate within structure |",
              "|---|---|---|---|"]
    for t in [*TAG_CHARS, "ya-phala"]:
        rate = 100 * err_tags[t] / all_tags[t] if all_tags[t] else 0.0
        lines.append(f"| {t} | {all_tags[t]} | {err_tags[t]} | {rate:.1f} % |")
    base = 100 * n_err / tot_types
    sem = collections.Counter(tag for w, a in AUDIT.items() if a[0] in ERROR_CATS for tag in a[2])
    lines += ["", f"Base error rate over all 188 types: {base:.1f} %.", "",
              "Annotated phenomena among the errors: " + ", ".join(f"{k} {v}" for k, v in sem.most_common()), ""]
    freq_err = sorted(((int(pred[w]["count"]), w) for w in pred if cat_of[w] in ERROR_CATS), reverse=True)
    top20 = sorted(rows, key=lambda r: -int(r["count"]))[:20]
    err_tok = sum(n_tok[c] for c in ERROR_CATS)
    lines += ["## Frequency", "",
              f"- Top-20 most frequent OOV types ({sum(int(r['count']) for r in top20)} of {tot_tok} tokens): "
              f"categories {dict(collections.Counter(cat_of[r['word']] for r in top20))}.",
              f"- Error types with their corpus counts: {freq_err}.",
              f"- Error tokens: {err_tok} of {tot_tok} OOV tokens = {100 * err_tok / tot_tok:.1f} %; "
              f"of all {N_SLR37_WORD_TOKENS:,} SLR37 word tokens: {100 * err_tok / N_SLR37_WORD_TOKENS:.2f} %.", ""]
    OUT_REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUT_REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    print("\n".join(lines[4:6 + len(CATS) + 1]))
    print(f"supplement entries: {len(supp)}; corrections: {len(CORRECTIONS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
