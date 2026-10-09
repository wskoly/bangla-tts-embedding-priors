# Data-size curves (ASR `wav2vec2-xls-r-300m-bengali`)

Fixed budget: 3000 updates at every size. Observations only.

Complete runs: BN-G@0.252h 2/2, LAT-G-det@0.252h 2/2, LAT-P@0.252h 2/2, BN-G-iv-vm-asp@0.252h 2/2, BN-G@0.5h 2/2, LAT-G-det@0.5h 2/2, LAT-P@0.5h 2/2, BN-G-iv-vm-asp@0.5h 2/2, BN-G@1.0h 2/2, LAT-G-det@1.0h 2/2, LAT-P@1.0h 2/2, BN-G-iv-vm-asp@1.0h 2/2, BN-G@1.58h 2/2, LAT-G-det@1.58h 2/2, LAT-P@1.58h 2/2, BN-G-iv-vm-asp@1.58h 2/2

## test_seen at u3000 (PRIMARY)

| arm | 0.252 h | 0.5 h | 1.0 h | 1.58 h |
|---|---|---|---|---|
| BN-G | 68.11 (±1.59) | 66.08 (±2.03) | 65.46 (±0.84) | 67.86 (±2.51) |
| LAT-G-det | 21.44 (±0.32) | 21.26 (±0.94) | 21.28 (±0.36) | 21.50 (±0.12) |
| LAT-P | 19.57 (±0.38) | 19.01 (±0.14) | 18.36 (±0.44) | 18.57 (±0.40) |
| BN-G-iv-vm-asp | 27.99 (±1.09) | 26.52 (±0.73) | 27.42 (±1.34) | 27.63 (±0.14) |

| size | contrast A − B | ΔCER | paired 95 % CI | half-width | 2 × max seed SD | G6 |
|---|---|---|---|---|---|---|
| 0.252 h | LAT-G-det − LAT-P | +1.87 | [+0.58, +3.07] | 1.25 | 0.76 | YES |
| 0.252 h | BN-G − LAT-G-det | +46.67 | [+44.59, +48.55] | 1.98 | 3.18 | YES |
| 0.252 h | BN-G-iv-vm-asp − BN-G | -40.13 | [-41.85, -38.27] | 1.79 | 3.18 | YES |
| 0.252 h | BN-G-iv-vm-asp − LAT-G-det | +6.54 | [+5.15, +8.00] | 1.43 | 2.17 | YES |
| 0.5 h | LAT-G-det − LAT-P | +2.25 | [+1.06, +3.37] | 1.15 | 1.88 | YES |
| 0.5 h | BN-G − LAT-G-det | +44.82 | [+42.84, +46.76] | 1.96 | 4.05 | YES |
| 0.5 h | BN-G-iv-vm-asp − BN-G | -39.56 | [-41.29, -37.74] | 1.77 | 4.05 | YES |
| 0.5 h | BN-G-iv-vm-asp − LAT-G-det | +5.26 | [+4.02, +6.57] | 1.28 | 1.88 | YES |
| 1.0 h | LAT-G-det − LAT-P | +2.92 | [+1.73, +4.04] | 1.16 | 0.89 | YES |
| 1.0 h | BN-G − LAT-G-det | +44.17 | [+42.24, +45.99] | 1.88 | 1.68 | YES |
| 1.0 h | BN-G-iv-vm-asp − BN-G | -38.03 | [-39.73, -36.21] | 1.76 | 2.68 | YES |
| 1.0 h | BN-G-iv-vm-asp − LAT-G-det | +6.14 | [+4.95, +7.37] | 1.21 | 2.68 | YES |
| 1.58 h | LAT-G-det − LAT-P | +2.92 | [+1.79, +4.02] | 1.12 | 0.80 | YES |
| 1.58 h | BN-G − LAT-G-det | +46.36 | [+44.56, +48.02] | 1.73 | 5.03 | YES |
| 1.58 h | BN-G-iv-vm-asp − BN-G | -40.22 | [-41.95, -38.43] | 1.76 | 5.03 | YES |
| 1.58 h | BN-G-iv-vm-asp − LAT-G-det | +6.14 | [+4.95, +7.35] | 1.20 | 0.27 | YES |

