# Controls report (pilot_v2)

Status: **observations only**: no claims, RQ framing or hypotheses. Contrasts and gate G6 were fixed before any control result existed: `tools/analyze_controls_v2.py` was committed in `8244d1d`, the arms in D-028. Its docstring cites "D-029" for G6; that ID was later reused for the crash log, and the gate definition itself is unchanged (D-024/D-027).

## Setup

- Training, eval set, decoding, budget and seeds are identical to pilot_v1_1. The config is `configs/pilot_v2.json`.
  - Data: `train_1h`.
  - Training: 3,000 updates at LR 1e-5; seeds 666 and 1234; online weights evaluated.
  - Decoding: NFE 32, CFG 2.
- **Arms:**

| arm | text | content-symbol embeddings |
|---|---|---|
| BN-G (v1_1) | Bengali graphemes | 59 new rows, N(0,1) init (official expansion) |
| BN-G-matched | Bengali graphemes | 59 new rows, matched init (per-dim mean/std of trained rows, std ≈ 0.62) |
| LAT-P (v1_1) | Latin phonemic | pretrained rows reused |
| LAT-P-reinit | Latin phonemic | 28 used rows (excluding space/punct) re-initialized, matched init |
| LAT-P-rand | LAT-P under a fixed symbol permutation | pretrained rows reused, but bound to the wrong sounds |
| LAT-G-det (v1_1) | ITRANS | pretrained rows reused |

- **Runs:** 6 of 6 complete. One run was interrupted by a machine reset (D-029) and resumed from its own checkpoint/eval outputs; nothing was re-run selectively.
- **Analysis tables:** `controls_v2_analysis_tugstugi_bengaliai-asr_whisper-medium.md` (primary ASR) and `controls_v2_analysis_wav2vec2-xls-r-300m-bengali.md` (secondary ASR).

## Primary metric: test_seen CER % at u3000 (Whisper), mean of 2 seeds

| arm | CER | seeds |
|---|---|---|
| LAT-P | 7.54 | 7.83, 7.25 |
| LAT-G-det | 11.10 | 11.01, 11.18 |
| LAT-P-reinit | 30.16 | 30.31, 30.01 |
| BN-G-matched | 66.16 | 66.58, 65.75 |
| BN-G | 67.97 | 66.81, 69.12 |
| LAT-P-rand | 81.30 | 81.12, 81.48 |

## Pre-specified contrasts (ΔCER, A − B; G6 = |Δ| > CI half-width and > 2 × max seed SD)

| contrast | isolates | Whisper seen | Whisper unseen | wav2vec2 seen | wav2vec2 unseen |
|---|---|---|---|---|---|
| BN-G-matched − BN-G | init scale of new rows | −1.80 (no) | −1.75 (no) | −2.17 (YES) | −1.08 (no) |
| LAT-P − LAT-P-reinit | reuse of pretrained rows | −22.62 (YES) | −23.03 (YES) | −18.67 (YES) | −18.99 (YES) |
| LAT-P − LAT-P-rand | correct vs scrambled prior | −73.76 (YES) | −85.32 (YES) | −59.51 (YES) | −64.90 (YES) |
| LAT-P-rand − LAT-P-reinit | scrambled reused vs fresh | +51.14 (YES) | +62.29 (YES) | +40.84 (YES) | +45.91 (YES) |
| BN-G-matched − LAT-P-reinit | text content, both fresh | +36.00 (YES) | +42.49 (YES) | +26.25 (YES) | +28.84 (YES) |
| BN-G-matched − LAT-G-det | fresh Bengali vs reused Latin graphemes | +55.07 (YES) | +61.03 (YES) | +42.01 (YES) | +44.32 (YES) |

- Both ASRs agree on the direction of every contrast.
- G6 disagrees only on the init-scale contrast: it passes on wav2vec2 test_seen only.

## Observations

1. **The init scale of the new embeddings explains almost none of the BN-G deficit.** Matched initialization moved test_seen CER by about 2 points; BN-G-matched stays at 66 CER, against 7.5 for LAT-P. The confound flagged in D-027 is therefore not the main driver at this budget.
2. **Reusing the pretrained embeddings matters a lot, even with identical text.** LAT-P-reinit is the same phonemic text with fresh rows for its 28 content symbols, and it loses about 23 CER points on both test sets (about 19 on wav2vec2).
3. **The pretrained rows carry sound-specific information, not just a good scale.** Binding them to the wrong sounds (LAT-P-rand) is worse than fresh rows by about 51 points, and worse than BN-G. LAT-P-rand's fixed-set curve barely moves after u500 (88 → 84). The mismatched prior is not unlearned at LR 1e-5 within 3,000 updates.
4. **With pretrained reuse removed from both arms, the phonemic text still beats Bengali graphemes** (BN-G-matched − LAT-P-reinit = +36). This contrast is confounded with:
   - inventory size (59 vs 28 symbols);
   - sequence length;
   - the explicit pronunciation in LAT-P: lexicon/G2P resolves the inherent vowel, schwa deletion and conjuncts, which a grapheme model must learn from 1 h of audio.
   It does not isolate script from linguistic representation. That needs BN-P, a phonemic representation in a non-Latin, fresh-embedding script.
5. **Descriptive path from BN-G to LAT-P** (test_seen, Whisper; telescoping sums, not a causal decomposition; interactions not estimated):

| step | ΔCER |
|---|---|
| BN-G → BN-G-matched | 1.8 |
| BN-G-matched → LAT-P-reinit | 36.0 |
| LAT-P-reinit → LAT-P | 22.6 |
| **total** | **60.4** |

6. **Curve shapes** (fixed set, u0 → u3000):

| arm | u0 | u1000 | u2000 | u3000 | pattern |
|---|---|---|---|---|---|
| LAT-P-reinit | 112 | 87 | 46 | 32 | sharp drop between u1000 and u2000 |
| BN-G-matched | 116 | 85 | 76 | 69 | steady decline |

   Both are still falling at u3000. Gaps measured at a larger budget or more data may differ, so every result here is conditional on 1 h of data and 3,000 updates.

## Limitations (unchanged from pilot v1_1 unless noted)

- **Statistics and design:**
  - Two seeds, so the seed SD in G6 is a crude estimate.
  - One data size and one training budget.
  - The LR was frozen and not tuned per arm. Fresh-embedding arms might prefer a higher embedding LR; that was not tested.
- **Metric:**
  - Intelligibility proxy only: ASR CER, no listening test.
  - CER above 100 at u0 reflects insertions.
- **Data:** SLR37 seen speakers only; test_unseen is a single held-out speaker.

## Open, not started

- Data-size curves (0.25 / 0.5 / 1 / 1.58 h) for the main arms.
- BN-P arm, to separate script from linguistic representation (observation 4).
- Optional: an embedding-LR sensitivity check for the fresh-row arms (observation 6).
