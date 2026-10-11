"""Data profile (D-057): which corpus files the pipeline reads.

Selected by "data_profile" in the pilot config named by $PILOT_CONFIG (default "slr37"), or by $DATA_PROFILE
for standalone tools. Every config written before C1 has no "data_profile" key, so it resolves to exactly the
SLR37 paths it always used.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROFILES = {
    "slr37": {"manifest": "data/derived/slr37_bn_bd/manifest.tsv", "splits": "data/derived/splits/v1",
              "audio_index": "data/derived/audio24k_v1/index.tsv", "eval_dir": "data/derived/eval",
              "allow_g2p": False},
    # C1 (D-056/D-057): Rasa Bengali, neutral styles. Words outside the lexicon go through G2P (LAT-P only).
    "rasa_bn_v1": {"manifest": "data/derived/rasa_bn/manifest.tsv", "splits": "data/derived/splits/rasa_v1",
                   "audio_index": "data/derived/audio24k_rasa_v1/index.tsv", "eval_dir": "data/derived/eval_rasa_v1",
                   "allow_g2p": True},
}


def _name() -> str:
    if os.environ.get("DATA_PROFILE"):
        return os.environ["DATA_PROFILE"]
    cfg = os.environ.get("PILOT_CONFIG")
    if cfg:
        return json.loads((ROOT / cfg).read_text(encoding="utf-8")).get("data_profile", "slr37")
    return "slr37"


NAME = _name()
_P = PROFILES[NAME]
MANIFEST = ROOT / _P["manifest"]
SPLITS = ROOT / _P["splits"]
AUDIO_INDEX = ROOT / _P["audio_index"]
EVAL_DIR = ROOT / _P["eval_dir"]
ALLOW_G2P = _P["allow_g2p"]
