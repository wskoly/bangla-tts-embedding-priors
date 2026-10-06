# ASR noise floor on real SLR37 audio

Scoring normalization fixed in advance (see `src/eval/asr.py`, D-015). Corpus CER/WER = ratio of summed errors; 95 % CI = utterance bootstrap (2,000 resamples).

| model | split | n | CER % [95 % CI] | CER no-space % [95 % CI] | WER % [95 % CI] | utt CER mean / median / p90 | utt WER mean / median | % utts CER=0 | hyps with digits |
|---|---|---|---|---|---|---|---|---|---|
| tugstugi_bengaliai-asr_whisper-medium | test_seen | 163 | 1.93 [1.54, 2.33] | 1.58 [1.22, 1.95] | 10.69 [8.59, 12.92] | 1.77 / 0.00 / 4.88 | 9.60 / 0.00 | 59.5 | 0 |
| tugstugi_bengaliai-asr_whisper-medium | test_unseen | 110 | 2.02 [1.55, 2.51] | 1.41 [1.01, 1.82] | 12.76 [9.86, 15.95] | 1.92 / 0.00 / 4.88 | 11.02 / 0.00 | 54.5 | 0 |
| tugstugi_bengaliai-asr_whisper-medium | val | 50 | 1.79 [1.13, 2.49] | 1.45 [0.92, 2.01] | 9.69 [6.04, 13.61] | 1.71 / 0.00 / 4.76 | 9.00 / 0.00 | 58.0 | 0 |
| wav2vec2-xls-r-300m-bengali | test_seen | 163 | 12.80 [10.93, 14.76] | 12.01 [10.06, 14.03] | 44.73 [41.06, 48.46] | 10.63 / 8.20 / 22.58 | 41.57 / 42.86 | 13.5 | 31 |
| wav2vec2-xls-r-300m-bengali | test_unseen | 110 | 15.79 [12.74, 18.91] | 15.13 [12.08, 18.32] | 50.81 [45.21, 56.01] | 13.01 / 8.97 / 28.89 | 45.52 / 50.00 | 13.6 | 26 |
| wav2vec2-xls-r-300m-bengali | val | 50 | 15.55 [11.95, 19.28] | 14.96 [11.06, 18.87] | 48.47 [42.09, 53.99] | 13.25 / 10.79 / 29.49 | 44.39 / 43.65 | 10.0 | 13 |

Per-utterance outputs (worst first): `data/derived/asr_floor_v1/<model>__<split>.tsv`.
