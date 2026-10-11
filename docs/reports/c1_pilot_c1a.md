# C1 pilot (pilot_c1a): Rasa bn, seed 666, u3000

Pilot only (D-055/D-058): one seed, so no seed-SD gate; results do not change any setting. CER % = corpus ratio; 95 % CI = utterance bootstrap. *covered* = test utterances whose every word is in the LAT-P lexicon + supplement (no G2P); LAT-P arms are judged on it as primary (coverage rule triggered).

## Per arm (CER % [95 % CI])

| arm | ASR | seen all | seen covered | unseen all | unseen covered |
|---|---|---|---|---|---|
| LAT-P | Whisper | 6.26 [5.54, 6.97] | 5.58 [3.85, 7.82] | 9.62 [8.27, 10.87] | 7.25 [5.08, 9.46] |
| LAT-P | wav2vec2 | 16.41 [14.99, 17.96] | 11.55 [9.47, 13.89] | 19.74 [18.27, 21.14] | 15.72 [12.81, 18.64] |
| LAT-P-reinit | Whisper | 39.82 [38.20, 41.44] | 34.75 [30.93, 38.69] | 57.29 [54.43, 60.16] | 48.53 [41.14, 55.07] |
| LAT-P-reinit | wav2vec2 | 45.24 [43.90, 46.67] | 41.86 [37.90, 45.42] | 59.31 [57.00, 61.46] | 53.18 [47.37, 58.43] |
| LAT-P-rand | Whisper | 85.65 [84.49, 86.87] | 83.72 [81.36, 86.16] | 90.30 [88.24, 92.49] | 86.73 [82.91, 91.19] |
| LAT-P-rand | wav2vec2 | 81.03 [80.14, 81.91] | 79.05 [77.48, 80.65] | 83.15 [81.87, 84.54] | 81.92 [79.13, 84.75] |
| BN-G-matched | Whisper | 74.93 [73.82, 76.10] | 71.55 [68.78, 74.19] | 78.80 [77.12, 80.46] | 75.41 [71.27, 80.55] |
| BN-G-matched | wav2vec2 | 72.03 [71.07, 73.03] | 69.64 [67.84, 71.44] | 74.48 [73.31, 75.60] | 72.31 [69.12, 75.40] |
| BN-G-iv-vm-asp | Whisper | 23.40 [21.79, 25.04] | 16.61 [13.46, 20.03] | 33.80 [31.37, 36.16] | 27.93 [22.31, 33.33] |
| BN-G-iv-vm-asp | wav2vec2 | 29.37 [27.90, 30.74] | 22.86 [19.67, 26.11] | 38.76 [36.73, 40.65] | 32.33 [27.68, 36.47] |

n: test_seen all = 160, test_seen covered = 47, test_unseen all = 109, test_unseen covered = 30

## Paired contrasts (Δ CER, A − B [95 % CI]; predicted = C3 direction)

| contrast | A − B | predicted | ASR | seen all | seen covered | unseen all | unseen covered |
|---|---|---|---|---|---|---|---|
| H1a-like | LAT-P − LAT-P-reinit | < 0 | Whisper | -33.56 [-35.12, -31.90] | -29.16 [-33.51, -24.86] | -47.67 [-50.72, -44.61] | -41.29 [-47.58, -34.18] |
| H1a-like | LAT-P − LAT-P-reinit | < 0 | wav2vec2 | -28.83 [-30.37, -27.16] | -30.31 [-33.63, -26.93] | -39.57 [-41.78, -37.39] | -37.46 [-42.03, -32.28] |
| H2-like | LAT-P-rand − LAT-P-reinit | > 0 | Whisper | +45.83 [+44.03, +47.64] | +48.97 [+44.90, +53.29] | +33.01 [+30.31, +35.81] | +38.19 [+32.16, +44.77] |
| H2-like | LAT-P-rand − LAT-P-reinit | > 0 | wav2vec2 | +35.79 [+34.42, +37.30] | +37.18 [+33.97, +40.67] | +23.84 [+21.87, +25.95] | +28.75 [+24.47, +33.42] |
| H3b∧c-like | BN-G-matched − BN-G-iv-vm-asp | > 0 | Whisper | +51.53 [+49.85, +53.18] | +54.94 [+50.60, +59.27] | +45.00 [+43.09, +46.87] | +47.48 [+42.52, +52.19] |
| H3b∧c-like | BN-G-matched − BN-G-iv-vm-asp | > 0 | wav2vec2 | +42.67 [+41.34, +44.05] | +46.78 [+43.37, +50.28] | +35.72 [+34.17, +37.29] | +39.98 [+36.51, +43.82] |
