"""C1 (D-057): build the rasa_bn_v1 data profile, following docs/C1_data_rules.md (fixed before download).

Steps: select rows from the metadata survey (data/raw/rasa_bn/meta.tsv) -> download only the needed shards
-> raw wavs + manifest -> 24 kHz trimmed audio + index -> splits -> fixed eval set + references -> coverage report.
Usage: python -I tools/c1_rasa_build.py [--keep-parquet]
"""

from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import io
import json
import os
import re
import sys
import unicodedata
from pathlib import Path

import numpy as np
import pyarrow.parquet as pq
import soundfile as sf
import torch
import torchaudio.functional as AF
from huggingface_hub import hf_hub_download

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ["DATA_PROFILE"] = "rasa_bn_v1"
from src.bnrep.normalize import is_bengali, normalize, tokens  # noqa: E402
from src.bnrep.reps import convert  # noqa: E402
from src.corpus.prep_audio import trim_bounds  # noqa: E402
from src.train.vocab import UnknownSymbolError, encode  # noqa: E402

SEED = "20261011"
RAW = ROOT / "data/raw/rasa_bn"
MAN_DIR, AUDIO_DIR = ROOT / "data/derived/rasa_bn", ROOT / "data/derived/audio24k_rasa_v1"
SPLITS, EVAL_DIR = ROOT / "data/derived/splits/rasa_v1", ROOT / "data/derived/eval_rasa_v1"
REPORT = ROOT / "docs/reports/c1_rasa_data_v1.md"
NEUTRAL = {"ALEXA", "BB", "BOOK", "CONV", "DIGI", "INDIC", "NEWS", "SANGRAH", "UMANG", "WIKI"}
SEEN, UNSEEN = "Female", "Male"
SPK = {"Female": "rasaF", "Male": "rasaM"}
SEEN_TEST_SHARD, UNSEEN_TEST_SHARD = "test-00004-of-00007.parquet", "test-00000-of-00007.parquet"
N_SEEN, N_UNSEEN, N_VAL, TRAIN_H = 160, 110, 50, 1.0
REPS = ["LAT-P", "LAT-P-rand", "LAT-G-det", "LAT-G-asp", "BN-G", "BN-G-iv", "BN-G-iv-vm", "BN-G-iv-vm-asp"]
TARGET_SR = 24000
VOCABS: dict[str, dict[str, int]] = {}


def clean_text(t: str) -> str:
    """docs/C1_data_rules.md text rule, steps 1-3 (normalize() runs later in every consumer)."""
    t = t.replace("৷", "।")
    t = re.sub("[​﻿'\"‘’“”()]", "", t)
    t = t.replace("-", " ")
    t = re.sub("[,;:?!]", ".", t)
    t = re.sub(r"\s*\.(\s*[.।])+", ".", t)  # collapse runs such as ". ." produced by the mapping
    return re.sub(r"\s+", " ", t).strip()


def admissible(t: str) -> bool:
    """Step 5: no digits / Latin letters; every arm encodes with its frozen v1 vocabulary."""
    if re.search(r"[0-9০-৯A-Za-z]", t):
        return False
    for rep in REPS:
        if rep not in VOCABS:
            syms = (ROOT / f"configs/vocab/{rep}_v1.txt").read_text(encoding="utf-8").split("\n")
            VOCABS[rep] = {s: i for i, s in enumerate(syms) if s or i == 0}
        try:
            encode(convert(rep, t).text, VOCABS[rep])
        except (UnknownSymbolError, AssertionError, KeyError):  # converters assert on symbols outside their inventory
            return False
    return True


def h(name: str) -> str:
    return hashlib.sha256((name + SEED).encode()).hexdigest()


def silence_edges(x: np.ndarray, sr: int) -> tuple[float, float]:
    """Leading / trailing silence (s) by the -40 dBFS / 20 ms rule, without margin (as slr37_stats)."""
    hop = int(sr * 0.02)
    n = len(x) // hop
    db = 20 * np.log10(np.sqrt((x[: n * hop].reshape(n, hop) ** 2).mean(axis=1)) + 1e-12)
    v = np.where(db > -40.0)[0]
    if v.size == 0:
        return len(x) / sr, 0.0
    return v[0] * hop / sr, (len(x) - (v[-1] + 1) * hop) / sr


def attach_audio(c: dict, audio: tuple[np.ndarray, int]) -> None:
    c["_audio"] = audio
    c["lead"], c["trail"] = silence_edges(*audio)
    c["speech_s"] = max(0.0, len(audio[0]) / audio[1] - c["lead"] - c["trail"])


