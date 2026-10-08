# LAT-G-asp analysis (ASR `tugstugi_bengaliai-asr_whisper-medium`)

Complete runs: BN-G 2/2, LAT-G-det 2/2, LAT-P 2/2, LAT-G-det-reinit 2/2, BN-G-iv-vm-asp 2/2, LAT-G-asp 2/2. Observations only.

## Fixed set CER % by update (mean of seeds)

| arm | u0 | u500 | u1000 | u2000 | u3000 |
|---|---|---|---|---|---|
| BN-G | 105.2 | 93.3 | 90.4 | 79.6 | 71.5 |
| LAT-G-det | 64.5 | 37.6 | 22.6 | 13.8 | 11.4 |
| LAT-P | 38.2 | 21.6 | 14.1 | 9.1 | 8.0 |
| LAT-G-det-reinit | 120.9 | 94.7 | 75.4 | 41.3 | 32.6 |
| BN-G-iv-vm-asp | 107.5 | 86.6 | 67.8 | 25.3 | 21.2 |
| LAT-G-asp | 61.3 | 37.4 | 21.8 | 14.4 | 12.6 |

## test_seen at u3000 (PRIMARY)

| arm | CER mean | per-seed | seed SD |
|---|---|---|---|
| BN-G | 67.97 | 66.81, 69.12 | 1.64 |
| LAT-G-det | 11.10 | 11.01, 11.18 | 0.12 |
| LAT-P | 7.54 | 7.83, 7.25 | 0.41 |
| LAT-G-det-reinit | 30.60 | 28.28, 32.91 | 3.27 |
| BN-G-iv-vm-asp | 19.36 | 17.77, 20.95 | 2.25 |
| LAT-G-asp | 10.28 | 10.22, 10.35 | 0.09 |

| contrast | ΔCER | paired 95 % CI | half-width | 2 × max seed SD | G6 |
|---|---|---|---|---|---|
| BN-G-iv-vm-asp − LAT-G-asp | +9.08 | [+7.68, +10.50] | 1.41 | 4.50 | YES |
| LAT-G-det − LAT-G-asp | +0.81 | [-0.28, +1.89] | 1.09 | 0.24 | no |
| LAT-P − LAT-G-asp | -2.74 | [-3.77, -1.60] | 1.08 | 0.81 | YES |
| (BN-G-iv-vm-asp − LAT-G-asp) − (LAT-G-det-reinit − LAT-G-det) | -10.42 | [-12.22, -8.76] | 1.73 | 6.55 | YES |

## test_unseen at u3000

| arm | CER mean | per-seed | seed SD |
|---|---|---|---|
| BN-G | 73.32 | 72.76, 73.87 | 0.78 |
| LAT-G-det | 10.54 | 10.67, 10.41 | 0.18 |
| LAT-P | 6.05 | 7.03, 5.07 | 1.39 |
| LAT-G-det-reinit | 32.00 | 30.99, 33.01 | 1.42 |
| BN-G-iv-vm-asp | 16.88 | 15.66, 18.10 | 1.73 |
| LAT-G-asp | 10.77 | 10.45, 11.09 | 0.46 |

| contrast | ΔCER | paired 95 % CI | half-width | 2 × max seed SD | G6 |
|---|---|---|---|---|---|
| BN-G-iv-vm-asp − LAT-G-asp | +6.11 | [+4.37, +7.99] | 1.81 | 3.45 | YES |
| LAT-G-det − LAT-G-asp | -0.23 | [-1.53, +1.05] | 1.29 | 0.92 | no |
| LAT-P − LAT-G-asp | -4.72 | [-6.04, -3.55] | 1.24 | 2.77 | YES |
| (BN-G-iv-vm-asp − LAT-G-asp) − (LAT-G-det-reinit − LAT-G-det) | -15.35 | [-17.40, -13.06] | 2.17 | 3.45 | YES |
