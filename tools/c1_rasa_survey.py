"""C1 (D-056): survey Rasa Bengali metadata without downloading audio.

Reads only the text columns of every Bengali parquet shard (HTTP range reads via HfFileSystem)
and writes data/raw/rasa_bn/meta.tsv with shard, row index, row group and metadata.
Usage: python tools/c1_rasa_survey.py
"""

from __future__ import annotations

import csv
from pathlib import Path

import pyarrow.parquet as pq
from huggingface_hub import HfFileSystem

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/raw/rasa_bn/meta.tsv"
COLS = ["filename", "text", "gender", "style", "duration"]


def main() -> int:
    fs = HfFileSystem()
    shards = sorted(fs.glob("datasets/ai4bharat/Rasa/Bengali/*.parquet"))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["shard", "row", "row_group", *COLS])
        for sh in shards:
            with fs.open(sh, "rb", block_size=256 * 1024, cache_type="bytes") as fh:
                pf = pq.ParquetFile(fh)
                row = 0
                for rg in range(pf.num_row_groups):
                    t = pf.read_row_group(rg, columns=COLS).to_pylist()
                    for r in t:
                        w.writerow([sh.split("/")[-1], row, rg, *(str(r[c]).replace("\t", " ").replace("\n", " ") for c in COLS)])
                        row += 1
            print(sh.split("/")[-1], row, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
