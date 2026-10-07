# Pilot pilot_v1_1 analysis (ASR: `tugstugi_bengaliai-asr_whisper-medium`)

Runs complete: 6/6. Observations only, no claims.

## Fixed eval set (50 utts): CER % by update (mean over seeds; per-seed in brackets)

| arm | u0 | u500 | u1000 | u2000 | u3000 |
|---|---|---|---|---|---|
| BN-G | 105.2 [105.2, 105.2] | 93.3 [93.3, 93.3] | 90.4 [88.6, 92.1] | 79.6 [77.8, 81.4] | 71.5 [70.6, 72.4] |
| LAT-G-det | 64.5 [64.5, 64.5] | 37.6 [39.4, 35.8] | 22.6 [22.0, 23.2] | 13.8 [13.8, 13.7] | 11.4 [11.1, 11.8] |
| LAT-P | 38.2 [38.2, 38.2] | 21.6 [20.5, 22.7] | 14.1 [14.6, 13.6] | 9.1 [10.0, 8.2] | 8.0 [8.8, 7.2] |

## test_seen at update 3000 (PRIMARY)

| arm | CER mean | per-seed CER | seed SD |
|---|---|---|---|
| BN-G | 67.97 | 66.81, 69.12 | 1.64 |
| LAT-G-det | 11.10 | 11.01, 11.18 | 0.12 |
| LAT-P | 7.54 | 7.83, 7.25 | 0.41 |

| A − B | ΔCER | paired 95 % CI | CI half-width | 2 × max seed SD | G6 signal? |
|---|---|---|---|---|---|
| BN-G − LAT-G-det | +56.87 | [+55.33, +58.39] | 1.53 | 3.27 | YES |
| BN-G − LAT-P | +60.42 | [+59.03, +61.76] | 1.36 | 3.27 | YES |
| LAT-G-det − LAT-P | +3.56 | [+2.37, +4.63] | 1.13 | 0.81 | YES |

## test_unseen at update 3000

| arm | CER mean | per-seed CER | seed SD |
|---|---|---|---|
| BN-G | 73.32 | 72.76, 73.87 | 0.78 |
| LAT-G-det | 10.54 | 10.67, 10.41 | 0.18 |
| LAT-P | 6.05 | 7.03, 5.07 | 1.39 |

| A − B | ΔCER | paired 95 % CI | CI half-width | 2 × max seed SD | G6 signal? |
|---|---|---|---|---|---|
| BN-G − LAT-G-det | +62.78 | [+60.14, +65.55] | 2.70 | 1.57 | YES |
| BN-G − LAT-P | +67.27 | [+64.51, +70.25] | 2.87 | 2.77 | YES |
| LAT-G-det − LAT-P | +4.49 | [+3.21, +5.93] | 1.36 | 2.77 | YES |

## fixed_v1 at update 3000

| arm | CER mean | per-seed CER | seed SD |
|---|---|---|---|
| BN-G | 71.50 | 70.61, 72.38 | 1.25 |
| LAT-G-det | 11.42 | 11.08, 11.76 | 0.48 |
| LAT-P | 7.99 | 8.82, 7.16 | 1.17 |

| A − B | ΔCER | paired 95 % CI | CI half-width | 2 × max seed SD | G6 signal? |
|---|---|---|---|---|---|
| BN-G − LAT-G-det | +60.08 | [+57.05, +63.16] | 3.06 | 2.50 | YES |
| BN-G − LAT-P | +63.51 | [+60.96, +66.52] | 2.78 | 2.50 | YES |
| LAT-G-det − LAT-P | +3.43 | [+1.50, +5.35] | 1.93 | 2.34 | YES |

Notes: seed SD from n = 2 seeds is a weak variance estimate (NaN with one seed, so G6 cannot pass); ΔCER < 0 means A has lower CER.
G6 wording in D4 named the unseen-speaker set; D-013 made test_seen primary, so both are reported.
