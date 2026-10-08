# LAT-G-det-reinit analysis (ASR `wav2vec2-xls-r-300m-bengali`)

Complete runs: BN-G 2/2, LAT-G-det 2/2, LAT-P 2/2, BN-G-matched 2/2, LAT-P-reinit 2/2, LAT-P-rand 2/2, LAT-G-det-reinit 2/2. Observations only.

## Fixed set CER % by update (mean of seeds)

| arm | u0 | u500 | u1000 | u2000 | u3000 |
|---|---|---|---|---|---|
| BN-G | 89.6 | 86.3 | 83.6 | 75.9 | 68.4 |
| LAT-G-det | 63.6 | 44.1 | 32.9 | 26.4 | 24.5 |
| LAT-P | 48.2 | 32.8 | 25.4 | 21.1 | 20.0 |
| BN-G-matched | 93.9 | 86.9 | 82.1 | 72.6 | 65.7 |
| LAT-P-reinit | 95.9 | 84.4 | 81.6 | 48.8 | 38.6 |
| LAT-P-rand | 91.2 | 83.2 | 82.9 | 83.5 | 80.3 |
| LAT-G-det-reinit | 99.4 | 85.8 | 70.1 | 45.5 | 39.4 |

## test_seen at u3000 (PRIMARY)

| arm | CER mean | per-seed | seed SD |
|---|---|---|---|
| BN-G | 65.46 | 64.86, 66.05 | 0.84 |
| LAT-G-det | 21.28 | 21.54, 21.03 | 0.36 |
| LAT-P | 18.36 | 18.67, 18.05 | 0.44 |
| BN-G-matched | 63.29 | 63.17, 63.41 | 0.16 |
| LAT-P-reinit | 37.04 | 37.22, 36.85 | 0.26 |
| LAT-P-rand | 77.87 | 77.78, 77.96 | 0.13 |
| LAT-G-det-reinit | 36.26 | 35.03, 37.48 | 1.73 |

| contrast | ΔCER | paired 95 % CI | half-width | 2 × max seed SD | G6 |
|---|---|---|---|---|---|
| LAT-G-det − LAT-G-det-reinit | -14.97 | [-16.37, -13.60] | 1.38 | 3.45 | YES |
| LAT-G-det-reinit − LAT-P-reinit | -0.78 | [-2.51, +0.93] | 1.72 | 3.45 | no |
| BN-G-matched − LAT-G-det-reinit | +27.03 | [+25.42, +28.65] | 1.61 | 3.45 | YES |
| (LAT-G-det-reinit − LAT-G-det) − (LAT-P-reinit − LAT-P) | -3.70 | [-5.58, -1.96] | 1.81 | 3.45 | YES |

## test_unseen at u3000

| arm | CER mean | per-seed | seed SD |
|---|---|---|---|
| BN-G | 68.24 | 68.29, 68.20 | 0.07 |
| LAT-G-det | 22.84 | 23.34, 22.34 | 0.71 |
| LAT-P | 19.33 | 19.18, 19.49 | 0.22 |
| BN-G-matched | 67.16 | 65.40, 68.92 | 2.48 |
| LAT-P-reinit | 38.32 | 39.18, 37.46 | 1.22 |
| LAT-P-rand | 84.24 | 83.54, 84.93 | 0.98 |
| LAT-G-det-reinit | 38.69 | 38.11, 39.28 | 0.82 |

| contrast | ΔCER | paired 95 % CI | half-width | 2 × max seed SD | G6 |
|---|---|---|---|---|---|
| LAT-G-det − LAT-G-det-reinit | -15.86 | [-17.72, -14.12] | 1.80 | 1.65 | YES |
| LAT-G-det-reinit − LAT-P-reinit | +0.37 | [-1.75, +2.42] | 2.08 | 2.43 | no |
| BN-G-matched − LAT-G-det-reinit | +28.47 | [+25.50, +31.65] | 3.08 | 4.97 | YES |
| (LAT-G-det-reinit − LAT-G-det) − (LAT-P-reinit − LAT-P) | -3.13 | [-5.34, -1.06] | 2.14 | 2.43 | YES |
