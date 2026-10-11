# ASR noise floor on real Rasa Bengali audio (C1, rasa_bn_v1)

Scoring normalization fixed in advance (see `src/eval/asr.py`, D-015). Corpus CER/WER = ratio of summed errors; 95 % CI = utterance bootstrap (2,000 resamples).

| model | split | n | CER % [95 % CI] | CER no-space % [95 % CI] | WER % [95 % CI] | utt CER mean / median / p90 | utt WER mean / median | % utts CER=0 | hyps with digits |
|---|---|---|---|---|---|---|---|---|---|
| tugstugi_bengaliai-asr_whisper-medium | test_seen | 160 | 2.77 [2.27, 3.29] | 2.59 [2.08, 3.15] | 14.97 [12.59, 17.54] | 2.90 / 1.47 / 7.58 | 15.73 / 10.82 | 33.8 | 0 |
| tugstugi_bengaliai-asr_whisper-medium | test_unseen | 110 | 3.27 [2.57, 4.03] | 3.21 [2.49, 4.03] | 15.50 [12.68, 18.24] | 2.87 / 1.87 / 7.69 | 13.60 / 11.11 | 34.5 | 0 |
| wav2vec2-xls-r-300m-bengali | test_seen | 160 | 11.17 [9.75, 12.77] | 11.25 [9.72, 12.95] | 41.65 [38.53, 44.75] | 10.34 / 8.71 / 20.00 | 39.08 / 38.46 | 8.8 | 16 |
| wav2vec2-xls-r-300m-bengali | test_unseen | 110 | 12.03 [10.73, 13.32] | 12.16 [10.66, 13.64] | 43.36 [39.72, 46.60] | 11.26 / 9.68 / 18.92 | 40.38 / 42.86 | 6.4 | 13 |

Per-utterance outputs (worst first): `data/derived/asr_floor_rasa_v1/<model>__<split>.tsv`.
