# Embedding-LR check (ASR `tugstugi_bengaliai-asr_whisper-medium`)

Complete runs: BN-G-matched 2/2, BN-G-matched-elr10 2/2, BN-G-iv-vm-asp 2/2, BN-G-iv-vm-asp-elr10 2/2, LAT-P-reinit 2/2, LAT-P-reinit-elr10 2/2, LAT-P 2/2. Observations only.

## Fixed set CER % by update (mean of seeds)

| arm | u0 | u500 | u1000 | u2000 | u3000 |
|---|---|---|---|---|---|
| BN-G-matched | 115.7 | 94.9 | 85.2 | 76.1 | 69.0 |
| BN-G-matched-elr10 | 115.7 | 94.5 | 90.5 | 70.8 | 62.0 |
| BN-G-iv-vm-asp | 107.5 | 86.6 | 67.8 | 25.3 | 21.2 |
| BN-G-iv-vm-asp-elr10 | 107.5 | 94.0 | 60.4 | 20.5 | 16.3 |
| LAT-P-reinit | 112.4 | 91.7 | 86.8 | 45.7 | 32.0 |
| LAT-P-reinit-elr10 | 112.4 | 94.5 | 86.3 | 36.9 | 23.3 |
| LAT-P | 38.2 | 21.6 | 14.1 | 9.1 | 8.0 |

## test_seen at u3000 (PRIMARY)

| arm | CER mean | per-seed | seed SD |
|---|---|---|---|
| BN-G-matched | 66.16 | 66.58, 65.75 | 0.59 |
| BN-G-matched-elr10 | 59.92 | 59.25, 60.59 | 0.95 |
| BN-G-iv-vm-asp | 19.36 | 17.77, 20.95 | 2.25 |
| BN-G-iv-vm-asp-elr10 | 15.66 | 15.94, 15.39 | 0.39 |
| LAT-P-reinit | 30.16 | 30.31, 30.01 | 0.22 |
| LAT-P-reinit-elr10 | 22.98 | 24.20, 21.77 | 1.72 |
| LAT-P | 7.54 | 7.83, 7.25 | 0.41 |

| contrast | ΔCER | paired 95 % CI | half-width | 2 × max seed SD | G6 |
|---|---|---|---|---|---|
| BN-G-matched-elr10 − BN-G-matched | -6.24 | [-7.36, -5.00] | 1.18 | 1.90 | YES |
| BN-G-iv-vm-asp-elr10 − BN-G-iv-vm-asp | -3.70 | [-4.58, -2.89] | 0.84 | 4.50 | no |
| LAT-P-reinit-elr10 − LAT-P-reinit | -7.18 | [-8.26, -6.08] | 1.09 | 3.44 | YES |
| BN-G-matched-elr10 − BN-G-iv-vm-asp-elr10 | +44.26 | [+42.46, +46.03] | 1.79 | 1.90 | YES |
| LAT-P-reinit-elr10 − LAT-P | +15.44 | [+13.75, +17.17] | 1.71 | 3.44 | YES |
| (BN-G-matched-elr10 − BN-G-iv-vm-asp-elr10) − (BN-G-matched − BN-G-iv-vm-asp) | -2.55 | [-3.94, -0.93] | 1.51 | 4.50 | no |

## test_unseen at u3000

| arm | CER mean | per-seed | seed SD |
|---|---|---|---|
| BN-G-matched | 71.57 | 70.03, 73.11 | 2.18 |
| BN-G-matched-elr10 | 63.29 | 63.42, 63.15 | 0.20 |
| BN-G-iv-vm-asp | 16.88 | 15.66, 18.10 | 1.73 |
| BN-G-iv-vm-asp-elr10 | 12.03 | 11.39, 12.67 | 0.90 |
| LAT-P-reinit | 29.08 | 29.68, 28.48 | 0.85 |
| LAT-P-reinit-elr10 | 20.71 | 21.63, 19.79 | 1.31 |
| LAT-P | 6.05 | 7.03, 5.07 | 1.39 |

| contrast | ΔCER | paired 95 % CI | half-width | 2 × max seed SD | G6 |
|---|---|---|---|---|---|
| BN-G-matched-elr10 − BN-G-matched | -8.28 | [-9.81, -6.91] | 1.45 | 4.37 | YES |
| BN-G-iv-vm-asp-elr10 − BN-G-iv-vm-asp | -4.85 | [-5.99, -3.74] | 1.12 | 3.45 | YES |
| LAT-P-reinit-elr10 − LAT-P-reinit | -8.37 | [-9.86, -6.91] | 1.47 | 2.62 | YES |
| BN-G-matched-elr10 − BN-G-iv-vm-asp-elr10 | +51.26 | [+48.78, +53.86] | 2.54 | 1.80 | YES |
| LAT-P-reinit-elr10 − LAT-P | +14.66 | [+12.78, +16.85] | 2.04 | 2.77 | YES |
| (BN-G-matched-elr10 − BN-G-iv-vm-asp-elr10) − (BN-G-matched − BN-G-iv-vm-asp) | -3.43 | [-5.39, -1.58] | 1.91 | 4.37 | no |
