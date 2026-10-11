# C3 hypothesis tests (D-046)

Plan: `docs/C3_analysis_plan.md` (frozen before runs). Primary: Whisper test_seen u3000. Observations on SLR37 (same data as exploration): robustness, not replication.

## Arms

| arm | seeds | Whisper seen CER (per seed) | SD |
|---|---|---|---|
| LAT-P | 3 | 7.79 (7.83, 7.25, 8.29) | 0.52 |
| LAT-G-det | 3 | 12.39 (11.01, 11.18, 14.99) | 2.25 |
| LAT-P-reinit | 3 | 29.83 (30.31, 30.01, 29.18) | 0.59 |
| LAT-P-rand | 3 | 81.37 (81.12, 81.48, 81.50) | 0.21 |
| BN-G-matched | 3 | 66.76 (66.58, 65.75, 67.97) | 1.12 |
| LAT-G-det-reinit | 3 | 30.51 (28.28, 32.91, 30.34) | 2.32 |
| BN-G-iv | 3 | 62.78 (65.08, 62.88, 60.39) | 2.35 |
| BN-G-iv-vm | 3 | 49.93 (52.11, 48.35, 49.33) | 1.95 |
| BN-G-iv-vm-asp | 3 | 19.20 (17.77, 20.95, 18.89) | 1.62 |
| LAT-G-asp | 3 | 10.57 (10.22, 10.35, 11.15) | 0.51 |
| BN-G-matched-elr3 | 2 | 66.54 (65.73, 67.34) | 1.14 |
| BN-G-iv-vm-asp-elr3 | 2 | 18.28 (18.12, 18.44) | 0.23 |
| LAT-P-reinit-elr3 | 2 | 28.20 (27.82, 28.57) | 0.53 |
| BN-G-matched-elr10 | 2 | 59.92 (59.25, 60.59) | 0.95 |
| BN-G-iv-vm-asp-elr10 | 2 | 15.66 (15.94, 15.39) | 0.39 |
| LAT-P-reinit-elr10 | 2 | 22.98 (24.20, 21.77) | 1.72 |
| BN-G-matched-elr30 | 2 | 44.40 (45.47, 43.32) | 1.52 |
| BN-G-iv-vm-asp-elr30 | 2 | 12.92 (12.46, 13.38) | 0.65 |
| LAT-P-reinit-elr30 | 2 | 14.36 (15.52, 13.20) | 1.64 |

## Tests

| id | contrast | predicted | Δ primary [95 % CI] | half | 2×SD | wav2vec2 seen Δ | Whisper unseen Δ | wav2vec2 unseen Δ | verdict |
|---|---|---|---|---|---|---|---|---|---|
| H1a | LAT-P − LAT-P-reinit | < 0 | -22.04 [-23.74, -20.32] | 1.71 | 1.18 | -18.46 | -22.86 | -18.28 | supported |
| H1b | LAT-G-det − LAT-G-det-reinit | < 0 | -18.12 [-19.78, -16.65] | 1.57 | 4.64 | -13.77 | -17.92 | -13.22 | supported |
| H1c-x3 | LAT-P − LAT-P-reinit-elr3 | < 0 | -20.41 [-22.32, -18.62] | 1.85 | 1.07 | -17.45 | -21.88 | -17.46 | supported |
| H1c-x10 | LAT-P − LAT-P-reinit-elr10 | < 0 | -15.20 [-16.92, -13.54] | 1.69 | 3.44 | -13.81 | -14.72 | -12.13 | supported |
| H1c-x30 | LAT-P − LAT-P-reinit-elr30 | < 0 | -6.57 [-7.94, -5.28] | 1.33 | 3.27 | -7.35 | -6.63 | -6.14 | supported |
| H2 | LAT-P-rand − LAT-P-reinit | > 0 | +51.53 [+49.45, +53.52] | 2.03 | 1.18 | +40.84 | +62.88 | +46.66 | supported |
| H3a | BN-G-matched − BN-G-iv | |Δ| ≤ 5 | +3.98 [+2.87, +5.13] | 1.13 | 4.70 | +2.13 | +7.90 | +5.04 | inconclusive |
| H3b | BN-G-iv − BN-G-iv-vm | > 0 | +12.85 [+11.61, +14.10] | 1.24 | 4.70 | +10.95 | +13.95 | +10.72 | supported |
| H3c | BN-G-iv-vm − BN-G-iv-vm-asp | > 0 | +30.73 [+29.10, +32.33] | 1.62 | 3.90 | +23.47 | +32.56 | +22.39 | supported |
| H4 | (BN-G-iv-vm-asp − LAT-G-asp) − (LAT-G-det-reinit − LAT-G-det) | < 0 | -9.49 [-11.23, -7.86] | 1.68 | 4.64 | -7.26 | -11.06 | -6.04 | supported |
| H5-x3 | BN-G-matched-elr3 − BN-G-iv-vm-asp-elr3 | > 0 | +48.25 [+46.46, +49.98] | 1.76 | 2.28 | +37.43 | +54.83 | +38.99 | supported |
| H5-x10 | BN-G-matched-elr10 − BN-G-iv-vm-asp-elr10 | > 0 | +44.26 [+42.46, +46.03] | 1.79 | 1.90 | +33.30 | +51.26 | +35.11 | supported |
| H5-x30 | BN-G-matched-elr30 − BN-G-iv-vm-asp-elr30 | > 0 | +31.48 [+29.73, +33.14] | 1.71 | 3.04 | +23.38 | +34.77 | +23.70 | supported |

Hypothesis-level: H1 = H1a ∧ H1b ∧ H1c-x3/x10/x30; H2; H3 = H3a ∧ H3b ∧ H3c; H4; H5 (LR stability) = H5-x3/x10/x30 ∧ H1c-x3/x10/x30 all supported with the same sign.
