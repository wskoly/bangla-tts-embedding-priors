"""Frozen train/val/test splits and nested training subsets for SLR37 bn_bd.

Design (docs/decisions.md D-008):
  * test_unseen : every utterance of one held-out speaker (default 01701).
  * Text-disjoint: a transcript (NFC) never appears in more than one of
    {train/val} vs {test_seen, test_unseen}. Other speakers' readings of a
    test_unseen text are moved to test_seen.
  * test_seen / val : whole text groups sampled per remaining speaker.
  * train_pool : the rest; nested subsets by edge-trimmed speech duration,
    speaker-stratified (proportional to each speaker's share of the pool).

Usage:
    python src/corpus/make_splits.py --manifest data/derived/slr37_bn_bd/manifest.tsv \
        --out-dir data/derived/splits/v1 --report docs/reports/splits_v1.md
"""

from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
import random
import sys
import unicodedata
from pathlib import Path

SEED = 20261006


def load(manifest: Path) -> list[dict]:
    with open(manifest, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE))
    for r in rows:
        r["text_nfc"] = unicodedata.normalize("NFC", r["text"]).strip()
        r["speech_s"] = max(0.0, float(r["duration_s"]) - float(r["lead_sil_s"]) - float(r["trail_sil_s"]))
    return [r for r in rows if "unreadable" not in r["flags"] and "no_audio" not in r["flags"]]


def take_groups(rows: list[dict], n_per_speaker: int, rng: random.Random) -> set[str]:
    """Pick whole text groups until each speaker has >= n utterances in the selection."""
    by_text = collections.defaultdict(list)
    for r in rows:
        by_text[r["text_nfc"]].append(r)
    texts = sorted(by_text)
    rng.shuffle(texts)
    need = collections.Counter({s: n_per_speaker for s in {r["speaker"] for r in rows}})
    chosen: set[str] = set()
    for t in texts:
        spk = {r["speaker"] for r in by_text[t]}
        if any(need[s] > 0 for s in spk):
            chosen.add(t)
            for r in by_text[t]:
                need[r["speaker"]] -= 1
        if all(v <= 0 for v in need.values()):
            break
    return chosen


def nested_subsets(pool: list[dict], targets_h: list[float], rng: random.Random) -> dict[str, list[dict]]:
    by_spk = collections.defaultdict(list)
    for r in sorted(pool, key=lambda r: r["utt_id"]):
        by_spk[r["speaker"]].append(r)
    for s in sorted(by_spk):
        rng.shuffle(by_spk[s])
    total = sum(r["speech_s"] for r in pool)
    share = {s: sum(r["speech_s"] for r in v) / total for s, v in by_spk.items()}
    # Greedy interleave: always extend the speaker furthest below its proportional share.
    order, taken, ptr = [], collections.Counter(), collections.Counter()
    cum = 0.0
    while any(ptr[s] < len(v) for s, v in by_spk.items()):
        cands = sorted(s for s, v in by_spk.items() if ptr[s] < len(v))
        s = min(cands, key=lambda s: (taken[s] / max(cum, 1e-9)) - share[s])
        r = by_spk[s][ptr[s]]
        ptr[s] += 1
        taken[s] += r["speech_s"]
        cum += r["speech_s"]
        order.append(r)
    subsets = {}
    for h in targets_h:
        out, acc = [], 0.0
        for r in order:
            if acc >= h * 3600:
                break
            out.append(r)
            acc += r["speech_s"]
        if acc < h * 3600 * 0.98:
            print(f"note: target {h} h not reachable (pool {total / 3600:.3f} h speech); skipped", file=sys.stderr)
            continue
        subsets[f"train_{h:g}h"] = out
    subsets["train_full"] = order
    return subsets


def write(rows: list[dict], path: Path) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = sorted(rows, key=lambda r: r["utt_id"])
    body = "utt_id\tspeaker\tspeech_s\tduration_s\n" + "".join(
        f"{r['utt_id']}\t{r['speaker']}\t{r['speech_s']:.3f}\t{float(r['duration_s']):.3f}\n" for r in rows)
    path.write_text(body, encoding="utf-8", newline="\n")
    return hashlib.sha256(body.encode()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--report", type=Path, required=True)
    ap.add_argument("--unseen-speaker", default="01701")
    ap.add_argument("--test-per-speaker", type=int, default=30)
    ap.add_argument("--val-per-speaker", type=int, default=10)
    ap.add_argument("--targets-h", default="0.25,0.5,1.0,2.0")
    args = ap.parse_args()
    rng = random.Random(SEED)

    rows = load(args.manifest)
    unseen = [r for r in rows if r["speaker"] == args.unseen_speaker]
    unseen_texts = {r["text_nfc"] for r in unseen}
    rest = [r for r in rows if r["speaker"] != args.unseen_speaker]

    # other speakers reading a test_unseen text -> test_seen (keeps train text-disjoint)
    forced_seen = [r for r in rest if r["text_nfc"] in unseen_texts]
    rest = [r for r in rest if r["text_nfc"] not in unseen_texts]

    seen_texts = take_groups(rest, args.test_per_speaker, rng)
    test_seen = forced_seen + [r for r in rest if r["text_nfc"] in seen_texts]
    rest = [r for r in rest if r["text_nfc"] not in seen_texts]

    val_texts = take_groups(rest, args.val_per_speaker, rng)
    val = [r for r in rest if r["text_nfc"] in val_texts]
    pool = [r for r in rest if r["text_nfc"] not in val_texts]

    def texts(rs):
        return {r["text_nfc"] for r in rs}

    # invariants
    assert not texts(pool) & (texts(test_seen) | texts(unseen) | texts(val)), "train text leak"
    assert not texts(val) & (texts(test_seen) | texts(unseen)), "val/test text leak"
    ids = [r["utt_id"] for part in (pool, val, test_seen, unseen) for r in part]
    assert len(ids) == len(set(ids)) == len(rows), "split is not a partition"

    targets = [float(x) for x in args.targets_h.split(",")]
    splits = {"test_unseen": unseen, "test_seen": test_seen, "val": val, **nested_subsets(pool, targets, rng)}
    hashes = {name: write(rs, args.out_dir / f"{name}.tsv") for name, rs in splits.items()}

    def stat(rs):
        spk = collections.Counter(r["speaker"] for r in rs)
        return {"utts": len(rs), "speech_h": sum(r["speech_s"] for r in rs) / 3600,
                "raw_h": sum(float(r["duration_s"]) for r in rs) / 3600,
                "speakers": dict(sorted(spk.items())), "unique_texts": len(texts(rs))}

    summary = {"seed": SEED, "unseen_speaker": args.unseen_speaker, "manifest": str(args.manifest),
               "splits": {k: stat(v) for k, v in splits.items()}, "sha256": hashes}
    (args.out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    lines = ["# Splits v1 (SLR37 bn_bd)", "",
             f"Seed {SEED}; unseen speaker `{args.unseen_speaker}`; text-disjoint across train/val vs test; "
             "durations are edge-trimmed speech (raw = file length).", "",
             "| split | utts | speech h | raw h | unique texts | per-speaker utts |", "|---|---|---|---|---|---|"]
    for k, v in summary["splits"].items():
        lines.append(f"| {k} | {v['utts']} | {v['speech_h']:.3f} | {v['raw_h']:.3f} | {v['unique_texts']} | {v['speakers']} |")
    lines += ["", "Nested: every smaller train subset is a prefix of the next (same audio for every representation arm).",
              "", "SHA-256 of split files:", "", *[f"- `{k}`: `{h}`" for k, h in hashes.items()]]
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    print("\n".join(lines[4:6 + len(splits)]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
