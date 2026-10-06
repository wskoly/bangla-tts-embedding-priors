"""Exact statistics for an extracted OpenSLR SLR37 subset (e.g. bn_bd).

Computes everything from the files on disk; no secondary-source numbers.

Usage:
    python src/corpus/slr37_stats.py --root data/raw/slr37/bn_bd \
        --out-dir data/derived/slr37 --report docs/reports/slr37_bn_bd_stats.md \
        [--google-prompts path/to/prompts.tsv]

Outputs:
    <out-dir>/manifest.tsv   one row per utterance (id, speaker, path, audio props, text, flags)
    <out-dir>/speakers.tsv   per-speaker utterance count and minutes
    <out-dir>/summary.json   machine-readable summary
    <report>                 human-readable markdown report
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import statistics
import sys
import unicodedata
from dataclasses import asdict, dataclass, field
from pathlib import Path

import numpy as np
import soundfile as sf

BENGALI_BLOCK = (0x0980, 0x09FF)
CLIP_LEVEL = 0.999          # |sample| at or above this counts as clipped
SILENCE_DBFS = -40.0        # frame RMS below this (relative to full scale) counts as silence
FRAME_MS = 20


@dataclass
class Utt:
    utt_id: str
    speaker: str
    path: str
    text: str = ""
    sample_rate: int = 0
    channels: int = 0
    subtype: str = ""
    n_frames: int = 0
    duration_s: float = 0.0
    peak: float = 0.0
    clip_frac: float = 0.0
    rms_dbfs: float = 0.0
    lead_sil_s: float = 0.0
    trail_sil_s: float = 0.0
    read_error: str = ""
    flags: list[str] = field(default_factory=list)


def speaker_of(utt_id: str) -> str:
    # Google crowdsourced corpora name files <lang>_<speaker>_<utt>; fall back to the full id.
    parts = utt_id.split("_")
    return parts[1] if len(parts) >= 3 else utt_id


def read_transcripts(root: Path) -> dict[str, str]:
    texts: dict[str, str] = {}
    for tsv in sorted(root.rglob("*.tsv")):
        for line in tsv.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            cols = line.split("\t")
            if len(cols) < 2:
                continue
            texts[cols[0].strip()] = cols[-1].strip()
    return texts


def audio_props(u: Utt) -> None:
    try:
        x, sr = sf.read(u.path, dtype="float32", always_2d=True)
        info = sf.info(u.path)
    except Exception as e:  # unreadable file is a finding, not a crash
        u.read_error = f"{type(e).__name__}: {e}"
        u.flags.append("unreadable")
        return
    u.sample_rate, u.channels, u.subtype = sr, x.shape[1], info.subtype
    u.n_frames = x.shape[0]
    u.duration_s = u.n_frames / sr
    mono = x.mean(axis=1)
    if mono.size == 0:
        u.flags.append("empty")
        return
    u.peak = float(np.abs(mono).max())
    u.clip_frac = float((np.abs(x) >= CLIP_LEVEL).mean())
    u.rms_dbfs = float(20 * np.log10(np.sqrt(np.mean(mono**2)) + 1e-12))
    hop = max(1, int(sr * FRAME_MS / 1000))
    n = len(mono) // hop
    if n:
        frames = mono[: n * hop].reshape(n, hop)
        db = 20 * np.log10(np.sqrt((frames**2).mean(axis=1)) + 1e-12)
        voiced = np.where(db > SILENCE_DBFS)[0]
        if voiced.size == 0:
            u.flags.append("all_silent")
        else:
            u.lead_sil_s = voiced[0] * hop / sr
            u.trail_sil_s = (n - 1 - voiced[-1]) * hop / sr


def text_profile(text: str) -> dict:
    nfc = unicodedata.normalize("NFC", text)
    chars = collections.Counter(nfc)
    beng = sum(c for ch, c in chars.items() if BENGALI_BLOCK[0] <= ord(ch) <= BENGALI_BLOCK[1])
    return {
        "nfc_changed": nfc != text,
        "n_chars": len(nfc),
        "n_words": len(nfc.split()),
        "bengali_chars": beng,
        "latin_chars": sum(c for ch, c in chars.items() if ch.isascii() and ch.isalpha()),
        "ascii_digits": sum(c for ch, c in chars.items() if ch.isascii() and ch.isdigit()),
        "bengali_digits": sum(c for ch, c in chars.items() if 0x09E6 <= ord(ch) <= 0x09EF),
        "zw_chars": sum(c for ch, c in chars.items() if ch in "‌‍"),
        "punct": sum(c for ch, c in chars.items() if unicodedata.category(ch).startswith("P")),
    }


def describe(values: list[float]) -> dict:
    if not values:
        return {}
    v = sorted(values)

    def q(p: float) -> float:
        return v[min(len(v) - 1, int(p * (len(v) - 1)))]

    return {"n": len(v), "sum": sum(v), "mean": statistics.mean(v), "sd": statistics.pstdev(v),
            "min": v[0], "p05": q(0.05), "median": q(0.5), "p95": q(0.95), "max": v[-1]}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--report", type=Path, required=True)
    ap.add_argument("--google-prompts", type=Path)
    args = ap.parse_args()

    texts = read_transcripts(args.root)
    wavs = {p.stem: p for p in sorted(args.root.rglob("*.wav"))}
    ids = sorted(set(texts) | set(wavs))

    utts: list[Utt] = []
    for i, uid in enumerate(ids):
        u = Utt(utt_id=uid, speaker=speaker_of(uid), path=str(wavs.get(uid, "")), text=texts.get(uid, ""))
        if uid not in wavs:
            u.flags.append("no_audio")
        else:
            audio_props(u)
        if uid not in texts:
            u.flags.append("no_transcript")
        utts.append(u)
        if (i + 1) % 500 == 0:
            print(f"  processed {i + 1}/{len(ids)}", file=sys.stderr)

    by_id = {u.utt_id: u for u in utts}
    ok = [u for u in utts if not u.read_error and "no_audio" not in u.flags]
    durs = [u.duration_s for u in ok]

    # duration / level outliers relative to this corpus (documented, not removed here)
    if durs:
        lo, hi = np.percentile(durs, [0.5, 99.5])
        for u in ok:
            if u.duration_s < lo:
                u.flags.append("dur_low_tail")
            if u.duration_s > hi:
                u.flags.append("dur_high_tail")
            if u.clip_frac > 0.001:
                u.flags.append("clipping")
            if u.lead_sil_s > 1.0 or u.trail_sil_s > 1.0:
                u.flags.append("long_edge_silence")

    # transcripts
    profiles = {u.utt_id: text_profile(u.text) for u in utts if u.text}
    norm_text = {u.utt_id: unicodedata.normalize("NFC", u.text).strip() for u in utts if u.text}
    by_text = collections.defaultdict(list)
    for uid, t in norm_text.items():
        by_text[t].append(uid)
    dup_groups = {t: v for t, v in by_text.items() if len(v) > 1}
    cross_speaker_dups = {t: v for t, v in dup_groups.items() if len({speaker_of(x) for x in v}) > 1}
    for v in dup_groups.values():
        for uid in v:
            by_id[uid].flags.append("dup_text")

    # speakers
    spk = collections.defaultdict(lambda: {"utts": 0, "dur_s": 0.0})
    for u in ok:
        spk[u.speaker]["utts"] += 1
        spk[u.speaker]["dur_s"] += u.duration_s

    # overlap with Google prompts.tsv (if given)
    overlap = {}
    if args.google_prompts and args.google_prompts.exists():
        google = {}
        for line in args.google_prompts.read_text(encoding="utf-8").splitlines():
            if line.startswith("#") or "\t" not in line:
                continue
            k, v = line.split("\t", 1)
            google[k.strip()] = unicodedata.normalize("NFC", v.strip())
        ids_in = [k for k in google if k in norm_text]
        gtexts = set(google.values())
        overlap = {
            "google_prompts": len(google),
            "ids_in_slr37": len(ids_in),
            "same_text_for_shared_ids": sum(1 for k in ids_in if google[k] == norm_text[k]),
            "slr37_unique_texts_in_google": sum(1 for t in set(norm_text.values()) if t in gtexts),
        }

    meta_files = sorted(str(p.relative_to(args.root)) for p in args.root.rglob("*")
                        if p.is_file() and p.suffix.lower() != ".wav")

    summary = {
        "root": str(args.root),
        "non_wav_files": meta_files,
        "n_ids": len(ids),
        "n_wav": len(wavs),
        "n_transcripts": len(texts),
        "n_no_audio": sum("no_audio" in u.flags for u in utts),
        "n_no_transcript": sum("no_transcript" in u.flags for u in utts),
        "n_unreadable": sum(bool(u.read_error) for u in utts),
        "total_hours": sum(durs) / 3600,
        "duration_s": describe(durs),
        "sample_rates": dict(collections.Counter(u.sample_rate for u in ok)),
        "channels": dict(collections.Counter(u.channels for u in ok)),
        "subtypes": dict(collections.Counter(u.subtype for u in ok)),
        "peak": describe([u.peak for u in ok]),
        "rms_dbfs": describe([u.rms_dbfs for u in ok]),
        "lead_sil_s": describe([u.lead_sil_s for u in ok]),
        "trail_sil_s": describe([u.trail_sil_s for u in ok]),
        "flag_counts": dict(collections.Counter(f for u in utts for f in u.flags)),
        "n_speakers": len(spk),
        "speaker_utts": describe([s["utts"] for s in spk.values()]),
        "speaker_minutes": describe([s["dur_s"] / 60 for s in spk.values()]),
        "chars_per_utt": describe([p["n_chars"] for p in profiles.values()]),
        "words_per_utt": describe([p["n_words"] for p in profiles.values()]),
        "chars_per_sec": describe([profiles[u.utt_id]["n_chars"] / u.duration_s
                                   for u in ok if u.utt_id in profiles and u.duration_s > 0]),
        "text_flags": {k: sum(1 for p in profiles.values() if p[k]) for k in
                       ["nfc_changed", "latin_chars", "ascii_digits", "bengali_digits", "zw_chars", "punct"]},
        "unique_texts": len(by_text),
        "dup_text_groups": len(dup_groups),
        "dup_text_utts": sum(len(v) for v in dup_groups.values()),
        "cross_speaker_dup_groups": len(cross_speaker_dups),
        "google_prompts_overlap": overlap,
        "transcript_sha256": hashlib.sha256(
            "\n".join(f"{k}\t{texts[k]}" for k in sorted(texts)).encode()).hexdigest(),
    }

    args.out_dir.mkdir(parents=True, exist_ok=True)
    cols = ["utt_id", "speaker", "path", "sample_rate", "channels", "subtype", "duration_s", "peak",
            "clip_frac", "rms_dbfs", "lead_sil_s", "trail_sil_s", "flags", "text"]
    with open(args.out_dir / "manifest.tsv", "w", encoding="utf-8", newline="\n") as f:
        f.write("\t".join(cols) + "\n")
        for u in utts:
            d = asdict(u)
            d["flags"] = ",".join(u.flags)
            f.write("\t".join(f"{d[c]:.4f}" if isinstance(d[c], float) else str(d[c]) for c in cols) + "\n")
    (args.out_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    (args.out_dir / "speakers.tsv").write_text(
        "speaker\tutts\tminutes\n" + "".join(f"{k}\t{v['utts']}\t{v['dur_s'] / 60:.2f}\n"
                                              for k, v in sorted(spk.items(), key=lambda kv: -kv[1]["dur_s"])),
        encoding="utf-8")
    write_report(args.report, summary, spk, cross_speaker_dups)
    print(json.dumps({k: summary[k] for k in ["n_wav", "n_transcripts", "total_hours", "n_speakers"]}, indent=2))
    return 0


def fmt(d: dict, unit: str = "", nd: int = 2) -> str:
    if not d:
        return "—"
    return (f"mean {d['mean']:.{nd}f}{unit} (sd {d['sd']:.{nd}f}); median {d['median']:.{nd}f}; "
            f"min {d['min']:.{nd}f}; p05 {d['p05']:.{nd}f}; p95 {d['p95']:.{nd}f}; max {d['max']:.{nd}f}")


def write_report(path: Path, s: dict, spk: dict, xdups: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    top = sorted(spk.items(), key=lambda kv: -kv[1]["dur_s"])
    tf = s["text_flags"]
    lines = [
        "# SLR37 statistics (computed from files on disk)", "",
        f"Root: `{s['root']}`  ", f"Transcript SHA-256: `{s['transcript_sha256']}`", "",
        "| Quantity | Value |", "|---|---|",
        f"| Utterance ids (audio ∪ transcript) | {s['n_ids']} |",
        f"| WAV files | {s['n_wav']} |",
        f"| Transcript lines | {s['n_transcripts']} |",
        f"| Audio without transcript / transcript without audio | {s['n_no_transcript']} / {s['n_no_audio']} |",
        f"| Unreadable audio | {s['n_unreadable']} |",
        f"| **Total duration** | **{s['total_hours']:.3f} h** |",
        f"| Utterance duration (s) | {fmt(s['duration_s'])} |",
        f"| Sample rates | {s['sample_rates']} |",
        f"| Channels / subtype | {s['channels']} / {s['subtypes']} |",
        f"| **Speakers** (from filename) | **{s['n_speakers']}** |",
        f"| Utterances per speaker | {fmt(s['speaker_utts'], nd=1)} |",
        f"| Minutes per speaker | {fmt(s['speaker_minutes'])} |",
        f"| Characters per utterance | {fmt(s['chars_per_utt'], nd=1)} |",
        f"| Words per utterance | {fmt(s['words_per_utt'], nd=1)} |",
        f"| Characters per second | {fmt(s['chars_per_sec'])} |",
        f"| Peak amplitude | {fmt(s['peak'], nd=3)} |",
        f"| RMS (dBFS) | {fmt(s['rms_dbfs'], nd=1)} |",
        f"| Leading silence (s) | {fmt(s['lead_sil_s'])} |",
        f"| Trailing silence (s) | {fmt(s['trail_sil_s'])} |",
        f"| Unique transcripts | {s['unique_texts']} |",
        f"| Duplicate-text groups / utterances | {s['dup_text_groups']} / {s['dup_text_utts']} |",
        f"| Duplicate texts read by >1 speaker | {s['cross_speaker_dup_groups']} |",
        "| Transcripts with: NFC change / Latin letters / ASCII digits / Bengali digits / ZWJ-ZWNJ / punctuation | "
        f"{tf['nfc_changed']} / {tf['latin_chars']} / {tf['ascii_digits']} / {tf['bengali_digits']} / "
        f"{tf['zw_chars']} / {tf['punct']} |",
        f"| Flag counts | {s['flag_counts']} |",
        f"| Overlap with Google `prompts.tsv` | {s['google_prompts_overlap'] or 'not checked'} |",
        f"| Non-WAV files | {', '.join(s['non_wav_files'])} |",
        "", "Gender: not inferred. Report only if corpus metadata provides it.", "",
        "## Speakers (top 15 by duration)", "", "| speaker | utts | minutes |", "|---|---|---|",
        *[f"| {k} | {v['utts']} | {v['dur_s'] / 60:.1f} |" for k, v in top[:15]],
        "", f"Full list: `speakers.tsv`. Cross-speaker duplicate texts (first 10, truncated): "
            f"{[t[:40] for t in list(xdups)[:10]]}", "",
        "Flag definitions: clipping = >0.1 % samples at |x| ≥ 0.999; long_edge_silence = >1 s below "
        f"{SILENCE_DBFS} dBFS at either edge; dur_low/high_tail = outside the 0.5–99.5 percentile range.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
