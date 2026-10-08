# LAT-G-asp analysis (ASR `wav2vec2-xls-r-300m-bengali`)

Complete runs: BN-G 2/2, LAT-G-det 2/2, LAT-P 2/2, LAT-G-det-reinit 2/2, BN-G-iv-vm-asp 2/2, LAT-G-asp 2/2. Observations only.

## Fixed set CER % by update (mean of seeds)

| arm | u0 | u500 | u1000 | u2000 | u3000 |
|---|---|---|---|---|---|
| BN-G | 89.6 | 86.3 | 83.6 | 75.9 | 68.4 |
| LAT-G-det | 63.6 | 44.1 | 32.9 | 26.4 | 24.5 |
| LAT-P | 48.2 | 32.8 | 25.4 | 21.1 | 20.0 |
| LAT-G-det-reinit | 99.4 | 85.8 | 70.1 | 45.5 | 39.4 |
| BN-G-iv-vm-asp | 91.6 | 82.6 | 63.5 | 34.1 | 31.1 |
| LAT-G-asp | 58.7 | 40.9 | 29.8 | 25.4 | 23.7 |

## test_seen at u3000 (PRIMARY)

| arm | CER mean | per-seed | seed SD |
|---|---|---|---|
| BN-G | 65.46 | 64.86, 66.05 | 0.84 |
| LAT-G-det | 21.28 | 21.54, 21.03 | 0.36 |
| LAT-P | 18.36 | 18.67, 18.05 | 0.44 |
| LAT-G-det-reinit | 36.26 | 35.03, 37.48 | 1.73 |
| BN-G-iv-vm-asp | 27.42 | 26.48, 28.37 | 1.34 |
| LAT-G-asp | 20.27 | 20.15, 20.40 | 0.18 |

| contrast | ΔCER | paired 95 % CI | half-width | 2 × max seed SD | G6 |
|---|---|---|---|---|---|
| BN-G-iv-vm-asp − LAT-G-asp | +7.15 | [+5.84, +8.58] | 1.37 | 2.68 | YES |
| LAT-G-det − LAT-G-asp | +1.01 | [-0.07, +2.04] | 1.06 | 0.72 | no |
| LAT-P − LAT-G-asp | -1.91 | [-3.05, -0.78] | 1.14 | 0.89 | YES |
| (BN-G-iv-vm-asp − LAT-G-asp) − (LAT-G-det-reinit − LAT-G-det) | -7.82 | [-9.43, -6.23] | 1.60 | 3.45 | YES |

## test_unseen at u3000

| arm | CER mean | per-seed | seed SD |
|---|---|---|---|
| BN-G | 68.24 | 68.29, 68.20 | 0.07 |
| LAT-G-det | 22.84 | 23.34, 22.34 | 0.71 |
| LAT-P | 19.33 | 19.18, 19.49 | 0.22 |
| LAT-G-det-reinit | 38.69 | 38.11, 39.28 | 0.82 |
| BN-G-iv-vm-asp | 28.65 | 28.35, 28.96 | 0.43 |
| LAT-G-asp | 22.20 | 22.36, 22.04 | 0.22 |

| contrast | ΔCER | paired 95 % CI | half-width | 2 × max seed SD | G6 |
|---|---|---|---|---|---|
| BN-G-iv-vm-asp − LAT-G-asp | +6.45 | [+4.73, +8.26] | 1.76 | 0.86 | YES |
| LAT-G-det − LAT-G-asp | +0.64 | [-0.59, +1.85] | 1.22 | 1.41 | no |
| LAT-P − LAT-G-asp | -2.87 | [-4.26, -1.45] | 1.41 | 0.44 | YES |
| (BN-G-iv-vm-asp − LAT-G-asp) − (LAT-G-det-reinit − LAT-G-det) | -9.40 | [-11.30, -7.57] | 1.87 | 1.65 | YES |
