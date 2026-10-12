# Long-training check (D-064, exploratory): SLR37 train_full, seed 666, Whisper

## Fixed set (50 utts): CER % / চ→ক % by update (15k-update schedule)

| arm | u0 | u1000 | u3000 | u6000 | u10000 | u15000 |
|---|---|---|---|---|---|---|
| LAT-P | 38.24 / 2.8 | 14.24 / 13.9 | 5.16 / 0.0 | 2.90 / 0.0 | 3.62 / 0.0 | 3.50 / 0.0 |
| LAT-G-det | 64.54 / 0.0 | 20.61 / 0.0 | 6.97 / 0.0 | 4.48 / 0.0 | 4.37 / 0.0 | 4.63 / 0.0 |

## test_seen / test_unseen: 3k-update runs (pilot_v6, s666 and s1234) vs 15k (pilot_x1, s666)

| arm | split | 3k CER s666 / s1234 | 15k CER s666 | 3k চ→ক s666 / s1234 | 15k চ→ক s666 (n words) |
|---|---|---|---|---|---|
| LAT-P | test_seen | 7.79 / 7.23 | 3.10 | 10.2 / 3.4 | 0.0 (88) |
| LAT-P | test_unseen | 5.97 / 5.16 | 2.64 | 3.8 / 0.0 | 0.0 (53) |
| LAT-G-det | test_seen | 11.09 / 10.55 | 3.63 | 0.0 / 0.0 | 0.0 (88) |
| LAT-G-det | test_unseen | 11.11 / 10.58 | 4.05 | 0.0 / 0.0 | 0.0 (53) |
