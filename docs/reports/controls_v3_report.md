# LAT-G-det-reinit report (pilot_v3)

Status: **observations only**. Contrasts and G6 were fixed before results (`tools/analyze_controls_v3.py`, commit `4ead9ce`, D-032).

- **Arm:** ITRANS text (LAT-G-det) with its 36 content-symbol embedding rows re-initialized. It uses matched init and the same rule as LAT-P-reinit (re-initialize every used symbol except space and `.`).
- **Settings:** training, eval and seeds identical to pilot_v1_1 and pilot_v2.
- **Runs:** 2 of 2, no machine resets (250 W cap).
- **Tables:** `controls_v3_analysis_tugstugi_bengaliai-asr_whisper-medium.md` (primary), `controls_v3_analysis_wav2vec2-xls-r-300m-bengali.md` (secondary).

## The four Latin cells (test_seen CER % at u3000, Whisper, mean of 2 seeds)

|  | pretrained rows reused | fresh rows (matched init) |
|---|---|---|
| grapheme (ITRANS) | LAT-G-det 11.10 | LAT-G-det-reinit **30.60** (28.28, 32.91) |
| phonemic | LAT-P 7.54 | LAT-P-reinit 30.16 |

Reference: BN-G-matched (Bengali Unicode, fresh rows) **66.16**.

## Pre-specified contrasts (ΔCER, G6)

| contrast | Whisper seen | Whisper unseen | wav2vec2 seen | wav2vec2 unseen |
|---|---|---|---|---|
| LAT-G-det − LAT-G-det-reinit (reuse benefit, grapheme) | −19.50 (YES) | −21.46 (YES) | −14.97 (YES) | −15.86 (YES) |
| LAT-G-det-reinit − LAT-P-reinit (content, both fresh) | +0.44 (no) | +2.92 (YES) | −0.78 (no) | +0.37 (no) |
| BN-G-matched − LAT-G-det-reinit (encoding of grapheme content, both fresh) | +35.57 (YES) | +39.57 (YES) | +27.03 (YES) | +28.47 (YES) |
| interaction: (G-reinit − G) − (P-reinit − P) | −3.12 (no) | −1.57 (no) | −3.70 (YES) | −3.13 (YES) |

- The LAT-G-det-reinit seeds differ by 4.6 points on test_seen with Whisper (SD 3.27). That makes the Whisper G6 threshold strict, at 6.55.
- The wav2vec2 seed SD is 1.73.

## Observations

1. **With fresh rows, grapheme and phonemic Latin text perform the same** at this budget: 30.6 vs 30.2.
   - Three of four ASR × test-set cells show no difference by G6. Whisper test_unseen shows +2.9 for graphemes.
   - Observation 4 of the pilot_v2 report attributed part of the BN-G-matched vs LAT-P-reinit gap to "explicit pronunciation". On this evidence, that part is about zero.
2. **The 36-point gap reappears between two encodings of the same grapheme content.** BN-G-matched (Bengali Unicode) vs LAT-G-det-reinit (ITRANS) is +35.6, with fresh rows on both sides. Candidate differences between the encodings, none isolated yet:
   - Inventory: 63 vs 38 symbols.
   - Sequence length: 52.1 vs 61.6 characters per training utterance.
   - The inherent vowel: written as an explicit `a` in ITRANS, implicit (no symbol) in Bengali script.
   - Vowel forms: the independent vowel and its vowel-sign form share one symbol in ITRANS but are separate codepoints in Bengali.
   - Aspirates: decomposed in ITRANS (`kh` = `k` + `h`, shared rows), single codepoints in Bengali.
3. **Pretrained reuse helps both representations by a similar amount:**
   - 19.5 points for graphemes, 22.6 for phonemes;
   - the interaction (−3.1) passes G6 on wav2vec2 only.

   The phonemic advantage over ITRANS seen in pilot_v1_1 (LAT-G-det − LAT-P = +3.56) appears only when pretrained rows are reused.
4. **Learning curves** (fixed set):
   - LAT-G-det-reinit falls earlier than LAT-P-reinit (u1000: 75.4 vs 86.8) and ends at about the same point (u3000: 32.6 vs 32.0).
   - Both are still falling at u3000. As before, all results are conditional on 1 h of data and 3,000 updates at LR 1e-5.
5. **Updated descriptive path from BN-G to LAT-P** (test_seen, Whisper). These are telescoping sums, not a causal decomposition:

| step | ΔCER |
|---|---|
| BN-G → BN-G-matched (init scale) | 1.8 |
| → LAT-G-det-reinit (Bengali Unicode → ITRANS encoding) | 35.6 |
| → LAT-P-reinit (grapheme → phonemic content) | 0.4 |
| → LAT-P (pretrained reuse) | 22.6 |
| **total** | **60.4** |

## Limitations

- Same as the pilot_v2 report: 2 seeds, one data size and budget, untuned LR, ASR CER only.
- LAT-G-det-reinit has the largest seed spread of any arm so far.
