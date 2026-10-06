# Splits v1 (SLR37 bn_bd)

Seed 20261006; unseen speaker `01701`; text-disjoint across train/val vs test; durations are edge-trimmed speech (raw = file length).

| split | utts | speech h | raw h | unique texts | per-speaker utts |
|---|---|---|---|---|---|
| test_unseen | 110 | 0.127 | 0.222 | 110 | {'01701': 110} |
| test_seen | 163 | 0.150 | 0.236 | 154 | {'00737': 34, '00779': 32, '01232': 33, '02194': 31, '03042': 33} |
| val | 50 | 0.047 | 0.073 | 46 | {'00737': 10, '00779': 10, '01232': 10, '02194': 10, '03042': 10} |
| train_0.25h | 251 | 0.252 | 0.384 | 251 | {'00737': 61, '00779': 26, '01232': 50, '02194': 40, '03042': 74} |
| train_0.5h | 503 | 0.500 | 0.761 | 502 | {'00737': 126, '00779': 54, '01232': 99, '02194': 83, '03042': 141} |
| train_1h | 1007 | 1.000 | 1.531 | 997 | {'00737': 263, '00779': 105, '01232': 199, '02194': 165, '03042': 275} |
| train_full | 1568 | 1.577 | 2.407 | 1546 | {'00737': 423, '00779': 162, '01232': 305, '02194': 248, '03042': 430} |

Nested: every smaller train subset is a prefix of the next (same audio for every representation arm).

SHA-256 of split files:

- `test_unseen`: `5a98e1fa809f82b92b1ad90b9b3fadb231ae3e83f2c4f415fae7c18eab578693`
- `test_seen`: `1e56c217b27037bce764d3c16490fa5bad4cbdf55393ae342cd1d1be80323a2f`
- `val`: `5e456e47464c556d15721b700dc85d946e015cff448401c52ba5ede4d276dcba`
- `train_0.25h`: `d3fb574abbea269b22648a74387a64dc9177df80a6dd35ca22e207e0f93cbf27`
- `train_0.5h`: `2c882ccba7451f74cc18ded2bf0eb828313e4fb9102679622807ea9e69980a5d`
- `train_1h`: `ebc75dce9f213a0fd4016882d2faebcf4315c648438dfef8063cc6c97335d1c4`
- `train_full`: `d075d2a546fc2bf4a8d09e3cb89d5ce0cf2938207734be1b56f232b7ce22939a`
