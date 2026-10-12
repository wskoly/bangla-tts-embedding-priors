"""Synthesize the stress-test sentences for the public sample page (illustration only; no claims; D-068).

Every model uses the same reference clip, the same target duration and the same noise seed per sentence, so the only
difference between outputs is the input representation (and its trained weights). Target duration = number of
non-space Bengali characters x the reference speaker's median seconds-per-character in its train_1h data (identical
for every arm). Words missing from the lexicon are filled by G2P v1 for the lexical arms and listed in meta.json.
Each output is transcribed with the primary ASR (Whisper-BengaliAI) and scored against the input text.
    python tools/samples_synth.py            # GPU; writes runs/samples_v1/
"""

from __future__ import annotations

import csv
import json
import re
import statistics
import sys
from pathlib import Path

import soundfile as sf

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.bnrep.normalize import normalize  # noqa: E402
from src.bnrep.reps import LEXICAL_CONVERTERS, convert  # noqa: E402

OUT = ROOT / "runs/samples_v1"
SENTENCES = [  # our own stress sentences (D-068); split at sentence ends, punctuation reduced as in C1 rules
    "ঐ বুড়ো ড্যাফোডিল গাছে চড়ে হঠাৎ ফিসফিস করে বলল, ‘ঋণ নেওয়া খুব খারাপ!’ এটা শুনেই খুকি ঘাবড়ে গিয়ে মেঘের মতন জোরে চেঁচিয়ে উঠল।",
    "ঐ থালায় কড়কড়ে ফ্রাই করা ব্যাং দেখে খুকি খুব ঘাবড়ে গেল।",
    "সে হঠাৎ জোরে চেঁচিয়ে উঠে বলল, ‘ঈশ!",
    "ধ্যাৎ, ওটা আমি ছুঁয়ে ফেলেছি!",
    "ঝড়-বৃষ্টির রাতে ওই প্রৌঢ় বাবুটি খ্যাকখ্যাক করে হেসে উঠলেন।",
    "তিনি ট্যাঁশ গদিতে বসে ধীর লয়ে ডালিম মাখা ভাত খেতে লাগলেন।",
]
CORPORA = {
    "slr37": {"manifest": "data/derived/slr37_bn_bd/manifest.tsv", "index": "data/derived/audio24k_v1/index.tsv",
              "train": "data/derived/splits/v1/train_1h.tsv", "refs": "data/derived/eval/refs_v1.tsv",
              "speaker": "00779"},
    "rasa": {"manifest": "data/derived/rasa_bn/manifest.tsv", "index": "data/derived/audio24k_rasa_v1/index.tsv",
             "train": "data/derived/splits/rasa_v1/train_1h.tsv", "refs": "data/derived/eval_rasa_v1/refs_v1.tsv",
             "speaker": "rasaF"},
}
R = "runs/{}__train_1h__s666/online_u3000.safetensors"
MODELS = [  # (id, rep, checkpoint, corpus)
    ("slr37_BN-G-matched", "BN-G", R.format("pilot_v2/BN-G-matched"), "slr37"),
    ("slr37_BN-G-iv-vm-asp", "BN-G-iv-vm-asp", R.format("pilot_v4/BN-G-iv-vm-asp"), "slr37"),
    ("slr37_LAT-G-det", "LAT-G-det", R.format("pilot_v1_1/LAT-G-det"), "slr37"),
    ("slr37_LAT-G-asp", "LAT-G-asp", R.format("pilot_v5/LAT-G-asp"), "slr37"),
    ("slr37_LAT-P", "LAT-P", R.format("pilot_v1_1/LAT-P"), "slr37"),
    ("slr37_LAT-P-reinit", "LAT-P", R.format("pilot_v2/LAT-P-reinit"), "slr37"),
    ("slr37_LAT-P-rand", "LAT-P-rand", R.format("pilot_v2/LAT-P-rand"), "slr37"),
    ("slr37_LAT-P_15k", "LAT-P", "runs/pilot_x1/LAT-P__train_full__s666/online_u15000.safetensors", "slr37"),
    ("slr37_LAT-G-det_15k", "LAT-G-det", "runs/pilot_x1/LAT-G-det__train_full__s666/online_u15000.safetensors", "slr37"),
    ("rasa_BN-G-matched", "BN-G", R.format("pilot_c1a/BN-G-matched"), "rasa"),
    ("rasa_BN-G-iv-vm-asp", "BN-G-iv-vm-asp", R.format("pilot_c1a/BN-G-iv-vm-asp"), "rasa"),
    ("rasa_LAT-G-det", "LAT-G-det", R.format("pilot_c1b/LAT-G-det"), "rasa"),
    ("rasa_LAT-G-asp", "LAT-G-asp", R.format("pilot_c1b/LAT-G-asp"), "rasa"),
    ("rasa_LAT-P", "LAT-P", R.format("pilot_c1a/LAT-P"), "rasa"),
]


