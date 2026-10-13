# C5 causal controls (D-067)

Plan: `docs/C5_analysis_plan.md` (frozen before the runs). Whisper test_seen u3000, SLR37 train_1h.

## C5a: fresh-row initialization seed

| test | Δ [95% CI] | half | 2σ (C3) | w2v Δ | verdict |
|---|---|---|---|---|---|
| C5a-H1a-1001 | -16.97 [-18.76, -15.08] | 1.84 | 1.18 | -13.85 | pass |
| C5a-H3path-1001 | +28.06 [+26.01, +30.24] | 2.12 | 3.23 | +22.05 | pass |
| C5a-H1a-1002 | -66.90 [-68.41, -65.27] | 1.57 | 1.18 | -52.40 | pass |
| C5a-H3path-1002 | +37.58 [+35.50, +39.65] | 2.08 | 3.23 | +31.08 | pass |

Spread of the fresh-row arms (CER %, Whisper test_seen):

| arm | init seeds 666 / 1001 / 1002 (train seed 666) | SD | train seeds 666 / 1234 / 4242 (init 666) | SD |
|---|---|---|---|---|
| BN-G-matched | 66.58 / 56.18 / 79.38 | 11.62 | 66.58 / 65.75 / 67.97 | 1.12 |
| LAT-P-reinit | 30.31 / 24.80 / 74.73 | 27.37 | 30.31 / 30.01 / 29.18 | 0.59 |
| BN-G-iv-vm-asp | 17.77 / 28.11 / 41.80 | 12.06 | 17.77 / 20.95 / 18.89 | 1.62 |

## C5b: choice of scrambled alphabet (H2)

| test | Δ [95% CI] | half | 2σ | w2v Δ | verdict |
|---|---|---|---|---|---|
| C5b-H2-2 | +54.24 [+52.18, +56.33] | 2.08 | 1.57 | +43.23 | pass |
| C5b-H2-3 | +52.89 [+50.88, +54.93] | 2.02 | 1.56 | +42.68 | pass |

CER of every derangement (Whisper test_seen, training seeds 666 / 1234):

- LAT-P-rand: 81.12 / 81.48
- LAT-P-rand2: 83.84 / 84.96
- LAT-P-rand3: 82.50 / 83.60
