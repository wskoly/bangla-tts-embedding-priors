# Data-size curves (ASR `tugstugi_bengaliai-asr_whisper-medium`)

Fixed budget: 3000 updates at every size. Observations only.

Complete runs: BN-G@0.252h 2/2, LAT-G-det@0.252h 2/2, LAT-P@0.252h 2/2, BN-G-iv-vm-asp@0.252h 2/2, BN-G@0.5h 2/2, LAT-G-det@0.5h 2/2, LAT-P@0.5h 2/2, BN-G-iv-vm-asp@0.5h 2/2, BN-G@1.0h 2/2, LAT-G-det@1.0h 2/2, LAT-P@1.0h 2/2, BN-G-iv-vm-asp@1.0h 2/2, BN-G@1.58h 2/2, LAT-G-det@1.58h 2/2, LAT-P@1.58h 2/2, BN-G-iv-vm-asp@1.58h 2/2

## test_seen at u3000 (PRIMARY)

| arm | 0.252 h | 0.5 h | 1.0 h | 1.58 h |
|---|---|---|---|---|
| BN-G | 70.73 (±3.22) | 68.61 (±1.66) | 67.97 (±1.64) | 71.28 (±2.76) |
| LAT-G-det | 11.27 (±0.49) | 11.45 (±0.42) | 11.10 (±0.12) | 10.82 (±0.38) |
| LAT-P | 8.65 (±0.21) | 7.75 (±0.90) | 7.54 (±0.41) | 7.51 (±0.40) |
| BN-G-iv-vm-asp | 20.38 (±2.16) | 18.43 (±0.49) | 19.36 (±2.25) | 19.67 (±0.27) |

| size | contrast A − B | ΔCER | paired 95 % CI | half-width | 2 × max seed SD | G6 |
|---|---|---|---|---|---|---|
| 0.252 h | LAT-G-det − LAT-P | +2.62 | [+1.47, +3.72] | 1.12 | 0.98 | YES |
| 0.252 h | BN-G − LAT-G-det | +59.47 | [+57.79, +61.11] | 1.66 | 6.44 | YES |
| 0.252 h | BN-G-iv-vm-asp − BN-G | -50.35 | [-51.90, -48.73] | 1.59 | 6.44 | YES |
| 0.252 h | BN-G-iv-vm-asp − LAT-G-det | +9.11 | [+7.47, +10.68] | 1.61 | 4.32 | YES |
| 0.5 h | LAT-G-det − LAT-P | +3.70 | [+2.57, +4.84] | 1.13 | 1.81 | YES |
| 0.5 h | BN-G − LAT-G-det | +57.16 | [+55.51, +58.79] | 1.64 | 3.33 | YES |
| 0.5 h | BN-G-iv-vm-asp − BN-G | -50.18 | [-51.79, -48.56] | 1.62 | 3.33 | YES |
| 0.5 h | BN-G-iv-vm-asp − LAT-G-det | +6.98 | [+5.41, +8.56] | 1.57 | 0.98 | YES |
| 1.0 h | LAT-G-det − LAT-P | +3.56 | [+2.37, +4.63] | 1.13 | 0.81 | YES |
| 1.0 h | BN-G − LAT-G-det | +56.87 | [+55.33, +58.39] | 1.53 | 3.27 | YES |
| 1.0 h | BN-G-iv-vm-asp − BN-G | -48.61 | [-50.24, -46.89] | 1.68 | 4.50 | YES |
| 1.0 h | BN-G-iv-vm-asp − LAT-G-det | +8.26 | [+6.93, +9.66] | 1.36 | 4.50 | YES |
| 1.58 h | LAT-G-det − LAT-P | +3.31 | [+2.15, +4.43] | 1.14 | 0.80 | YES |
| 1.58 h | BN-G − LAT-G-det | +60.46 | [+58.95, +61.96] | 1.51 | 5.52 | YES |
| 1.58 h | BN-G-iv-vm-asp − BN-G | -51.61 | [-53.39, -49.82] | 1.78 | 5.52 | YES |
| 1.58 h | BN-G-iv-vm-asp − LAT-G-det | +8.85 | [+7.37, +10.31] | 1.47 | 0.76 | YES |

