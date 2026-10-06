"""Frozen fixed evaluation set + fixed reference prompts (D-017). Never re-selected after results exist.

Pre-registered rule (written before any synthesis):
  * 40 utterances from test_seen (primary) + 10 from test_unseen (secondary), text-disjoint from training.
  * Each candidate is tagged from its canonical Bengali text; tags are filled in a fixed order with
    fixed quotas; ties broken by sha256(utt_id + seed) (deterministic pseudo-random); speakers are
    rotated so no speaker dominates a tag.
  * Reference prompt per speaker: from `val` (or, for the unseen speaker, from test_unseen utterances not
    selected for evaluation): the utterance whose edge-trimmed speech duration is closest to 4.0 s among
    those whose words are all in the main Google lexicon and need no transcript correction.
  * The same eval utterances, reference audio and reference texts (converted per arm) are used for every arm.

Usage: python -m src.eval.fixed_set
"""

from __future__ import annotations

import collections
import csv
import hashlib
import json
from pathlib import Path

from src.bnrep.lexicon import load_lexicon, load_supplement
from src.bnrep.normalize import is_bengali, normalize, tokens

ROOT = Path(__file__).resolve().parents[2]
SPLITS = ROOT / "data/derived/splits/v1"
MANIFEST = ROOT / "data/derived/slr37_bn_bd/manifest.tsv"
OUT = ROOT / "data/derived/eval"
SEED = "20261006"
NUMBER_WORDS = set("এক দুই তিন চার পাঁচ ছয় সাত আট নয় দশ এগারো বারো তেরো চৌদ্দ পনেরো ষোল সতেরো আঠারো উনিশ বিশ "
                   "ত্রিশ চল্লিশ পঞ্চাশ ষাট সত্তর আশি নব্বই শত শো হাজার লক্ষ লাখ কোটি শূন্য দেড় আড়াই".split())
ASPIRATES, RETROFLEX = set("খঘছঝঠঢথধফভ"), set("টঠডঢণ")
QUOTAS_SEEN = [("supplement_word", 6), ("number", 5), ("conjunct_heavy", 6), ("aspirate_heavy", 5),
               ("retroflex_heavy", 4), ("nasal", 4), ("long", 2), ("ordinary", 8)]
QUOTAS_UNSEEN = [("supplement_word", 2), ("number", 2), ("conjunct_heavy", 2), ("aspirate_heavy", 2), ("ordinary", 2)]


def tags_of(text: str) -> set[str]:
    words = [t for t in tokens(normalize(text)) if is_bengali(t)]
    s = "".join(words)
    lex, supp = load_lexicon()[0], load_supplement()
    t = set()
    if any(w not in lex and w in supp for w in words):
        t.add("supplement_word")  # originally out-of-lexicon: mostly loanwords and proper names
    if any(w in NUMBER_WORDS for w in words) or "টায়" in s:
        t.add("number")
    if s.count("্") >= 3:
        t.add("conjunct_heavy")
    if sum(c in ASPIRATES for c in s) >= 4:
        t.add("aspirate_heavy")
    if sum(c in RETROFLEX for c in s) >= 4:
        t.add("retroflex_heavy")
    if "ঁ" in s or "ং" in s:
        t.add("nasal")
    if len(words) >= 12:
        t.add("long")
    if not t:
        t.add("ordinary")
    return t


def rank(uid: str) -> str:
    return hashlib.sha256((uid + SEED).encode()).hexdigest()


def select(cands: list[dict], quotas: list[tuple[str, int]]) -> list[dict]:
    chosen: dict[str, dict] = {}
    for tag, k in quotas:
        pool = sorted((c for c in cands if tag in c["tags"] and c["utt_id"] not in chosen),
                      key=lambda c: rank(c["utt_id"]))
        picked, spk_count = [], collections.Counter()
        while pool and len(picked) < k:  # rotate speakers: least-used speaker first
            best = min(pool, key=lambda c: (spk_count[c["speaker"]], rank(c["utt_id"])))
            pool.remove(best)
            picked.append(best)
            spk_count[best["speaker"]] += 1
        for c in picked:
            chosen[c["utt_id"]] = {**c, "selected_for": tag}
    return list(chosen.values())


