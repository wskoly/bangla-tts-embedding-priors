# Encoding-path analysis (ASR `wav2vec2-xls-r-300m-bengali`)

Complete runs: BN-G-matched 2/2, BN-G-iv 2/2, BN-G-iv-vm 2/2, BN-G-iv-vm-asp 2/2, LAT-G-det-reinit 2/2. Observations only.

## Fixed set CER % by update (mean of seeds)

| arm | u0 | u500 | u1000 | u2000 | u3000 |
|---|---|---|---|---|---|
| BN-G-matched | 93.9 | 86.9 | 82.1 | 72.6 | 65.7 |
| BN-G-iv | 94.3 | 83.9 | 82.3 | 72.4 | 63.1 |
| BN-G-iv-vm | 92.1 | 84.9 | 82.4 | 59.4 | 52.6 |
| BN-G-iv-vm-asp | 91.6 | 82.6 | 63.5 | 34.1 | 31.1 |
| LAT-G-det-reinit | 99.4 | 85.8 | 70.1 | 45.5 | 39.4 |

## test_seen at u3000 (PRIMARY)

| arm | CER mean | per-seed | seed SD |
|---|---|---|---|
| BN-G-matched | 63.29 | 63.17, 63.41 | 0.16 |
| BN-G-iv | 62.60 | 63.14, 62.06 | 0.76 |
| BN-G-iv-vm | 50.97 | 51.74, 50.19 | 1.09 |
| BN-G-iv-vm-asp | 27.42 | 26.48, 28.37 | 1.34 |
| LAT-G-det-reinit | 36.26 | 35.03, 37.48 | 1.73 |

| step A − B | ΔCER | paired 95 % CI | half-width | 2 × max seed SD | G6 |
|---|---|---|---|---|---|
| BN-G-matched − BN-G-iv | +0.69 | [-0.39, +1.78] | 1.08 | 1.52 | no |
| BN-G-iv − BN-G-iv-vm | +11.63 | [+10.44, +12.84] | 1.20 | 2.19 | YES |
| BN-G-iv-vm − BN-G-iv-vm-asp | +23.54 | [+21.88, +25.17] | 1.64 | 2.68 | YES |
| BN-G-iv-vm-asp − LAT-G-det-reinit | -8.83 | [-10.15, -7.54] | 1.30 | 3.45 | YES |

## test_unseen at u3000

| arm | CER mean | per-seed | seed SD |
|---|---|---|---|
| BN-G-matched | 67.16 | 65.40, 68.92 | 2.48 |
| BN-G-iv | 63.02 | 64.98, 61.06 | 2.77 |
| BN-G-iv-vm | 52.34 | 53.37, 51.31 | 1.45 |
| BN-G-iv-vm-asp | 28.65 | 28.35, 28.96 | 0.43 |
| LAT-G-det-reinit | 38.69 | 38.11, 39.28 | 0.82 |

| step A − B | ΔCER | paired 95 % CI | half-width | 2 × max seed SD | G6 |
|---|---|---|---|---|---|
| BN-G-matched − BN-G-iv | +4.14 | [+2.71, +5.59] | 1.44 | 5.54 | no |
| BN-G-iv − BN-G-iv-vm | +10.68 | [+9.06, +12.23] | 1.58 | 5.54 | YES |
| BN-G-iv-vm − BN-G-iv-vm-asp | +23.69 | [+21.62, +25.95] | 2.17 | 2.90 | YES |
| BN-G-iv-vm-asp − LAT-G-det-reinit | -10.04 | [-11.77, -8.36] | 1.70 | 1.65 | YES |