| scope | trend (A − B at 1.58 h) − (A − B at 0.25 h) | ΔΔCER | paired 95 % CI | half-width | 2 × max seed SD | G6 |
|---|---|---|---|---|---|---|
| trend | LAT-G-det − LAT-P | +1.05 | [-0.11, +2.25] | 1.18 | 0.80 | no |
| trend | BN-G-iv-vm-asp − LAT-G-det | -0.40 | [-1.57, +0.80] | 1.19 | 2.17 | no |

## test_unseen at u3000

| arm | 0.252 h | 0.5 h | 1.0 h | 1.58 h |
|---|---|---|---|---|
| BN-G | 72.31 (±4.82) | 68.23 (±1.31) | 68.24 (±0.07) | 71.62 (±1.44) |
| LAT-G-det | 24.13 (±0.03) | 23.21 (±0.65) | 22.84 (±0.71) | 23.18 (±0.22) |
| LAT-P | 19.78 (±0.67) | 19.14 (±0.24) | 19.33 (±0.22) | 18.92 (±0.10) |
| BN-G-iv-vm-asp | 29.03 (±1.88) | 27.00 (±0.73) | 28.65 (±0.43) | 28.00 (±1.79) |

| size | contrast A − B | ΔCER | paired 95 % CI | half-width | 2 × max seed SD | G6 |
|---|---|---|---|---|---|---|
| 0.252 h | LAT-G-det − LAT-P | +4.35 | [+3.06, +5.75] | 1.35 | 1.33 | YES |
| 0.252 h | BN-G − LAT-G-det | +48.18 | [+45.14, +51.21] | 3.03 | 9.65 | YES |
| 0.252 h | BN-G-iv-vm-asp − BN-G | -43.28 | [-46.22, -40.34] | 2.94 | 9.65 | YES |
| 0.252 h | BN-G-iv-vm-asp − LAT-G-det | +4.90 | [+3.11, +6.74] | 1.82 | 3.76 | YES |
| 0.5 h | LAT-G-det − LAT-P | +4.07 | [+2.61, +5.51] | 1.45 | 1.31 | YES |
| 0.5 h | BN-G − LAT-G-det | +45.03 | [+41.97, +48.12] | 3.07 | 2.62 | YES |
| 0.5 h | BN-G-iv-vm-asp − BN-G | -41.23 | [-44.17, -38.11] | 3.03 | 2.62 | YES |
| 0.5 h | BN-G-iv-vm-asp − LAT-G-det | +3.79 | [+2.10, +5.57] | 1.74 | 1.47 | YES |
| 1.0 h | LAT-G-det − LAT-P | +3.50 | [+2.29, +4.70] | 1.20 | 1.41 | YES |
| 1.0 h | BN-G − LAT-G-det | +45.40 | [+42.21, +48.96] | 3.38 | 1.41 | YES |
| 1.0 h | BN-G-iv-vm-asp − BN-G | -39.59 | [-42.46, -36.81] | 2.82 | 0.86 | YES |
| 1.0 h | BN-G-iv-vm-asp − LAT-G-det | +5.81 | [+4.04, +7.60] | 1.78 | 1.41 | YES |
| 1.58 h | LAT-G-det − LAT-P | +4.26 | [+3.22, +5.40] | 1.09 | 0.44 | YES |
| 1.58 h | BN-G − LAT-G-det | +48.44 | [+45.16, +51.88] | 3.36 | 2.88 | YES |
| 1.58 h | BN-G-iv-vm-asp − BN-G | -43.61 | [-46.60, -40.58] | 3.01 | 3.58 | YES |
| 1.58 h | BN-G-iv-vm-asp − LAT-G-det | +4.83 | [+3.16, +6.47] | 1.65 | 3.58 | YES |

| scope | trend (A − B at 1.58 h) − (A − B at 0.25 h) | ΔΔCER | paired 95 % CI | half-width | 2 × max seed SD | G6 |
|---|---|---|---|---|---|---|
| trend | LAT-G-det − LAT-P | -0.09 | [-1.22, +1.02] | 1.12 | 1.33 | no |
| trend | BN-G-iv-vm-asp − LAT-G-det | -0.07 | [-1.76, +1.44] | 1.60 | 3.76 | no |

