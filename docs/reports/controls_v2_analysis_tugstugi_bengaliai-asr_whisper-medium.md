# Control analysis (ASR `tugstugi_bengaliai-asr_whisper-medium`)

Complete runs: BN-G 2/2, LAT-G-det 2/2, LAT-P 2/2, BN-G-matched 2/2, LAT-P-reinit 2/2, LAT-P-rand 2/2. Observations only.

## Fixed set CER % by update (mean of seeds)

| arm | u0 | u500 | u1000 | u2000 | u3000 |
|---|---|---|---|---|---|
| BN-G | 105.2 | 93.3 | 90.4 | 79.6 | 71.5 |
| LAT-G-det | 64.5 | 37.6 | 22.6 | 13.8 | 11.4 |
| LAT-P | 38.2 | 21.6 | 14.1 | 9.1 | 8.0 |
| BN-G-matched | 115.7 | 94.9 | 85.2 | 76.1 | 69.0 |
| LAT-P-reinit | 112.4 | 91.7 | 86.8 | 45.7 | 32.0 |
| LAT-P-rand | 103.9 | 88.4 | 89.5 | 88.9 | 84.4 |

## test_seen at u3000 (PRIMARY)

| arm | CER mean | per-seed | seed SD |
|---|---|---|---|
| BN-G | 67.97 | 66.81, 69.12 | 1.64 |
| LAT-G-det | 11.10 | 11.01, 11.18 | 0.12 |
| LAT-P | 7.54 | 7.83, 7.25 | 0.41 |
| BN-G-matched | 66.16 | 66.58, 65.75 | 0.59 |
| LAT-P-reinit | 30.16 | 30.31, 30.01 | 0.22 |
| LAT-P-rand | 81.30 | 81.12, 81.48 | 0.25 |

| contrast A − B | ΔCER | paired 95 % CI | half-width | 2 × max seed SD | G6 |
|---|---|---|---|---|---|
| BN-G-matched − BN-G | -1.80 | [-2.78, -0.87] | 0.96 | 3.27 | no |
| LAT-P − LAT-P-reinit | -22.62 | [-24.37, -20.83] | 1.77 | 0.81 | YES |
| LAT-P − LAT-P-rand | -73.76 | [-75.26, -72.24] | 1.51 | 0.81 | YES |
| LAT-P-rand − LAT-P-reinit | +51.14 | [+48.96, +53.27] | 2.16 | 0.51 | YES |
| BN-G-matched − LAT-P-reinit | +36.00 | [+33.88, +38.12] | 2.12 | 1.18 | YES |
| BN-G-matched − LAT-G-det | +55.07 | [+53.52, +56.59] | 1.54 | 1.18 | YES |

## test_unseen at u3000

| arm | CER mean | per-seed | seed SD |
|---|---|---|---|
| BN-G | 73.32 | 72.76, 73.87 | 0.78 |
| LAT-G-det | 10.54 | 10.67, 10.41 | 0.18 |
| LAT-P | 6.05 | 7.03, 5.07 | 1.39 |
| BN-G-matched | 71.57 | 70.03, 73.11 | 2.18 |
| LAT-P-reinit | 29.08 | 29.68, 28.48 | 0.85 |
| LAT-P-rand | 91.36 | 91.33, 91.40 | 0.05 |

| contrast A − B | ΔCER | paired 95 % CI | half-width | 2 × max seed SD | G6 |
|---|---|---|---|---|---|
| BN-G-matched − BN-G | -1.75 | [-3.12, -0.23] | 1.44 | 4.37 | no |
| LAT-P − LAT-P-reinit | -23.03 | [-25.51, -20.78] | 2.37 | 2.77 | YES |
| LAT-P − LAT-P-rand | -85.32 | [-88.79, -82.26] | 3.26 | 2.77 | YES |
| LAT-P-rand − LAT-P-reinit | +62.29 | [+59.12, +65.55] | 3.21 | 1.70 | YES |
| BN-G-matched − LAT-P-reinit | +42.49 | [+39.74, +45.23] | 2.74 | 4.37 | YES |
| BN-G-matched − LAT-G-det | +61.03 | [+58.50, +63.78] | 2.64 | 4.37 | YES |
