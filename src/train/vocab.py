"""Versioned, per-representation F5-TTS vocabularies with a mandatory zero-unknown assertion (D-016).

Tokenization used for EVERY arm, in training and in inference:
    tokens = list(text)            # one token per Unicode code point
    ids    = f5_tts.model.utils.list_str_to_idx([tokens], vocab_char_map)
F5's `convert_char_to_pinyin` (used by its prepare_csv_wavs.py and infer utils) is deliberately bypassed:
it inserts spurious spaces into Latin/IPA text (after "-" / "." and around IPA modifier letters) while
leaving Bengali untouched, which would confound the comparison.

Vocabulary = F5 v1 Base vocab (2,545 entries, original order, space at index 0) + the arm's new symbols
appended in sorted code-point order. Unknown symbols raise; nothing is silently mapped to index 0.

CLI: build + validate vocabularies for all arms over the frozen splits
    python -m src.train.vocab --reps BN-G,LAT-G-det,LAT-P,IPA-P --out configs/vocab --report docs/reports/vocab_v1.md
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import unicodedata
from importlib.resources import files
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
from src.corpus.profile import ALLOW_G2P, MANIFEST, SPLITS  # noqa: E402  (D-057 data profile)
SPLIT_NAMES = ["train_full", "val", "test_seen", "test_unseen"]  # train subsets are nested in train_full
TEXT_DIM = 512  # F5TTS_v1_Base text_dim; embedding rows = vocab_size + 1 (row 0 = filler)
VERSION = "v1"


class UnknownSymbolError(ValueError):
    pass


def base_vocab() -> list[str]:
    text = files("f5_tts").joinpath("infer/examples/vocab.txt").read_text(encoding="utf-8")
    vocab = text.split("\n")
    if vocab and vocab[-1] == "":
        vocab = vocab[:-1]
    assert vocab[0] == " " and len(vocab) == 2545, (len(vocab), repr(vocab[0]))
    return vocab


def tokenize(text: str) -> list[str]:
    return list(text)


def encode(text: str, vocab_map: dict[str, int]) -> list[int]:
    """Exact F5 path (list_str_to_idx) after verifying every symbol is known."""
    from f5_tts.model.utils import list_str_to_idx
    toks = tokenize(text)
    unknown = sorted({t for t in toks if t not in vocab_map})
    if unknown:
        raise UnknownSymbolError(f"unknown symbols {[(u, f'U+{ord(u):04X}') for u in unknown]} in {text!r}")
    return list_str_to_idx([toks], vocab_map)[0].tolist()


def split_texts(rep: str) -> dict[str, dict[str, str]]:
    from src.bnrep.reps import convert
    with open(MANIFEST, encoding="utf-8", newline="") as f:
        raw = {r["utt_id"]: r["text"] for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE)}
    out = {}
    for name in SPLIT_NAMES:
        with open(SPLITS / f"{name}.tsv", encoding="utf-8") as f:
            ids = [r["utt_id"] for r in csv.DictReader(f, delimiter="\t")]
        res = {u: convert(rep, raw[u]) for u in ids}
        bad = {u: r.oov for u, r in res.items() if r.oov}
        if bad and not ALLOW_G2P:  # C1 profile allows G2P for out-of-lexicon words (LAT-P only; reported separately)
            raise RuntimeError(f"{rep}/{name}: words needing G2P (SLR37 must be G2P-free): {list(bad.items())[:3]}")
        out[name] = {u: r.text for u, r in res.items()}
    return out


def build(rep: str, out_dir: Path) -> dict:
    base = base_vocab()
    texts = split_texts(rep)
    used = {c for split in texts.values() for t in split.values() for c in tokenize(t)}
    added = sorted(used - set(base), key=ord)
    vocab = base + added
    vocab_map = {s: i for i, s in enumerate(vocab)}
    assert len(vocab_map) == len(vocab), "duplicate vocab entries"

    # mandatory validation through the exact F5 encoding path, every split
    per_split = {}
    for name, split in texts.items():
        n_tok = 0
        for t in split.values():
            ids = encode(t, vocab_map)  # raises on any unknown symbol
            assert ids == [vocab_map[c] for c in t]
            n_tok += len(ids)
        per_split[name] = {"utterances": len(split), "tokens": n_tok, "unknown_symbols": 0}

    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{rep}_{VERSION}.txt"
    body = "\n".join(vocab) + "\n"
    path.write_text(body, encoding="utf-8", newline="\n")
    meta = {
        "rep": rep, "version": VERSION, "file": path.relative_to(ROOT).as_posix(),
        "sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
        "original_vocab_size": len(base), "final_vocab_size": len(vocab),
        "added_symbols": [{"symbol": s, "codepoint": f"U+{ord(s):04X}", "name": unicodedata.name(s, "?")} for s in added],
        "n_new_embeddings": len(added), "embedding_dim": TEXT_DIM,
        "embedding_rows": len(vocab) + 1, "symbols_used": len(used),
        "symbols_used_from_base": len(used & set(base)), "splits": per_split,
    }
    (out_dir / f"{rep}_{VERSION}.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return meta


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", required=True)
    ap.add_argument("--out", type=Path, default=ROOT / "configs/vocab")
    ap.add_argument("--report", type=Path, default=ROOT / "docs/reports/vocab_v1.md")
    args = ap.parse_args()
    metas = [build(r, args.out) for r in args.reps.split(",")]
    lines = ["# F5 vocabularies v1 (per representation)", "",
             "Tokenization: one token per code point via F5 `list_str_to_idx`; `convert_char_to_pinyin` bypassed "
             "(D-016). Every split validated: unknown symbols = 0 (enforced by exception).", "",
             "| rep | base size | added | final size | embedding rows × dim | new embeddings | symbols used (from base) | "
             "tokens train_full / val / test_seen / test_unseen | sha256 (first 12) |", "|---|---|---|---|---|---|---|---|---|"]
    for m in metas:
        s = m["splits"]
        lines.append(f"| {m['rep']} | {m['original_vocab_size']} | {len(m['added_symbols'])} | {m['final_vocab_size']} | "
                     f"{m['embedding_rows']} × {m['embedding_dim']} | {m['n_new_embeddings']} | "
                     f"{m['symbols_used']} ({m['symbols_used_from_base']}) | "
                     f"{s['train_full']['tokens']} / {s['val']['tokens']} / {s['test_seen']['tokens']} / "
                     f"{s['test_unseen']['tokens']} | `{m['sha256'][:12]}` |")
    lines += ["", "Added symbols per arm:", ""]
    for m in metas:
        lines.append(f"- **{m['rep']}**: " + (" ".join(f"{a['symbol']} ({a['codepoint']})" for a in m["added_symbols"])
                                              or "none"))
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[4:4 + len(metas) + 2]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
