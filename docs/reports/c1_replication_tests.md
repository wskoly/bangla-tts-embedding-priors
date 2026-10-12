# C1 replication tests (D-061)

Plan: `docs/C1_analysis_plan.md` (frozen before the full runs). Corpus: Rasa bn (neutral), train_1h rasaF. Primary: Whisper test_seen u3000, mean of seeds 666/1234/4242; H1a/H2 primary on the coverage-restricted subset. Gate G6 as in C3.

## Arms (Whisper test_seen CER, per seed)

| arm | all (n=160): mean (per seed) | SD | covered: mean (per seed) | SD |
|---|---|---|---|---|
| LAT-P | 6.10 (6.26, 5.86, 6.19) | 0.21 | 4.95 (5.58, 4.58, 4.68) | 0.55 |
| LAT-P-reinit | 39.45 (39.82, 38.30, 40.22) | 1.01 | 34.11 (34.75, 32.74, 34.85) | 1.19 |
| LAT-P-rand | 83.82 (85.65, 83.37, 82.43) | 1.65 | 80.99 (83.72, 79.71, 79.52) | 2.37 |
| BN-G-matched | 71.83 (74.93, 72.35, 68.21) | 3.39 | 68.02 (71.55, 67.64, 64.87) | 3.36 |
| BN-G-iv-vm-asp | 25.74 (23.40, 25.74, 28.07) | 2.34 | 19.33 (16.61, 19.67, 21.72) | 2.57 |
| LAT-G-det | 12.63 (12.45, 12.53, 12.92) | 0.25 | 11.39 (11.50, 11.12, 11.55) | 0.24 |
| LAT-G-det-reinit | 36.37 (35.04, 38.63, 35.43) | 1.97 | 31.31 (30.02, 34.03, 29.88) | 2.36 |
| LAT-G-asp | 14.88 (14.93, 14.67, 15.04) | 0.19 | 10.85 (11.93, 10.69, 9.93) | 1.01 |

## Tests

| id | contrast | predicted | primary subset | Δ primary [95 % CI] | half | 2×SD | wav2vec2 Δ | Whisper Δ other subset | Whisper unseen Δ (all / covered) | wav2vec2 unseen Δ (all / covered) | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| H1a | LAT-P − LAT-P-reinit | < 0 | covered | -29.16 [-32.74, -25.15] | 3.79 | 2.37 | -29.21 | -33.35 | -46.69 / -41.29 | -38.65 / -35.64 | replicated |
| H1b | LAT-G-det − LAT-G-det-reinit | < 0 | all | -23.73 [-25.17, -22.20] | 1.49 | 3.93 | -18.32 | -19.92 | -28.54 / -23.13 | -22.35 / -20.19 | replicated |
| H2 | LAT-P-rand − LAT-P-reinit | > 0 | covered | +46.87 [+43.70, +50.46] | 3.38 | 4.74 | +37.20 | +44.37 | +32.50 / +38.55 | +24.13 / +30.16 | replicated |
| H3-path | BN-G-matched − BN-G-iv-vm-asp | > 0 | all | +46.09 [+44.75, +47.45] | 1.35 | 6.78 | +38.62 | +48.69 | +41.02 / +44.41 | +32.12 / +37.11 | replicated |
| H4 | (BN-G-iv-vm-asp − LAT-G-asp) − (LAT-G-det-reinit − LAT-G-det) | < 0 | all | -12.88 [-14.43, -11.33] | 1.55 | 4.67 | -9.66 | -11.44 | -12.40 / -7.60 | -9.25 / -8.39 | replicated |

Hypothesis-level: H1 = H1a ∧ H1b; H2; H3-path; H4. 5 tests, no correction beyond G6.
