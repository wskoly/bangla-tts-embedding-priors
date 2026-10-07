# Pilot pilot_v1_1 analysis (ASR: `wav2vec2-xls-r-300m-bengali`)

Runs complete: 6/6. Observations only, no claims.

## Fixed eval set (50 utts): CER % by update (mean over seeds; per-seed in brackets)

| arm | u0 | u500 | u1000 | u2000 | u3000 |
|---|---|---|---|---|---|
| BN-G | 89.6 [89.6, 89.6] | 86.3 [85.8, 86.9] | 83.6 [83.0, 84.2] | 75.9 [74.9, 76.8] | 68.4 [68.0, 68.8] |
| LAT-G-det | 63.6 [63.6, 63.6] | 44.1 [45.3, 43.0] | 32.9 [33.0, 32.9] | 26.4 [26.5, 26.3] | 24.5 [25.1, 23.8] |
| LAT-P | 48.2 [48.2, 48.2] | 32.8 [31.7, 34.0] | 25.4 [25.5, 25.4] | 21.1 [22.0, 20.2] | 20.0 [20.3, 19.7] |

## test_seen at update 3000 (PRIMARY)

| arm | CER mean | per-seed CER | seed SD |
|---|---|---|---|
| BN-G | 65.46 | 64.86, 66.05 | 0.84 |
| LAT-G-det | 21.28 | 21.54, 21.03 | 0.36 |
| LAT-P | 18.36 | 18.67, 18.05 | 0.44 |

| A − B | ΔCER | paired 95 % CI | CI half-width | 2 × max seed SD | G6 signal? |
|---|---|---|---|---|---|
| BN-G − LAT-G-det | +44.17 | [+42.24, +45.99] | 1.88 | 1.68 | YES |
| BN-G − LAT-P | +47.10 | [+44.87, +49.14] | 2.13 | 1.68 | YES |
| LAT-G-det − LAT-P | +2.92 | [+1.73, +4.04] | 1.16 | 0.89 | YES |

## test_unseen at update 3000

| arm | CER mean | per-seed CER | seed SD |
|---|---|---|---|
| BN-G | 68.24 | 68.29, 68.20 | 0.07 |
| LAT-G-det | 22.84 | 23.34, 22.34 | 0.71 |
| LAT-P | 19.33 | 19.18, 19.49 | 0.22 |

| A − B | ΔCER | paired 95 % CI | CI half-width | 2 × max seed SD | G6 signal? |
|---|---|---|---|---|---|
| BN-G − LAT-G-det | +45.40 | [+42.21, +48.96] | 3.38 | 1.41 | YES |
| BN-G − LAT-P | +48.91 | [+45.52, +52.62] | 3.55 | 0.44 | YES |
| LAT-G-det − LAT-P | +3.50 | [+2.29, +4.70] | 1.20 | 1.41 | YES |

## fixed_v1 at update 3000

| arm | CER mean | per-seed CER | seed SD |
|---|---|---|---|
| BN-G | 68.37 | 67.97, 68.76 | 0.56 |
| LAT-G-det | 24.45 | 25.09, 23.81 | 0.91 |
| LAT-P | 20.03 | 20.31, 19.74 | 0.40 |

| A − B | ΔCER | paired 95 % CI | CI half-width | 2 × max seed SD | G6 signal? |
|---|---|---|---|---|---|
| BN-G − LAT-G-det | +43.91 | [+40.54, +47.41] | 3.44 | 1.81 | YES |
| BN-G − LAT-P | +48.34 | [+44.42, +52.37] | 3.97 | 1.12 | YES |
| LAT-G-det − LAT-P | +4.43 | [+2.55, +6.23] | 1.84 | 1.81 | YES |

Notes: seed SD from n = 2 seeds is a weak variance estimate (NaN with one seed, so G6 cannot pass); ΔCER < 0 means A has lower CER.
G6 wording in D4 named the unseen-speaker set; D-013 made test_seen primary, so both are reported.