def load_shard(shard: str, wanted: set[str]) -> dict[str, tuple[np.ndarray, int]]:
    print(f"download {shard}", flush=True)
    p = hf_hub_download("ai4bharat/Rasa", f"Bengali/{shard}", repo_type="dataset", local_dir=RAW / "parquet")
    out = {}
    pf = pq.ParquetFile(p)
    for rg in range(pf.num_row_groups):
        for r in pf.read_row_group(rg, columns=["filename", "audio"]).to_pylist():
            if r["filename"] in wanted:
                x, sr = sf.read(io.BytesIO(r["audio"]["bytes"]), dtype="float32", always_2d=True)
                out[r["filename"]] = (x.mean(axis=1), sr)
    assert set(out) == wanted, f"{shard}: missing {sorted(wanted - set(out))[:3]}"
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--keep-parquet", action="store_true")
    args = ap.parse_args()
    with open(RAW / "meta.tsv", encoding="utf-8", newline="") as f:
        meta = list(csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE))
    assert len(meta) == 28086 + 3123, f"survey incomplete: {len(meta)} rows"
    shard_genders = collections.defaultdict(set)
    for m in meta:
        shard_genders[m["shard"]].add(m["gender"])
    excl, cand = collections.Counter(), []
    for r in meta:
        if r["style"] not in NEUTRAL:
            excl["emotion style"] += 1
            continue
        if not 1.0 <= float(r["duration"]) <= 15.0:
            excl["duration outside 1-15 s"] += 1
            continue
        t = clean_text(r["text"])
        if not t or not admissible(t):
            excl["text rule (digits / Latin / out-of-vocab)"] += 1
            continue
        cand.append({**r, "clean": t, "nfc": unicodedata.normalize("NFC", normalize(t))})
    print(f"candidates {len(cand)}; excluded {dict(excl)}", flush=True)

    def by(pred):
        return sorted((c for c in cand if pred(c)), key=lambda c: h(c["filename"]))

    test_seen = by(lambda c: c["shard"] == SEEN_TEST_SHARD and c["gender"] == SEEN)[:N_SEEN]
    test_unseen = by(lambda c: c["shard"] == UNSEEN_TEST_SHARD and c["gender"] == UNSEEN)[:N_UNSEEN]
    assert len(test_seen) == N_SEEN and len(test_unseen) == N_UNSEEN
    female_train = sorted(s for s, g in shard_genders.items() if s.startswith("train-") and g == {SEEN})

    used_texts = {c["nfc"] for c in test_seen + test_unseen}
    val, train, train_s, shards_used = [], [], 0.0, []
    for shard in female_train:  # add shards in name order until val + 1 h of trimmed speech
        if len(val) == N_VAL and train_s >= TRAIN_H * 3600:
            break
        shards_used.append(shard)
        rows = by(lambda c, s=shard: c["shard"] == s)
        audio = load_shard(shard, {c["filename"] for c in rows})
        for c in rows:
            if len(val) == N_VAL and train_s >= TRAIN_H * 3600:
                break
            if c["nfc"] in used_texts:
                excl["text overlaps test / val / train"] += 1
                continue
            attach_audio(c, audio[c["filename"]])
            if len(val) < N_VAL:
                val.append(c)
            else:
                train.append(c)
                train_s += c["speech_s"]
            used_texts.add(c["nfc"])
    assert len(val) == N_VAL and train_s >= TRAIN_H * 3600, (len(val), train_s)
    for shard, group in ((SEEN_TEST_SHARD, test_seen), (UNSEEN_TEST_SHARD, test_unseen)):
        shards_used.append(shard)
        audio = load_shard(shard, {c["filename"] for c in group})
        for c in group:
            attach_audio(c, audio[c["filename"]])

    splits = {"test_seen": test_seen, "test_unseen": test_unseen, "val": val, "train_1h": train}
    write_all(splits)
    report(splits, excl, shards_used, len(cand))
    if not args.keep_parquet:
        for p in (RAW / "parquet").rglob("*.parquet"):
            p.unlink()
    return 0


