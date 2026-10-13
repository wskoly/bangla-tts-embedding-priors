# Letter-prior confusions (D-076; post hoc, exploratory)

Whisper transcripts, test_seen, 3,000 updates, all training seeds pooled (SLR37: 3 seeds, C3 runs; Rasa: 3 seeds, C1 runs; Rasa uses all seen sentences, including words filled by G2P for LAT-P). *sub*: share of reference words containing the source letter whose substituted form appears in the hypothesis. *ok*: share recovered exactly. *floor*: ASR on the real recordings. Word matching is exact and order-free, so *sub* is a lower bound on the confusion. The pairs were fixed before any rate was computed. Twin differences (pretrained minus fresh rows on identical text) carry a 95 % bootstrap interval over sentences (2000 resamples). Not corrected for multiple comparisons.

## SLR37

### Substitution rate *sub* % (n reference words)

| pair | motivated by | LAT-P | LAT-P-reinit | LAT-G-det | LAT-G-det-reinit | LAT-G-asp | BN-G-iv-vm-asp | BN-G-matched | floor |
|---|---|---|---|---|---|---|---|---|---|
| চ→ক (n=88) | LAT-P / LAT-G-asp `c` (English /k/); ITRANS `ch` | 8.0 | 0.0 | 0.0 | 0.0 | 2.3 | 0.4 | 0.0 | 0.0 |
| থ→ত (n=75) | `th` in all Latin arms (English /θ/) | 0.0 | 0.9 | 0.0 | 0.4 | 0.0 | 1.8 | 0.0 | 0.0 |
| খ→ক (n=29) | control: generic loss of aspiration; `kh` has no English clash | 0.0 | 0.0 | 1.1 | 0.0 | 4.6 | 0.0 | 2.3 | 0.0 |
| ছ→চ (n=53) | ITRANS `Ch` vs `ch` (case); LAT-P / LAT-G-asp `ch` (English /tʃ/ = চ) | 0.0 | 0.0 | 0.6 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| ট→ত (n=127) | LAT-P / ITRANS `T` vs `t` (case); LAT-G-asp `ṭ` | 2.9 | 0.8 | 1.8 | 1.3 | 2.9 | 0.5 | 0.0 | 0.0 |
| ড→দ (n=115) | LAT-P / ITRANS `D` vs `d` (case); LAT-G-asp `ḍ` | 4.1 | 1.7 | 3.2 | 4.6 | 2.0 | 1.4 | 0.0 | 0.0 |
| ত→ট (n=172) | reverse of `T`/`t` | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.2 | 0.0 |
| দ→ড (n=121) | reverse of `D`/`d` | 0.0 | 0.3 | 0.0 | 0.0 | 0.0 | 0.0 | 0.3 | 0.0 |
| ব→ভ (n=191) | ITRANS `v` (English /v/) | 0.2 | 0.0 | 0.3 | 0.2 | 0.5 | 0.0 | 0.0 | 0.0 |
| ং→ন (n=47) | LAT-P `N` vs `n` (case) | 2.8 | 0.0 | 0.0 | 0.0 | 0.7 | 0.0 | 0.0 | 0.0 |

### Exact recovery *ok* % of words containing the source letter

| letter | LAT-P | LAT-P-reinit | LAT-G-det | LAT-G-det-reinit | LAT-G-asp | BN-G-iv-vm-asp | BN-G-matched | floor |
|---|---|---|---|---|---|---|---|---|
| চ | 64.4 | 43.9 | 73.1 | 41.7 | 65.9 | 50.8 | 2.7 | 93.2 |
| থ | 88.9 | 74.2 | 77.8 | 74.2 | 84.4 | 76.9 | 3.6 | 100.0 |
| খ | 74.7 | 44.8 | 66.7 | 47.1 | 63.2 | 65.5 | 5.7 | 96.6 |
| ছ | 87.4 | 57.9 | 76.7 | 46.5 | 86.8 | 70.4 | 23.3 | 94.3 |
| ট | 69.6 | 26.0 | 65.4 | 23.6 | 62.2 | 46.5 | 1.6 | 89.0 |
| ড | 56.2 | 31.6 | 43.5 | 13.6 | 58.3 | 37.4 | 0.3 | 77.4 |
| ত | 81.6 | 54.3 | 63.2 | 46.3 | 74.8 | 59.5 | 2.5 | 93.0 |
| দ | 80.7 | 29.2 | 70.5 | 56.2 | 72.5 | 60.1 | 11.6 | 90.1 |
| ব | 78.5 | 38.9 | 65.3 | 33.3 | 68.4 | 53.2 | 4.4 | 89.0 |
| ং | 80.1 | 22.0 | 72.3 | 31.2 | 72.3 | 62.4 | 11.3 | 95.7 |

### Pretrained minus fresh rows on identical text: *sub* difference, pp [95 % CI]

| pair | LAT-P − LAT-P-reinit | LAT-G-det − LAT-G-det-reinit |
|---|---|---|
| চ→ক | +8.0 [+4.1, +12.4] | +0.0 [+0.0, +0.0] |
| থ→ত | -0.9 [-2.4, +0.0] | -0.4 [-1.4, +0.0] |
| খ→ক | +0.0 [+0.0, +0.0] | +1.1 [+0.0, +3.7] |
| ছ→চ | +0.0 [+0.0, +0.0] | +0.6 [+0.0, +2.0] |
| ট→ত | +2.1 [+0.5, +3.9] | +0.5 [-1.8, +2.8] |
| ড→দ | +2.3 [-1.2, +6.2] | -1.4 [-4.9, +2.0] |
| ত→ট | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] |
| দ→ড | -0.3 [-0.9, +0.0] | +0.0 [+0.0, +0.0] |
| ব→ভ | +0.2 [+0.0, +0.6] | +0.2 [-0.5, +1.1] |
| ং→ন | +2.8 [+0.0, +8.3] | +0.0 [+0.0, +0.0] |