def clean(s: str) -> str:
    """C1 text rules (docs/C1_data_rules.md): drop quotes, hyphen to space, , ; : ? ! to '.', then normalize."""
    s = re.sub("[‘’'\"“”()]", "", s).replace("-", " ")
    return normalize(re.sub(r"[,;:?!]", ".", s))


def tsv(path: str) -> list[dict]:
    with open(ROOT / path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE))


def speaker_setup(c: dict) -> dict:
    text = {r["utt_id"]: r["text"] for r in tsv(c["manifest"])}
    audio = {r["utt_id"]: r for r in tsv(c["index"])}
    train = [r["utt_id"] for r in tsv(c["train"])]
    own = [u for u in train if u in audio and (c["speaker"] == "rasaF" or f"_{c['speaker']}_" in u)]
    rate = statistics.median(float(audio[u]["duration_s"]) / len(normalize(text[u]).replace(" ", "")) for u in own)
    ref = next(r for r in tsv(c["refs"]) if r["speaker"] == c["speaker"])
    return {"rate": rate, "n_rate_utts": len(own), "ref_wav": str(ROOT / audio[ref["ref_utt_id"]]["path"]),
            "ref_text": ref["text"]}


def main() -> int:
    import torch

    from src.bnrep.g2p.model import G2P
    from src.eval.asr import ASR, load_audio_16k, utt_scores
    from src.infer.f5_infer import F5Synth, utt_seed
    g2p = G2P(ROOT / "runs/g2p/v1", device="cpu")
    sents = [clean(s) for s in SENTENCES]
    setup = {k: speaker_setup(c) for k, c in CORPORA.items()}
    OUT.mkdir(parents=True, exist_ok=True)
    meta = {"sentences": sents, "setup": setup, "models": {}}
    for mid, rep, ckpt, corpus in MODELS:
        d = OUT / mid
        d.mkdir(exist_ok=True)
        s = setup[corpus]
        lex = rep in LEXICAL_CONVERTERS
        synth = F5Synth(rep, str(ROOT / ckpt), use_ema=False)
        ref = convert(rep, s["ref_text"], g2p=g2p if lex else None)
        entries = []
        for i, txt in enumerate(sents):
            res = convert(rep, txt, g2p=g2p if lex else None)
            secs = len(txt.replace(" ", "")) * s["rate"]
            wav = synth.synth(s["ref_wav"], ref.text, res.text, secs, utt_seed(f"samples-v1-{i}"))
            sf.write(d / f"s{i}.wav", wav, 24000, subtype="PCM_16")
            entries.append({"i": i, "input": res.text, "g2p_words": res.oov if lex else [], "seconds": round(secs, 2)})
        meta["models"][mid] = {"rep": rep, "ckpt": ckpt, "corpus": corpus, "items": entries}
        del synth
        torch.cuda.empty_cache()
        print(mid, "done", flush=True)
    asr = ASR("bengaliAI/tugstugi_bengaliai-asr_whisper-medium")
    for mid, m in meta["models"].items():
        hyps = asr.transcribe([load_audio_16k(str(OUT / mid / f"s{e['i']}.wav")) for e in m["items"]])
        for e, h in zip(m["items"], hyps):
            sc = utt_scores(sents[e["i"]], h)
            e["asr"], e["cer"] = sc["hyp"], round(100 * sc["cer"], 1)
    (OUT / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    print("ok:", len(MODELS), "models x", len(sents), "sentences")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