def read_split(name: str) -> list[str]:
    with open(SPLITS / f"{name}.tsv", encoding="utf-8") as f:
        return [r["utt_id"] for r in csv.DictReader(f, delimiter="\t")]


def main() -> int:
    with open(MANIFEST, encoding="utf-8", newline="") as f:
        man = {r["utt_id"]: r for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE)}

    def cand(u):
        r = man[u]
        speech = float(r["duration_s"]) - float(r["lead_sil_s"]) - float(r["trail_sil_s"])
        return {"utt_id": u, "speaker": r["speaker"], "text": r["text"], "speech_s": speech, "tags": tags_of(r["text"])}

    seen = select([cand(u) for u in read_split("test_seen")], QUOTAS_SEEN)
    unseen_c = [cand(u) for u in read_split("test_unseen")]
    unseen = select(unseen_c, QUOTAS_UNSEEN)
    lex = load_lexicon()[0]

    def ref_ok(c):
        raw = normalize(c["text"], apply_corrections=False)
        words = [t for t in tokens(raw) if is_bengali(t)]
        return all(w in lex for w in words) and normalize(c["text"]) == raw

    refs = {}
    val = [cand(u) for u in read_split("val")]
    for spk in sorted({c["speaker"] for c in val}):
        pool = [c for c in val if c["speaker"] == spk and ref_ok(c)]
        refs[spk] = min(pool, key=lambda c: (abs(c["speech_s"] - 4.0), c["utt_id"]))
    sel_unseen = {c["utt_id"] for c in unseen}
    pool = [c for c in unseen_c if c["utt_id"] not in sel_unseen and ref_ok(c)]
    refs[unseen_c[0]["speaker"]] = min(pool, key=lambda c: (abs(c["speech_s"] - 4.0), c["utt_id"]))

    OUT.mkdir(parents=True, exist_ok=True)
    body = "utt_id\tspeaker\tsubset\tselected_for\ttags\tspeech_s\ttext\n" + "".join(
        f"{c['utt_id']}\t{c['speaker']}\t{sub}\t{c['selected_for']}\t{','.join(sorted(c['tags']))}\t"
        f"{c['speech_s']:.3f}\t{c['text']}\n"
        for sub, group in (("seen", seen), ("unseen", unseen)) for c in sorted(group, key=lambda c: c["utt_id"]))
    (OUT / "fixed_v1.tsv").write_text(body, encoding="utf-8", newline="\n")
    rbody = "speaker\tref_utt_id\tspeech_s\ttext\n" + "".join(
        f"{s}\t{c['utt_id']}\t{c['speech_s']:.3f}\t{c['text']}\n" for s, c in sorted(refs.items()))
    (OUT / "refs_v1.tsv").write_text(rbody, encoding="utf-8", newline="\n")
    meta = {"fixed_v1_sha256": hashlib.sha256(body.encode()).hexdigest(),
            "refs_v1_sha256": hashlib.sha256(rbody.encode()).hexdigest(),
            "n_seen": len(seen), "n_unseen": len(unseen), "seed": SEED,
            "quotas_seen": QUOTAS_SEEN, "quotas_unseen": QUOTAS_UNSEEN}
    (OUT / "fixed_v1.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    group = seen + unseen
    print(json.dumps(meta, indent=1))
    print("selected_for:", dict(collections.Counter(c["selected_for"] for c in group)))
    print("speakers:", dict(collections.Counter(c["speaker"] for c in group)))
    print("tag coverage (any tag):", dict(collections.Counter(t for c in group for t in c["tags"])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