## Rasa

### Substitution rate *sub* % (n reference words)

| pair | motivated by | LAT-P | LAT-P-reinit | LAT-G-det | LAT-G-det-reinit | LAT-G-asp | BN-G-iv-vm-asp | BN-G-matched | floor |
|---|---|---|---|---|---|---|---|---|---|
| চ→ক (n=101) | LAT-P / LAT-G-asp `c` (English /k/); ITRANS `ch` | 5.9 | 0.3 | 1.3 | 0.3 | 4.6 | 0.0 | 0.0 | 0.0 |
| থ→ত (n=62) | `th` in all Latin arms (English /θ/) | 1.6 | 2.7 | 0.0 | 0.0 | 0.0 | 1.1 | 0.0 | 1.6 |
| খ→ক (n=68) | control: generic loss of aspiration; `kh` has no English clash | 2.5 | 0.0 | 0.5 | 1.5 | 5.4 | 0.5 | 0.0 | 0.0 |
| ছ→চ (n=102) | ITRANS `Ch` vs `ch` (case); LAT-P / LAT-G-asp `ch` (English /tʃ/ = চ) | 0.0 | 0.0 | 1.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| ট→ত (n=175) | LAT-P / ITRANS `T` vs `t` (case); LAT-G-asp `ṭ` | 8.0 | 1.5 | 4.0 | 0.2 | 5.0 | 0.6 | 0.0 | 0.0 |
| ড→দ (n=70) | LAT-P / ITRANS `D` vs `d` (case); LAT-G-asp `ḍ` | 4.3 | 0.5 | 2.9 | 0.0 | 1.9 | 1.0 | 0.0 | 0.0 |
| ত→ট (n=339) | reverse of `T`/`t` | 0.2 | 0.0 | 0.6 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| দ→ড (n=228) | reverse of `D`/`d` | 0.0 | 0.0 | 0.6 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| ব→ভ (n=329) | ITRANS `v` (English /v/) | 0.0 | 0.0 | 0.0 | 0.2 | 0.0 | 0.1 | 0.0 | 0.0 |
| ং→ন (n=48) | LAT-P `N` vs `n` (case) | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |

### Exact recovery *ok* % of words containing the source letter

| letter | LAT-P | LAT-P-reinit | LAT-G-det | LAT-G-det-reinit | LAT-G-asp | BN-G-iv-vm-asp | BN-G-matched | floor |
|---|---|---|---|---|---|---|---|---|
| চ | 60.1 | 9.6 | 61.1 | 9.9 | 45.5 | 22.8 | 0.7 | 86.1 |
| থ | 89.2 | 45.2 | 75.8 | 32.8 | 73.7 | 44.6 | 0.0 | 91.9 |
| খ | 79.4 | 26.0 | 63.2 | 39.2 | 58.3 | 55.4 | 5.9 | 89.7 |
| ছ | 85.9 | 26.8 | 82.4 | 60.8 | 78.8 | 57.2 | 3.6 | 97.1 |
| ট | 65.9 | 13.0 | 50.9 | 11.0 | 40.4 | 37.5 | 0.2 | 86.3 |
| ড | 59.0 | 6.2 | 23.3 | 6.2 | 30.0 | 9.0 | 0.0 | 72.9 |
| ত | 82.9 | 30.0 | 61.1 | 28.3 | 59.4 | 42.4 | 1.9 | 87.3 |
| দ | 77.0 | 6.9 | 59.6 | 25.9 | 57.0 | 35.4 | 1.5 | 84.2 |
| ব | 80.5 | 26.6 | 61.9 | 21.0 | 54.4 | 45.2 | 6.1 | 88.1 |
| ং | 79.2 | 36.8 | 71.5 | 38.9 | 70.1 | 55.6 | 36.8 | 85.4 |

### Pretrained minus fresh rows on identical text: *sub* difference, pp [95 % CI]

| pair | LAT-P − LAT-P-reinit | LAT-G-det − LAT-G-det-reinit |
|---|---|---|
| চ→ক | +5.6 [+1.7, +10.7] | +1.0 [-0.3, +2.3] |
| থ→ত | -1.1 [-4.5, +3.0] | +0.0 [+0.0, +0.0] |
| খ→ক | +2.5 [+0.0, +6.2] | -1.0 [-3.2, +0.0] |
| ছ→চ | +0.0 [+0.0, +0.0] | +1.0 [+0.0, +3.0] |
| ট→ত | +6.5 [+2.7, +10.5] | +3.8 [+1.5, +6.3] |
| ড→দ | +3.8 [+0.9, +7.7] | +2.9 [+0.0, +6.8] |
| ত→ট | +0.2 [+0.0, +0.6] | +0.6 [+0.0, +1.5] |
| দ→ড | +0.0 [+0.0, +0.0] | +0.6 [+0.0, +1.5] |
| ব→ভ | +0.0 [+0.0, +0.0] | -0.2 [-0.7, +0.0] |
| ং→ন | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] |

