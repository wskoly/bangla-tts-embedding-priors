"""Phase-4 representation benchmark (D4 §3): text-level properties of each representation.

No TTS involved. All metrics are computed on the same SLR37 transcripts (canonical form).

Usage:
    python -m src.bnrep.stats --g2p runs/g2p/v1 --out data/derived/rep_bench_v1 \
        --report docs/reports/phase4_representation_benchmark.md [--bpe Qwen/Qwen2.5-0.5B]
"""

from __future__ import annotations

import argparse
import collections
import csv
import json
import statistics
from importlib.resources import files
from pathlib import Path

from .lexicon import ROOT, load_lexicon
from .normalize import is_bengali, normalize, tokens
from .reps import OOV_MARK, REP_IDS, convert

ASPIRATES = set("খঘছঝঠঢথধফভ")
RETROFLEX = set("টঠডঢণ")
DENTAL = set("তথদধন")
LEXICON_COLLISION_REPS = ("BN-G", "LAT-G-det", "LAT-G-iso", "LAT-G-colloq", "LAT-uroman", "LAT-P", "IPA-P")


def describe(v: list[float]) -> dict:
    v = sorted(v)

    def q(p: float) -> float:
        return v[min(len(v) - 1, int(p * (len(v) - 1)))]

    return {"mean": statistics.mean(v), "median": q(.5), "p95": q(.95), "max": v[-1]}


def f5_vocab() -> set[str]:
    path = files("f5_tts").joinpath("infer/examples/vocab.txt")
    return {line.rstrip("\n") for line in path.read_text(encoding="utf-8").splitlines(keepends=True)}


