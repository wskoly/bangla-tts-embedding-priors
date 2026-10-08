# LAT-G-asp report (pilot_v5)

Status: **observations only**. Contrasts and G6 were fixed before results (`tools/analyze_controls_v5.py`, commit `0ace661`, D-036).

- **Arm:** LAT-G-asp, a one-to-one relabeling of BN-G-iv-vm-asp onto single lowercase characters that already have pretrained rows. Base vocabulary, official init, 0 new rows.
- **Settings:** training, eval and seeds identical to all earlier pilots.
- **Runs:** 2 of 2 complete, no machine resets.
  - The first attempt failed on a full disk, before any evaluation (D-037).
  - The runs were repeated from scratch with an unchanged config.
- **Tables:** `controls_v5_analysis_tugstugi_bengaliai-asr_whisper-medium.md` (primary), `controls_v5_analysis_wav2vec2-xls-r-300m-bengali.md` (secondary).

## test_seen CER % at u3000 (mean of 2 seeds)

| arm | rows | Whisper | wav2vec2 |
|---|---|---|---|
| LAT-P | pretrained | 7.54 | 18.36 |
| **LAT-G-asp** | pretrained | **10.28** (10.22, 10.35) | **20.27** |
| LAT-G-det (ITRANS) | pretrained | 11.10 | 21.28 |
| BN-G-iv-vm-asp (same encoding as LAT-G-asp) | fresh | 19.36 | 27.42 |
| LAT-G-det-reinit | fresh | 30.60 | 36.26 |
| BN-G | fresh (N(0,1)) | 67.97 | — |

## Pre-specified contrasts (ΔCER, G6)

| contrast | Whisper seen | Whisper unseen | wav2vec2 seen | wav2vec2 unseen |
|---|---|---|---|---|
| BN-G-iv-vm-asp − LAT-G-asp (reuse, same encoding) | +9.08 (YES) | +6.11 (YES) | +7.15 (YES) | +6.45 (YES) |
| LAT-G-det − LAT-G-asp (ITRANS vs new, both pretrained) | +0.81 (no) | −0.23 (no) | +1.01 (no) | +0.64 (no) |
| LAT-P − LAT-G-asp | −2.74 (YES) | −4.72 (YES) | −1.91 (YES) | −2.87 (YES) |
| interaction (BN-G-iv-vm-asp − LAT-G-asp) − (LAT-G-det-reinit − LAT-G-det) | −10.42 (YES) | −15.35 (YES) | −7.82 (YES) | −9.40 (YES) |

## Observations

1. **Encoding and pretrained reuse do not add up.** With fresh rows, the new encoding beats ITRANS by 11.2 points (D-035). With pretrained rows, LAT-G-asp and ITRANS do not differ in any ASR × set cell (|Δ| ≤ 1.0).
2. **The reuse benefit is smaller for the better encoding:** 9.1 points vs 19.5 for ITRANS. The interaction passes G6 in all four cells, so this is sub-additive.

   Description, not a tested mechanism: pretrained rows appear to compensate for ITRANS's conventions, and once rows are pretrained, the grapheme arms converge near 10–11 CER at this budget.
3. **The phonemic arm stays best.** LAT-P is still 1.9–4.7 points better than LAT-G-asp (YES in all cells), consistent with the D-033 observation that the phonemic advantage appears only with pretrained rows.
4. **Zero-shot (u0, fixed set, Whisper):** LAT-G-asp 61.3 vs LAT-G-det 64.5 vs LAT-P 38.2. The new letter choices give no zero-shot advantage over ITRANS.
5. **Seed spread:** LAT-G-asp has the smallest of any arm (test_seen SD 0.09).

## Caveats (fixed in advance, D-036)

- Letter choices differ from ITRANS (অ/আ = o/a vs a/A, শ = x, ব = b), so LAT-G-asp − LAT-G-det mixes structure with letter priors.
- The diacritic rows (9.4 % of tokens) have unknown training status.
- Same as before: 2 seeds, one data size and budget, untuned LR, ASR CER only.