def write_all(splits: dict) -> None:
    wav_dir = RAW / "wavs"
    for d in (wav_dir, MAN_DIR, AUDIO_DIR, SPLITS, EVAL_DIR):
        d.mkdir(parents=True, exist_ok=True)
    man = ["utt_id\tspeaker\tpath\tsample_rate\tchannels\tsubtype\tduration_s\tpeak\tclip_frac\trms_dbfs\t"
           "lead_sil_s\ttrail_sil_s\tflags\ttext"]
    idx = ["utt_id\tpath\tduration_s\ttrimmed_lead_s\ttrimmed_trail_s"]
    for c in sorted((c for rows in splits.values() for c in rows), key=lambda c: c["filename"]):
        u, (x, sr) = c["filename"], c["_audio"]
        raw = wav_dir / f"{u}.wav"
        sf.write(raw, np.clip(x, -1, 1), sr, subtype="PCM_16")
        rms = 20 * np.log10(np.sqrt((x ** 2).mean()) + 1e-12)
        man.append(f"{u}\t{SPK[c['gender']]}\t{raw.relative_to(ROOT).as_posix()}\t{sr}\t1\tPCM_16\t{len(x) / sr:.4f}\t"
                   f"{float(np.abs(x).max()):.4f}\t{float((np.abs(x) >= 0.999).mean()):.4f}\t{rms:.4f}\t"
                   f"{c['lead']:.4f}\t{c['trail']:.4f}\tstyle={c['style']}\t{c['clean']}")
        s, e = trim_bounds(x, sr)
        y = np.clip(AF.resample(torch.from_numpy(x[s:e].copy()), sr, TARGET_SR).numpy(), -1.0, 1.0)
        out = AUDIO_DIR / f"{u}.wav"
        sf.write(out, y, TARGET_SR, subtype="PCM_16")
        idx.append(f"{u}\t{out.relative_to(ROOT).as_posix()}\t{len(y) / TARGET_SR:.4f}\t{s / sr:.4f}\t{(len(x) - e) / sr:.4f}")
    (MAN_DIR / "manifest.tsv").write_text("\n".join(man) + "\n", encoding="utf-8")
    (AUDIO_DIR / "index.tsv").write_text("\n".join(idx) + "\n", encoding="utf-8")
    for name, rows in {**splits, "train_full": splits["train_1h"]}.items():  # vocab.py expects train_full
        body = ["utt_id\tspeaker\tspeech_s\tduration_s"] + [
            f"{c['filename']}\t{SPK[c['gender']]}\t{c['speech_s']:.3f}\t{float(c['duration']):.3f}" for c in rows]
        (SPLITS / f"{name}.tsv").write_text("\n".join(body) + "\n", encoding="utf-8")
    seen, unseen = splits["test_seen"][:40], splits["test_unseen"][:10]  # fixed set: curves only
    fixed = ["utt_id\tspeaker\tsubset\tselected_for\ttags\tspeech_s\ttext"] + [
        f"{c['filename']}\t{SPK[c['gender']]}\t{sub}\thash_order\t-\t{c['speech_s']:.3f}\t{c['clean']}"
        for sub, grp in (("seen", seen), ("unseen", unseen)) for c in grp]
    fixed_ids = {c["filename"] for c in seen + unseen}
    refs = ["speaker\tref_utt_id\tspeech_s\ttext"]
    for g, pool in ((SEEN, splits["val"]),
                    (UNSEEN, [c for c in splits["test_unseen"] if c["filename"] not in fixed_ids])):
        ok = [c for c in pool if not convert("LAT-P", c["clean"], g2p=None).oov]  # all words in lexicon/supplement
        best = min(ok, key=lambda c: (abs(c["speech_s"] - 4.0), h(c["filename"])))
        refs.append(f"{SPK[g]}\t{best['filename']}\t{best['speech_s']:.3f}\t{best['clean']}")
    (EVAL_DIR / "fixed_v1.tsv").write_text("\n".join(fixed) + "\n", encoding="utf-8")
    (EVAL_DIR / "refs_v1.tsv").write_text("\n".join(refs) + "\n", encoding="utf-8")


def report(splits: dict, excl: collections.Counter, shards: list[str], n_cand: int) -> None:
    lines = ["# C1 Rasa Bengali data (rasa_bn_v1, D-057)", "",
             "Built by `tools/c1_rasa_build.py` under `docs/C1_data_rules.md` (rules fixed before download).", "",
             f"- Shards downloaded: {', '.join(shards)}.",
             f"- Neutral candidates after filters: {n_cand}. Exclusions: {dict(excl)}.", "",
             "| split | speaker | utts | trimmed speech h | raw h |", "|---|---|---|---|---|"]
    for name, rows in splits.items():
        lines.append(f"| {name} | {', '.join(sorted({SPK[c['gender']] for c in rows}))} | {len(rows)} | "
                     f"{sum(c['speech_s'] for c in rows) / 3600:.3f} | {sum(float(c['duration']) for c in rows) / 3600:.3f} |")
    lines += ["", "## LAT-P lexicon coverage (lexicon + supplement; the rest via G2P v1)", "",
              "| split | tokens | token coverage % | types | type coverage % | utts fully covered |",
              "|---|---|---|---|---|---|"]
    cov = {}
    for name, rows in splits.items():
        toks, oov, full = [], [], 0
        for c in rows:
            toks += [w for w in tokens(normalize(c["clean"])) if is_bengali(w)]
            o = convert("LAT-P", c["clean"], g2p=None).oov
            oov += o
            full += not o
        cov[name] = {"token_cov": 100 * (1 - len(oov) / len(toks)), "type_cov": 100 * (1 - len(set(oov)) / len(set(toks))),
                     "fully_covered_utts": full, "utts": len(rows)}
        lines.append(f"| {name} | {len(toks)} | {cov[name]['token_cov']:.1f} | {len(set(toks))} | "
                     f"{cov[name]['type_cov']:.1f} | {full} / {len(rows)} |")
    met = min(cov["test_seen"]["token_cov"], cov["test_unseen"]["token_cov"]) >= 85
    lines += ["", "Go/no-go criterion (D-055): LAT-P test token coverage ≥ 85 %: " + ("met" if met else "**not met**")
              + ". The ASR floor is measured separately."]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    (MAN_DIR / "build_summary.json").write_text(json.dumps({"shards": shards, "coverage": cov, "excluded": dict(excl)},
                                                           indent=2), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    raise SystemExit(main())
