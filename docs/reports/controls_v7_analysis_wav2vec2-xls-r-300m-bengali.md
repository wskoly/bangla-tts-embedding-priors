# Embedding-LR check (ASR `wav2vec2-xls-r-300m-bengali`)

Complete runs: BN-G-matched 2/2, BN-G-matched-elr10 2/2, BN-G-iv-vm-asp 2/2, BN-G-iv-vm-asp-elr10 2/2, LAT-P-reinit 2/2, LAT-P-reinit-elr10 2/2, LAT-P 2/2. Observations only.

## Fixed set CER % by update (mean of seeds)

| arm | u0 | u500 | u1000 | u2000 | u3000 |
|---|---|---|---|---|---|
| BN-G-matched | 93.9 | 86.9 | 82.1 | 72.6 | 65.7 |
| BN-G-matched-elr10 | 93.9 | 85.6 | 83.6 | 68.5 | 59.0 |
| BN-G-iv-vm-asp | 91.6 | 82.6 | 63.5 | 34.1 | 31.1 |
| BN-G-iv-vm-asp-elr10 | 91.6 | 85.5 | 57.7 | 30.4 | 27.2 |
| LAT-P-reinit | 95.9 | 84.4 | 81.6 | 48.8 | 38.6 |
| LAT-P-reinit-elr10 | 95.9 | 86.3 | 79.1 | 42.4 | 34.9 |
| LAT-P | 48.2 | 32.8 | 25.4 | 21.1 | 20.0 |

## test_seen at u3000 (PRIMARY)

| arm | CER mean | per-seed | seed SD |
|---|---|---|---|
| BN-G-matched | 63.29 | 63.17, 63.41 | 0.16 |
| BN-G-matched-elr10 | 58.05 | 57.84, 58.26 | 0.30 |
| BN-G-iv-vm-asp | 27.42 | 26.48, 28.37 | 1.34 |
| BN-G-iv-vm-asp-elr10 | 24.75 | 24.87, 24.64 | 0.16 |
| LAT-P-reinit | 37.04 | 37.22, 36.85 | 0.26 |
| LAT-P-reinit-elr10 | 32.45 | 33.12, 31.79 | 0.94 |
| LAT-P | 18.36 | 18.67, 18.05 | 0.44 |

| contrast | ΔCER | paired 95 % CI | half-width | 2 × max seed SD | G6 |
|---|---|---|---|---|---|
| BN-G-matched-elr10 − BN-G-matched | -5.24 | [-6.21, -4.31] | 0.95 | 0.60 | YES |
| BN-G-iv-vm-asp-elr10 − BN-G-iv-vm-asp | -2.67 | [-3.47, -1.88] | 0.79 | 2.68 | no |
| LAT-P-reinit-elr10 − LAT-P-reinit | -4.59 | [-5.45, -3.77] | 0.84 | 1.88 | YES |
| BN-G-matched-elr10 − BN-G-iv-vm-asp-elr10 | +33.30 | [+31.27, +35.34] | 2.03 | 0.60 | YES |
| LAT-P-reinit-elr10 − LAT-P | +14.09 | [+12.40, +15.82] | 1.71 | 1.88 | YES |
| (BN-G-matched-elr10 − BN-G-iv-vm-asp-elr10) − (BN-G-matched − BN-G-iv-vm-asp) | -2.56 | [-3.85, -1.24] | 1.30 | 2.68 | no |

## test_unseen at u3000

| arm | CER mean | per-seed | seed SD |
|---|---|---|---|
| BN-G-matched | 67.16 | 65.40, 68.92 | 2.48 |
| BN-G-matched-elr10 | 60.32 | 59.45, 61.19 | 1.23 |
| BN-G-iv-vm-asp | 28.65 | 28.35, 28.96 | 0.43 |
| BN-G-iv-vm-asp-elr10 | 25.20 | 25.26, 25.15 | 0.08 |
| LAT-P-reinit | 38.32 | 39.18, 37.46 | 1.22 |
| LAT-P-reinit-elr10 | 31.91 | 32.58, 31.23 | 0.95 |
| LAT-P | 19.33 | 19.18, 19.49 | 0.22 |

| contrast | ΔCER | paired 95 % CI | half-width | 2 × max seed SD | G6 |
|---|---|---|---|---|---|
| BN-G-matched-elr10 − BN-G-matched | -6.84 | [-7.96, -5.78] | 1.09 | 4.97 | YES |
| BN-G-iv-vm-asp-elr10 − BN-G-iv-vm-asp | -3.45 | [-4.51, -2.43] | 1.04 | 0.86 | YES |
| LAT-P-reinit-elr10 − LAT-P-reinit | -6.42 | [-7.63, -5.30] | 1.17 | 2.43 | YES |
| BN-G-matched-elr10 − BN-G-iv-vm-asp-elr10 | +35.11 | [+32.19, +38.12] | 2.97 | 2.46 | YES |
| LAT-P-reinit-elr10 − LAT-P | +12.57 | [+10.87, +14.52] | 1.83 | 1.91 | YES |
| (BN-G-matched-elr10 − BN-G-iv-vm-asp-elr10) − (BN-G-matched − BN-G-iv-vm-asp) | -3.39 | [-4.91, -1.87] | 1.52 | 4.97 | no |
