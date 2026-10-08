# Encoding-path report (pilot_v4)

Status: **observations only**. Step contrasts and G6 were fixed before results (`tools/analyze_controls_v4.py`, commit `ea6e730`, D-034).

- **Arms:** cumulative and lossless, in Bengali codepoints, all with fresh matched-init content rows.
- **Settings:** training, eval and seeds identical to pilot_v1_1 through v3.
- **Runs:** 6 of 6, no machine resets.
  - Mid-queue, RAM fell to 0.5 GB free because WSL held about 10 GB. WSL was shut down (10.7 GB free afterwards).
  - No run failed or was re-run.
- **Tables:** `controls_v4_analysis_tugstugi_bengaliai-asr_whisper-medium.md` (primary), `controls_v4_analysis_wav2vec2-xls-r-300m-bengali.md` (secondary).

## Path (test_seen CER % at u3000, mean of 2 seeds)

| arm | step added | symbols | chars/utt | Whisper | wav2vec2 |
|---|---|---|---|---|---|
| BN-G-matched | — | 63 | 52.1 | 66.16 | 63.29 |
| BN-G-iv | explicit inherent vowel, no hasanta | 62 | 58.6 | 63.98 | 62.60 |
| BN-G-iv-vm | + vowel signs → independent vowels | 52 | 58.6 | 50.23 | 50.97 |
| BN-G-iv-vm-asp | + aspirates → unaspirated + হ | 42 | 60.5 | **19.36** | **27.42** |
| LAT-G-det-reinit | (ITRANS, fresh rows) | 38 | 61.6 | 30.60 | 36.26 |

Reference: LAT-G-det, ITRANS with pretrained rows = 11.10 (Whisper).

## Step contrasts (ΔCER A − B, G6)

| step | Whisper seen | Whisper unseen | wav2vec2 seen | wav2vec2 unseen |
|---|---|---|---|---|
| inherent vowel (BN-G-matched − BN-G-iv) | +2.18 (no) | +6.65 (no) | +0.69 (no) | +4.14 (no) |
| vowel merge (BN-G-iv − BN-G-iv-vm) | +13.75 (YES) | +14.15 (YES) | +11.63 (YES) | +10.68 (YES) |
| aspirate split (BN-G-iv-vm − BN-G-iv-vm-asp) | +30.87 (YES) | +33.89 (YES) | +23.54 (YES) | +23.69 (YES) |
| residual (BN-G-iv-vm-asp − LAT-G-det-reinit) | −11.24 (YES) | −15.12 (YES) | −8.83 (YES) | −10.04 (YES) |

## Symbol frequency in train_1h (content symbols, excluding space and `.`)

| rep | types | median count | types < 100 | types < 20 |
|---|---|---|---|---|
| BN-G | 59 | 383 | 18 | 6 |
| BN-G-iv | 58 | 388 | 18 | 6 |
| BN-G-iv-vm | 50 | 433 | 14 | 3 |
| BN-G-iv-vm-asp | 40 | 897 | 10 | 2 |
| LAT-G-det | 36 | 858 | 5 | 2 |
| LAT-P | 28 | 1,304 | 2 | 2 |

## Observations

1. **Most of the 35.6-point Bengali Unicode vs ITRANS gap is recovered without leaving Bengali codepoints.** The full path covers 46.8 points (66.2 → 19.4), so it overshoots ITRANS by 11.2.
2. **Making the inherent vowel explicit (abugida → alphabet) has no gated effect** in any ASR × test-set cell. The point estimates are positive (+0.7 to +6.7).
3. **Merging vowel signs with independent vowels gains 11–14 points; splitting aspirates gains 24–34 points**, the largest single step. Both steps are conditional on the cumulative order, with the inherent vowel already explicit. Neither was tested alone, because each would be lossy alone.
4. **The steps that help are the ones that make symbols shared.** The vowel merge has one row serve both forms of a vowel; the aspirate split has aspirates reuse the rows of the unaspirated consonant and হ. Both cut inventory and raise per-symbol frequency.

   Frequency alone does not explain the ordering, though: LAT-G-det has a similar frequency profile to BN-G-iv-vm-asp but is 11 points worse with fresh rows.

   Remaining ITRANS conventions are candidate causes, none isolated:
   - digraphs for non-aspirate single sounds (`sh`, `Sh`, `ch`, `.N`, `RRi`, `kSh`);
   - upper/lower case pairs for vowel length and retroflexion (`A`/`a`, `T`/`t`);
   - longer sequences.
5. **Learning curves** (fixed set): BN-G-iv-vm-asp drops earliest and furthest (u1000 67.8, u2000 25.3, u3000 21.2). All arms are still falling at u3000, so everything is conditional on 1 h of data, 3,000 updates and LR 1e-5.
6. **Cross-reference:** BN-G-iv-vm-asp with fresh rows (19.4) sits between ITRANS with pretrained rows (11.1) and ITRANS with fresh rows (30.6). Pretrained reuse remains the other large factor (D-031, D-033).

## Limitations

- Same as before: 2 seeds, one data size and budget, untuned LR, ASR CER only.
- Step effects depend on the cumulative order.
- "Shared symbols" is a post-hoc description, not a tested mechanism.
