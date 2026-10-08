# LAT-G-det-reinit analysis (ASR `tugstugi_bengaliai-asr_whisper-medium`)

Complete runs: BN-G 2/2, LAT-G-det 2/2, LAT-P 2/2, BN-G-matched 2/2, LAT-P-reinit 2/2, LAT-P-rand 2/2, LAT-G-det-reinit 2/2. Observations only.

## Fixed set CER % by update (mean of seeds)

| arm | u0 | u500 | u1000 | u2000 | u3000 |
|---|---|---|---|---|---|
| BN-G | 105.2 | 93.3 | 90.4 | 79.6 | 71.5 |
| LAT-G-det | 64.5 | 37.6 | 22.6 | 13.8 | 11.4 |
| LAT-P | 38.2 | 21.6 | 14.1 | 9.1 | 8.0 |
| BN-G-matched | 115.7 | 94.9 | 85.2 | 76.1 | 69.0 |
| LAT-P-reinit | 112.4 | 91.7 | 86.8 | 45.7 | 32.0 |
| LAT-P-rand | 103.9 | 88.4 | 89.5 | 88.9 | 84.4 |
| LAT-G-det-reinit | 120.9 | 94.7 | 75.4 | 41.3 | 32.6 |

## test_seen at u3000 (PRIMARY)

| arm | CER mean | per-seed | seed SD |
|---|---|---|---|
| BN-G | 67.97 | 66.81, 69.12 | 1.64 |
| LAT-G-det | 11.10 | 11.01, 11.18 | 0.12 |
| LAT-P | 7.54 | 7.83, 7.25 | 0.41 |
| BN-G-matched | 66.16 | 66.58, 65.75 | 0.59 |
| LAT-P-reinit | 30.16 | 30.31, 30.01 | 0.22 |
| LAT-P-rand | 81.30 | 81.12, 81.48 | 0.25 |
| LAT-G-det-reinit | 30.60 | 28.28, 32.91 | 3.27 |

| contrast | ΔCER | paired 95 % CI | half-width | 2 × max seed SD | G6 |
|---|---|---|---|---|---|
| LAT-G-det − LAT-G-det-reinit | -19.50 | [-21.19, -17.98] | 1.60 | 6.55 | YES |
| LAT-G-det-reinit − LAT-P-reinit | +0.44 | [-1.56, +2.53] | 2.04 | 6.55 | no |
| BN-G-matched − LAT-G-det-reinit | +35.57 | [+33.72, +37.32] | 1.80 | 6.55 | YES |
| (LAT-G-det-reinit − LAT-G-det) − (LAT-P-reinit − LAT-P) | -3.12 | [-5.02, -0.89] | 2.06 | 6.55 | no |

## test_unseen at u3000

| arm | CER mean | per-seed | seed SD |
|---|---|---|---|
| BN-G | 73.32 | 72.76, 73.87 | 0.78 |
| LAT-G-det | 10.54 | 10.67, 10.41 | 0.18 |
| LAT-P | 6.05 | 7.03, 5.07 | 1.39 |
| BN-G-matched | 71.57 | 70.03, 73.11 | 2.18 |
| LAT-P-reinit | 29.08 | 29.68, 28.48 | 0.85 |
| LAT-P-rand | 91.36 | 91.33, 91.40 | 0.05 |
| LAT-G-det-reinit | 32.00 | 30.99, 33.01 | 1.42 |

| contrast | ΔCER | paired 95 % CI | half-width | 2 × max seed SD | G6 |
|---|---|---|---|---|---|
| LAT-G-det − LAT-G-det-reinit | -21.46 | [-23.67, -19.24] | 2.22 | 2.85 | YES |
| LAT-G-det-reinit − LAT-P-reinit | +2.92 | [+0.83, +5.03] | 2.10 | 2.85 | YES |
| BN-G-matched − LAT-G-det-reinit | +39.57 | [+37.15, +42.25] | 2.55 | 4.37 | YES |
| (LAT-G-det-reinit − LAT-G-det) − (LAT-P-reinit − LAT-P) | -1.57 | [-3.89, +0.62] | 2.26 | 2.85 | no |
