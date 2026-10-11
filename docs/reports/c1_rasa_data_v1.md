# C1 Rasa Bengali data (rasa_bn_v1, D-057)

Built by `tools/c1_rasa_build.py` under `docs/C1_data_rules.md` (rules fixed before download).

- Shards downloaded: train-00028-of-00055.parquet, train-00029-of-00055.parquet, train-00030-of-00055.parquet, test-00004-of-00007.parquet, test-00000-of-00007.parquet.
- Filters applied to the 2 test shards + first 4 Female train shards. Neutral candidates: 1871. Exclusions: {'duration outside 1-15 s': 117, 'emotion style': 935, 'text rule (digits / Latin / out-of-vocab)': 14}.

| split | speaker | utts | trimmed speech h | raw h |
|---|---|---|---|---|
| test_seen | rasaF | 160 | 0.264 | 0.291 |
| test_unseen | rasaM | 110 | 0.160 | 0.175 |
| val | rasaF | 50 | 0.080 | 0.089 |
| train_1h | rasaF | 624 | 1.001 | 1.122 |

## LAT-P lexicon coverage (lexicon + supplement; the rest via G2P v1)

| split | tokens | token coverage % | types | type coverage % | utts fully covered |
|---|---|---|---|---|---|
| test_seen | 1904 | 84.7 | 1294 | 79.0 | 47 / 160 |
| test_unseen | 1310 | 83.9 | 940 | 79.5 | 31 / 110 |
| val | 586 | 88.1 | 455 | 85.3 | 18 / 50 |
| train_1h | 7282 | 84.6 | 3704 | 74.4 | 150 / 624 |

Go/no-go criterion (D-055): LAT-P test token coverage ≥ 85 %: **not met**. The ASR floor is measured separately.