| scope | trend (A − B at 1.58 h) − (A − B at 0.25 h) | ΔΔCER | paired 95 % CI | half-width | 2 × max seed SD | G6 |
|---|---|---|---|---|---|---|
| trend | LAT-G-det − LAT-P | +0.70 | [-0.33, +1.79] | 1.06 | 0.98 | no |
| trend | BN-G-iv-vm-asp − LAT-G-det | -0.26 | [-1.78, +1.29] | 1.53 | 4.32 | no |

## test_unseen at u3000

| arm | 0.252 h | 0.5 h | 1.0 h | 1.58 h |
|---|---|---|---|---|
| BN-G | 77.05 (±5.23) | 72.85 (±0.80) | 73.32 (±0.78) | 77.33 (±1.41) |
| LAT-G-det | 12.01 (±0.48) | 10.96 (±0.95) | 10.54 (±0.18) | 10.84 (±0.38) |
| LAT-P | 6.19 (±1.05) | 5.56 (±0.20) | 6.05 (±1.39) | 5.57 (±0.58) |
| BN-G-iv-vm-asp | 18.09 (±2.52) | 14.64 (±0.01) | 16.88 (±1.73) | 15.62 (±1.69) |

| size | contrast A − B | ΔCER | paired 95 % CI | half-width | 2 × max seed SD | G6 |
|---|---|---|---|---|---|---|
| 0.252 h | LAT-G-det − LAT-P | +5.82 | [+4.51, +7.22] | 1.35 | 2.09 | YES |
| 0.252 h | BN-G − LAT-G-det | +65.04 | [+62.35, +68.10] | 2.87 | 10.46 | YES |
| 0.252 h | BN-G-iv-vm-asp − BN-G | -58.96 | [-61.86, -56.17] | 2.84 | 10.46 | YES |
| 0.252 h | BN-G-iv-vm-asp − LAT-G-det | +6.08 | [+4.17, +7.92] | 1.88 | 5.05 | YES |
| 0.5 h | LAT-G-det − LAT-P | +5.40 | [+3.92, +6.98] | 1.53 | 1.91 | YES |
| 0.5 h | BN-G − LAT-G-det | +61.89 | [+59.32, +64.68] | 2.68 | 1.91 | YES |
| 0.5 h | BN-G-iv-vm-asp − BN-G | -58.21 | [-60.79, -55.75] | 2.52 | 1.59 | YES |
| 0.5 h | BN-G-iv-vm-asp − LAT-G-det | +3.68 | [+1.82, +5.58] | 1.88 | 1.91 | YES |
| 1.0 h | LAT-G-det − LAT-P | +4.49 | [+3.21, +5.93] | 1.36 | 2.77 | YES |
| 1.0 h | BN-G − LAT-G-det | +62.78 | [+60.14, +65.55] | 2.70 | 1.57 | YES |
| 1.0 h | BN-G-iv-vm-asp − BN-G | -56.43 | [-59.02, -53.90] | 2.56 | 3.45 | YES |
| 1.0 h | BN-G-iv-vm-asp − LAT-G-det | +6.34 | [+4.42, +8.35] | 1.96 | 3.45 | YES |
| 1.58 h | LAT-G-det − LAT-P | +5.28 | [+3.94, +6.59] | 1.32 | 1.15 | YES |
| 1.58 h | BN-G − LAT-G-det | +66.48 | [+63.80, +69.56] | 2.88 | 2.82 | YES |
| 1.58 h | BN-G-iv-vm-asp − BN-G | -61.71 | [-64.19, -59.27] | 2.46 | 3.37 | YES |
| 1.58 h | BN-G-iv-vm-asp − LAT-G-det | +4.77 | [+2.92, +6.68] | 1.88 | 3.37 | YES |

| scope | trend (A − B at 1.58 h) − (A − B at 0.25 h) | ΔΔCER | paired 95 % CI | half-width | 2 × max seed SD | G6 |
|---|---|---|---|---|---|---|
| trend | LAT-G-det − LAT-P | -0.54 | [-1.72, +0.70] | 1.21 | 2.09 | no |
| trend | BN-G-iv-vm-asp − LAT-G-det | -1.31 | [-3.08, +0.51] | 1.79 | 5.05 | no |

