# Control analysis (ASR `wav2vec2-xls-r-300m-bengali`)

Complete runs: BN-G 2/2, LAT-G-det 2/2, LAT-P 2/2, BN-G-matched 2/2, LAT-P-reinit 2/2, LAT-P-rand 2/2. Observations only.

## Fixed set CER % by update (mean of seeds)

| arm | u0 | u500 | u1000 | u2000 | u3000 |
|---|---|---|---|---|---|
| BN-G | 89.6 | 86.3 | 83.6 | 75.9 | 68.4 |
| LAT-G-det | 63.6 | 44.1 | 32.9 | 26.4 | 24.5 |
| LAT-P | 48.2 | 32.8 | 25.4 | 21.1 | 20.0 |
| BN-G-matched | 93.9 | 86.9 | 82.1 | 72.6 | 65.7 |
| LAT-P-reinit | 95.9 | 84.4 | 81.6 | 48.8 | 38.6 |
| LAT-P-rand | 91.2 | 83.2 | 82.9 | 83.5 | 80.3 |

## test_seen at u3000 (PRIMARY)

| arm | CER mean | per-seed | seed SD |
|---|---|---|---|
| BN-G | 65.46 | 64.86, 66.05 | 0.84 |
| LAT-G-det | 21.28 | 21.54, 21.03 | 0.36 |
| LAT-P | 18.36 | 18.67, 18.05 | 0.44 |
| BN-G-matched | 63.29 | 63.17, 63.41 | 0.16 |
| LAT-P-reinit | 37.04 | 37.22, 36.85 | 0.26 |
| LAT-P-rand | 77.87 | 77.78, 77.96 | 0.13 |

| contrast A − B | ΔCER | paired 95 % CI | half-width | 2 × max seed SD | G6 |
|---|---|---|---|---|---|
| BN-G-matched − BN-G | -2.17 | [-3.16, -1.24] | 0.96 | 1.68 | YES |
| LAT-P − LAT-P-reinit | -18.67 | [-20.56, -16.88] | 1.84 | 0.89 | YES |
| LAT-P − LAT-P-rand | -59.51 | [-61.47, -57.51] | 1.98 | 0.89 | YES |
| LAT-P-rand − LAT-P-reinit | +40.84 | [+39.01, +42.60] | 1.80 | 0.52 | YES |
| BN-G-matched − LAT-P-reinit | +26.25 | [+24.22, +28.25] | 2.01 | 0.52 | YES |
| BN-G-matched − LAT-G-det | +42.01 | [+40.08, +43.93] | 1.93 | 0.72 | YES |

## test_unseen at u3000

| arm | CER mean | per-seed | seed SD |
|---|---|---|---|
| BN-G | 68.24 | 68.29, 68.20 | 0.07 |
| LAT-G-det | 22.84 | 23.34, 22.34 | 0.71 |
| LAT-P | 19.33 | 19.18, 19.49 | 0.22 |
| BN-G-matched | 67.16 | 65.40, 68.92 | 2.48 |
| LAT-P-reinit | 38.32 | 39.18, 37.46 | 1.22 |
| LAT-P-rand | 84.24 | 83.54, 84.93 | 0.98 |

| contrast A − B | ΔCER | paired 95 % CI | half-width | 2 × max seed SD | G6 |
|---|---|---|---|---|---|
| BN-G-matched − BN-G | -1.08 | [-2.26, +0.16] | 1.21 | 4.97 | no |
| LAT-P − LAT-P-reinit | -18.99 | [-21.25, -17.03] | 2.11 | 2.43 | YES |
| LAT-P − LAT-P-rand | -64.90 | [-68.75, -61.37] | 3.69 | 1.96 | YES |
| LAT-P-rand − LAT-P-reinit | +45.91 | [+42.76, +48.83] | 3.03 | 2.43 | YES |
| BN-G-matched − LAT-P-reinit | +28.84 | [+26.00, +31.73] | 2.87 | 4.97 | YES |
| BN-G-matched − LAT-G-det | +44.32 | [+41.16, +47.73] | 3.28 | 4.97 | YES |
