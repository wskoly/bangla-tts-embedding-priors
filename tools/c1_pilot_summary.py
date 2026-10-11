"""C1 pilot (pilot_c1a, seed 666) summary: per-arm CER and three paired contrasts at u3000, on all test utterances
and on the LAT-P coverage-restricted subset (every word in lexicon + supplement; D-055 rule triggered, D-058).

Pilot only: one seed, so the G6 seed-SD gate cannot be applied; nothing here changes any setting.

    DATA_PROFILE=rasa_bn_v1 python tools/c1_pilot_summary.py
"""

from __future__ import annotations

import csv
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.bnrep.reps import convert  # noqa: E402
from src.corpus.profile import MANIFEST, NAME, SPLITS  # noqa: E402
from src.eval.asr import bootstrap, corpus, utt_scores  # noqa: E402

assert NAME == "rasa_bn_v1", NAME
RUN = ROOT / "runs/pilot_c1a"
ARMS = ["LAT-P", "LAT-P-reinit", "LAT-P-rand", "BN-G-matched", "BN-G-iv-vm-asp"]
ASRS = {"Whisper": "tugstugi_bengaliai-asr_whisper-medium", "wav2vec2": "wav2vec2-xls-r-300m-bengali"}
SPLIT_NAMES = ["test_seen", "test_unseen"]
CONTRASTS = [("H1a-like", "LAT-P", "LAT-P-reinit", "< 0"),
             ("H2-like", "LAT-P-rand", "LAT-P-reinit", "> 0"),
             ("H3b∧c-like", "BN-G-matched", "BN-G-iv-vm-asp", "> 0")]
OUT = ROOT / "docs/reports/c1_pilot_c1a.md"


def rows(arm: str, split: str, asr: str) -> dict[str, dict]:
    p = RUN / f"{arm}__train_1h__s666/eval/u3000/{split}/asr_{asr}.tsv"
    with open(p, encoding="utf-8", newline="") as f:
        return {r["utt_id"]: utt_scores(r["ref"], r["hyp"])
                for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE)}


def paired_delta(a: dict, b: dict, ids: list[str], n: int = 2000) -> tuple[float, float, float]:
    d = corpus([a[u] for u in ids])["CER"] - corpus([b[u] for u in ids])["CER"]
    rng, ds = random.Random(20261011), []
    for _ in range(n):
        s = [ids[rng.randrange(len(ids))] for _ in ids]
        ds.append(corpus([a[u] for u in s])["CER"] - corpus([b[u] for u in s])["CER"])
    ds.sort()
    return d, ds[int(.025 * (n - 1))], ds[int(.975 * (n - 1))]


def main() -> int:
    with open(MANIFEST, encoding="utf-8", newline="") as f:
        text = {r["utt_id"]: r["text"] for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE)}
    data = {(a, sp, m): rows(a, sp, asr) for a in ARMS for sp in SPLIT_NAMES for m, asr in ASRS.items()}
    subsets = {}
    for sp in SPLIT_NAMES:
        with open(SPLITS / f"{sp}.tsv", encoding="utf-8") as f:
            ids = [r["utt_id"] for r in csv.DictReader(f, delimiter="\t")]
        ids = [u for u in ids if u in data[(ARMS[0], sp, "Whisper")]]  # the speaker's reference clip is not evaluated
        subsets[(sp, "all")] = ids
        subsets[(sp, "covered")] = [u for u in ids if not convert("LAT-P", text[u]).oov]
    for k, v in data.items():
        assert set(v) == set(subsets[(k[1], "all")]), k

    L = ["# C1 pilot (pilot_c1a): Rasa bn, seed 666, u3000", "",
         "Pilot only (D-055/D-058): one seed, so no seed-SD gate; results do not change any setting. "
         "CER % = corpus ratio; 95 % CI = utterance bootstrap. *covered* = test utterances whose every word is in the "
         "LAT-P lexicon + supplement (no G2P); LAT-P arms are judged on it as primary (coverage rule triggered).", "",
         "## Per arm (CER % [95 % CI])", "",
         "| arm | ASR | seen all | seen covered | unseen all | unseen covered |", "|---|---|---|---|---|---|"]
    for a in ARMS:
        for m in ASRS:
            cells = []
            for sp in SPLIT_NAMES:
                for sub in ("all", "covered"):
                    rs = [data[(a, sp, m)][u] for u in subsets[(sp, sub)]]
                    c, ci = corpus(rs)["CER"], bootstrap(rs)["CER_ci95"]
                    cells.append(f"{c:.2f} [{ci[0]:.2f}, {ci[1]:.2f}]")
            L.append(f"| {a} | {m} | " + " | ".join(cells) + " |")
    L += ["", "n: " + ", ".join(f"{sp} {sub} = {len(subsets[(sp, sub)])}" for sp in SPLIT_NAMES
                                 for sub in ("all", "covered")), "",
          "## Paired contrasts (Δ CER, A − B [95 % CI]; predicted = C3 direction)", "",
          "| contrast | A − B | predicted | ASR | seen all | seen covered | unseen all | unseen covered |",
          "|---|---|---|---|---|---|---|---|"]
    for name, a, b, pred in CONTRASTS:
        for m in ASRS:
            cells = []
            for sp in SPLIT_NAMES:
                for sub in ("all", "covered"):
                    d, lo, hi = paired_delta(data[(a, sp, m)], data[(b, sp, m)], subsets[(sp, sub)])
                    cells.append(f"{d:+.2f} [{lo:+.2f}, {hi:+.2f}]")
            L.append(f"| {name} | {a} − {b} | {pred} | {m} | " + " | ".join(cells) + " |")
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