def phenomena(canon: str) -> dict:
    words = [t for t in tokens(canon) if is_bengali(t)]
    s = "".join(words)
    lex = load_lexicon()[0]
    return {
        "words": len(words),
        "conjunct_viramas": s.count("্"),
        "aspirate_letters": sum(c in ASPIRATES for c in s),
        "retroflex_letters": sum(c in RETROFLEX for c in s),
        "dental_letters": sum(c in DENTAL for c in s),
        "chandrabindu": s.count("ঁ"),
        "anusvara": s.count("ং"),
        "visarga": s.count("ঃ"),
        "khanda_ta": s.count("ৎ"),
        "lexicon_oov_words": sum(w not in lex for w in words),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--g2p", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--report", type=Path, required=True)
    ap.add_argument("--bpe", default="", help="HF tokenizer id for BPE token counts (optional)")
    args = ap.parse_args()

    from .g2p.model import G2P
    g2p = G2P(args.g2p)

    with open(ROOT / "data/derived/slr37_bn_bd/manifest.tsv", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE))
    canon = {r["utt_id"]: normalize(r["text"]) for r in rows}
    speech = {r["utt_id"]: max(1e-3, float(r["duration_s"]) - float(r["lead_sil_s"]) - float(r["trail_sil_s"]))
              for r in rows}
    vocab = f5_vocab()
    bpe = None
    if args.bpe:
        from transformers import AutoTokenizer
        bpe = AutoTokenizer.from_pretrained(args.bpe)

    word_types = sorted({t for c in canon.values() for t in tokens(c) if is_bengali(t)})
    # single-token, Bengali-only keys: hyphenated compounds and Latin entries would be split /
    # re-predicted by `convert`, which would contaminate the collision metric
    lex_words = [w for w in load_lexicon()[0] if is_bengali(w)]
    n_word_tokens = sum(1 for c in canon.values() for t in tokens(c) if is_bengali(t))

    def mapping(rep: str, ws: list[str]) -> dict[str, set[str]]:
        m = collections.defaultdict(set)
        for w in ws:
            m[convert(rep, w, g2p=g2p, already_normalized=True).text].add(w)
        return m

    args.out.mkdir(parents=True, exist_ok=True)
    results = {}
    for rep in REP_IDS:
        conv = {u: convert(rep, c, g2p=g2p, already_normalized=True) for u, c in canon.items()}
        texts = {u: r.text for u, r in conv.items()}
        assert not any(OOV_MARK in t for t in texts.values()), rep
        chars = collections.Counter(ch for t in texts.values() for ch in t)
        n_chars = sum(chars.values())
        oov_syms = {c for c in chars if c not in vocab}
        slr_map = mapping(rep, word_types)
        lex_map = mapping(rep, lex_words) if rep in LEXICON_COLLISION_REPS else {}
        res = {
            "chars_per_utt": describe([len(t) for t in texts.values()]),
            "chars_per_word": describe([len(w) for t in texts.values() for w in t.split()]),
            "chars_per_speech_sec": describe([len(texts[u]) / speech[u] for u in texts]),
            "unique_symbols": len(chars),
            "symbols_not_in_f5_vocab": sorted(oov_syms),
            "pct_chars_new_embedding": 100 * sum(chars[c] for c in oov_syms) / n_chars,
            "pct_non_ascii": 100 * sum(v for c, v in chars.items() if ord(c) > 127) / n_chars,
            "pct_word_tokens_g2p_filled": 100 * sum(len(r.oov) for r in conv.values()) / n_word_tokens,
            "slr37_types": len(word_types),
            "slr37_type_collisions": sum(len(v) - 1 for v in slr_map.values() if len(v) > 1),
            "lexicon_type_collisions": (sum(len(v) - 1 for v in lex_map.values() if len(v) > 1)
                                        if lex_map else None),
            "lexicon_collision_examples": ([sorted(v)[:3] for v in lex_map.values() if len(v) > 1][:5]
                                           if lex_map else []),
        }
        if bpe is not None:
            n_tok = [len(bpe(t, add_special_tokens=False)["input_ids"]) for t in texts.values()]
            n_words = [max(1, len(t.split())) for t in texts.values()]
            res["bpe_tokens_per_utt"] = describe(n_tok)
            res["bpe_tokens_per_word"] = statistics.mean(a / b for a, b in zip(n_tok, n_words))
            res["bpe_chars_per_token"] = n_chars / sum(n_tok)
        results[rep] = res
        with open(args.out / f"{rep}.tsv", "w", encoding="utf-8", newline="\n") as f:
            f.write("utt_id\ttext\n" + "".join(f"{u}\t{t}\n" for u, t in sorted(texts.items())))
        print(f"{rep:14s} chars/word {res['chars_per_word']['mean']:.2f}  new-emb {res['pct_chars_new_embedding']:.1f}%"
              f"  lex-collisions {res['lexicon_type_collisions']}", flush=True)

    ph = [phenomena(c) for c in canon.values()]
    phen = {k: sum(p[k] for p in ph) for k in ph[0]}
    (args.out / "summary.json").write_text(json.dumps({"reps": results, "phenomena_totals": phen},
                                                      ensure_ascii=False, indent=2), encoding="utf-8")

    hdr = ["rep", "chars/word", "chars/utt", "chars/speech-s", "unique syms", "% chars new emb.", "% non-ASCII",
           "% words via G2P", "SLR37 type collisions", "lexicon type collisions"]
    if bpe is not None:
        hdr += ["BPE tok/word", "BPE chars/tok"]
    lines = ["# Phase 4: representation benchmark (text only, SLR37 bn_bd, 1,891 utterances)", "",
             f"G2P for out-of-lexicon words: `{args.g2p.as_posix()}`"
             + (f"; BPE tokenizer: `{args.bpe}`" if bpe is not None else "") + ".", "",
             "| " + " | ".join(hdr) + " |", "|" + "---|" * len(hdr)]
    for rep, r in results.items():
        row = [rep, f"{r['chars_per_word']['mean']:.2f}", f"{r['chars_per_utt']['mean']:.1f}",
               f"{r['chars_per_speech_sec']['mean']:.2f}", str(r["unique_symbols"]),
               f"{r['pct_chars_new_embedding']:.1f}", f"{r['pct_non_ascii']:.1f}",
               f"{r['pct_word_tokens_g2p_filled']:.1f}", str(r["slr37_type_collisions"]),
               "—" if r["lexicon_type_collisions"] is None else str(r["lexicon_type_collisions"])]
        if bpe is not None:
            row += [f"{r['bpe_tokens_per_word']:.2f}", f"{r['bpe_chars_per_token']:.2f}"]
        lines.append("| " + " | ".join(row) + " |")
    lines += ["", "Collisions = distinct Bengali word types mapping to the same string (information lost). "
                  "For lexicon-based arms these are homophones by construction (e.g. nasal vowels are not transcribed).",
              "", "Collision examples (lexicon):", "",
              *[f"- {rep}: {r['lexicon_collision_examples']}" for rep, r in results.items()
                if r["lexicon_collision_examples"]],
              "", "Phenomenon totals over the corpus (canonical Bengali):", "",
              "| " + " | ".join(phen) + " |", "|" + "---|" * len(phen),
              "| " + " | ".join(str(v) for v in phen.values()) + " |"]
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
