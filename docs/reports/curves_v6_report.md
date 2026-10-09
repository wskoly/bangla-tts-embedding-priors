# Data-size curves report (pilot_v6)

Status: **observations only**. Contrasts and G6 were fixed before results (`tools/analyze_curves_v6.py`, commit `210e1d7`, D-039).

- **Runs:** 24 of 24 complete, plus the train_1h runs reused from pilot_v1_1 and v4.
- **Machine resets:** two, both in the same run (D-040, D-041). That run restarted from scratch; no reported result comes from an interrupted run.
- **GPU settings:**
  - The last 6 runs used a 250 W cap plus a clock lock at 2,400 MHz (`nvidia-smi -lgc 210,2400`, set manually). This affects speed only.
  - Earlier runs used the 250 W cap without the lock.
- **Design:** a fixed budget of 3,000 updates at every size.
  - Equal compute: 0.25 h ≈ 116 epochs, 1.58 h ≈ 19 epochs.
- **Tables:** `curves_v6_analysis_tugstugi_bengaliai-asr_whisper-medium.md` (primary), `curves_v6_analysis_wav2vec2-xls-r-300m-bengali.md` (secondary).

## test_seen CER % at u3000, Whisper (mean ± SD of 2 seeds)

| arm | 0.25 h | 0.5 h | 1 h | 1.58 h |
|---|---|---|---|---|
| BN-G | 70.73 ± 3.22 | 68.61 ± 1.66 | 67.97 ± 1.64 | 71.28 ± 2.76 |
| LAT-G-det | 11.27 ± 0.49 | 11.45 ± 0.42 | 11.10 ± 0.12 | 10.82 ± 0.38 |
| LAT-P | 8.65 ± 0.21 | 7.75 ± 0.90 | 7.54 ± 0.41 | 7.51 ± 0.40 |
| BN-G-iv-vm-asp | 20.38 ± 2.16 | 18.43 ± 0.49 | 19.36 ± 2.25 | 19.67 ± 0.27 |

test_unseen shows the same pattern, with LAT-P at 5.6–6.2 and LAT-G-det at 10.5–12.0 across sizes.

## Pre-specified contrasts

- **Ordering:** at every size, all four contrasts pass G6 for both ASRs and both test sets. The ordering LAT-P < LAT-G-det < BN-G-iv-vm-asp < BN-G holds at every size.
- **Trend contrasts** (gap at 1.58 h minus gap at 0.25 h) do not pass G6 anywhere:

| trend | Whisper seen | Whisper unseen | wav2vec2 seen | wav2vec2 unseen |
|---|---|---|---|---|
| LAT-G-det − LAT-P | +0.70 | −0.54 | +1.05 | −0.09 |
| BN-G-iv-vm-asp − LAT-G-det | −0.26 | −1.31 | −0.40 | −0.07 |

## Observations

1. **The curves are flat.** Between 0.25 h and 1.58 h, no arm moves by more than about 1–3 CER points, which is within about 1.5 seed SD for most arms. LAT-P improves slightly (8.65 → 7.51 seen).
2. **The representation gaps do not depend on data size** in this range. The trend contrasts show no change.
3. **At a fixed 3,000-update budget, the binding constraint appears to be the update budget, not the data.** Fifteen minutes of audio already gives about as much as 3,000 updates can exploit.
   - BN-G is slightly worse at 1.58 h than at 1 h (71.3 vs 68.0), consistent with fewer passes over each symbol for slowly learned fresh rows.
   - This is post-hoc, within about 1.5 seed SD, and not tested.
4. **Consequence for the claims:** this design cannot support a data-efficiency claim, i.e. that one representation needs less data. What it does show is that the representation ordering and gap sizes are stable from 15 min to 1.6 h at this budget.

   A data-efficiency test needs either:
   - a budget scaled to the data (fixed epochs), or
   - training to convergence at each size, e.g. early stopping on val CER.

## Limitations

- Same as before: 2 seeds, untuned LR, ASR CER only, SLR37 only.
- The update budget is the main confound for any "data" interpretation.
