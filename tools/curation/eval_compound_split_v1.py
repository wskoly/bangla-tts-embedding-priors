"""Does two-part compound lookup beat G2P v1 on held-out lexicon words? (D-014)

Reproduces the G2P v1 word split (seed 20261006), builds a train-only dictionary, and on the
test words where `compound_lookup` fires, compares exact-match accuracy of compound vs G2P.

Usage: python tools/curation/eval_compound_split_v1.py
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.bnrep.g2p.model import G2P, tokens_to_pron  # noqa: E402
from src.bnrep.g2p.train import SEED, load_pairs  # noqa: E402
from src.bnrep.lexicon import compound_lookup, parse_pron  # noqa: E402


def flat(pron):
    return [x for s in pron for x in s]


def main() -> int:
    pairs = load_pairs()
    random.Random(SEED).shuffle(pairs)
    n = len(pairs)
    train, test = pairs[: int(.9 * n)], pairs[int(.95 * n):]
    table = {w: parse_pron(" ".join(p)) for w, p in train}
    g2p = G2P(ROOT / "runs/g2p/v1")
    hits = [(w, parse_pron(" ".join(p)), compound_lookup(w, table)) for w, p in test]
    hits = [(w, ref, comp) for w, ref, comp in hits if comp is not None]
    preds = g2p.predict_tokens([w for w, _, _ in hits])
    comp_ok = sum(flat(c) == flat(r) for _, r, c in hits)
    g2p_ok = sum(flat(tokens_to_pron(t)) == flat(r) for (_, r, _), t in zip(hits, preds))
    sys.stdout.reconfigure(encoding="utf-8")
    print(f"test words: {len(test)}; compound split fires on: {len(hits)}")
    print(f"exact match (ignoring syllable dots): compound {comp_ok}/{len(hits)} = {100 * comp_ok / max(1, len(hits)):.1f} %"
          f" | G2P {g2p_ok}/{len(hits)} = {100 * g2p_ok / max(1, len(hits)):.1f} %")
    print("compound misses (word | ref | compound):")
    for w, r, c in [h for h in hits if flat(h[2]) != flat(h[1])][:12]:
        print("  ", w, "|", " ".join(flat(r)), "|", " ".join(flat(c)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
