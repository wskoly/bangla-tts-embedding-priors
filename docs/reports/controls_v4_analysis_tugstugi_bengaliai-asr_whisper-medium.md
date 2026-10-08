# Encoding-path analysis (ASR `tugstugi_bengaliai-asr_whisper-medium`)

Complete runs: BN-G-matched 2/2, BN-G-iv 2/2, BN-G-iv-vm 2/2, BN-G-iv-vm-asp 2/2, LAT-G-det-reinit 2/2. Observations only.

## Fixed set CER % by update (mean of seeds)

| arm | u0 | u500 | u1000 | u2000 | u3000 |
|---|---|---|---|---|---|
| BN-G-matched | 115.7 | 94.9 | 85.2 | 76.1 | 69.0 |
| BN-G-iv | 114.7 | 89.8 | 87.1 | 76.8 | 65.4 |
| BN-G-iv-vm | 112.7 | 88.4 | 88.7 | 60.9 | 50.2 |
| BN-G-iv-vm-asp | 107.5 | 86.6 | 67.8 | 25.3 | 21.2 |
| LAT-G-det-reinit | 120.9 | 94.7 | 75.4 | 41.3 | 32.6 |

## test_seen at u3000 (PRIMARY)

| arm | CER mean | per-seed | seed SD |
|---|---|---|---|
| BN-G-matched | 66.16 | 66.58, 65.75 | 0.59 |
| BN-G-iv | 63.98 | 65.08, 62.88 | 1.56 |
| BN-G-iv-vm | 50.23 | 52.11, 48.35 | 2.66 |
| BN-G-iv-vm-asp | 19.36 | 17.77, 20.95 | 2.25 |
| LAT-G-det-reinit | 30.60 | 28.28, 32.91 | 3.27 |

| step A − B | ΔCER | paired 95 % CI | half-width | 2 × max seed SD | G6 |
|---|---|---|---|---|---|
| BN-G-matched − BN-G-iv | +2.18 | [+1.02, +3.34] | 1.16 | 3.11 | no |
| BN-G-iv − BN-G-iv-vm | +13.75 | [+12.53, +15.09] | 1.28 | 5.32 | YES |
| BN-G-iv-vm − BN-G-iv-vm-asp | +30.87 | [+29.23, +32.49] | 1.63 | 5.32 | YES |
| BN-G-iv-vm-asp − LAT-G-det-reinit | -11.24 | [-12.86, -9.72] | 1.57 | 6.55 | YES |

## test_unseen at u3000

| arm | CER mean | per-seed | seed SD |
|---|---|---|---|
| BN-G-matched | 71.57 | 70.03, 73.11 | 2.18 |
| BN-G-iv | 64.92 | 67.29, 62.56 | 3.35 |
| BN-G-iv-vm | 50.77 | 51.63, 49.91 | 1.22 |
| BN-G-iv-vm-asp | 16.88 | 15.66, 18.10 | 1.73 |
| LAT-G-det-reinit | 32.00 | 30.99, 33.01 | 1.42 |

| step A − B | ΔCER | paired 95 % CI | half-width | 2 × max seed SD | G6 |
|---|---|---|---|---|---|
| BN-G-matched − BN-G-iv | +6.65 | [+4.96, +8.39] | 1.71 | 6.69 | no |
| BN-G-iv − BN-G-iv-vm | +14.15 | [+12.33, +15.96] | 1.82 | 6.69 | YES |
| BN-G-iv-vm − BN-G-iv-vm-asp | +33.89 | [+31.61, +36.14] | 2.26 | 3.45 | YES |
| BN-G-iv-vm-asp − LAT-G-det-reinit | -15.12 | [-17.12, -13.09] | 2.02 | 3.45 | YES |
