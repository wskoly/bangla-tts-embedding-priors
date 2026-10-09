# Embedding-LR check report (pilot_v7)

Status: **observations only**. Contrasts and G6 were fixed before results (`tools/analyze_controls_v7.py`, commit `5ab1317`, D-043).

- **Change:** the text-embedding table trains at 10× the base LR (1e-4). The rest of the model stays at 1e-5; everything else is identical to the base-LR arms.
- **Runs:** 6 of 6 complete, no resets (250 W cap + clock lock 2,400 MHz).
- **Tables:** `controls_v7_analysis_tugstugi_bengaliai-asr_whisper-medium.md` (primary), `controls_v7_analysis_wav2vec2-xls-r-300m-bengali.md` (secondary).

## test_seen CER % at u3000 (Whisper, mean of 2 seeds)

| arm | base LR | embedding LR ×10 | Δ (G6) |
|---|---|---|---|
| BN-G-matched | 66.16 | 59.92 | −6.24 (YES) |
| BN-G-iv-vm-asp | 19.36 | 15.66 | −3.70 (no; YES on unseen) |
| LAT-P-reinit | 30.16 | 22.98 | −7.18 (YES) |
| LAT-P (pretrained rows, base LR, reference) | 7.54 | — | — |

## Key gaps at the higher embedding LR

| gap | base LR (earlier) | embedding LR ×10 | G6 at ×10 | change in gap |
|---|---|---|---|---|
| encoding: BN-G-matched − BN-G-iv-vm-asp | +46.80 | **+44.26** | YES (all 4 ASR × set cells) | −2.55 (no, all cells) |
| reuse: LAT-P-reinit − LAT-P | +22.62 | **+15.44** | YES (all 4 cells) | not pre-specified as an interaction (LAT-P not rerun) |

## Observations

1. **Fresh-row arms were partly undertrained at the base LR.** ×10 on the embedding table helps all three by 3–8 CER points; all fixed-set curves are still falling at u3000.
2. **The encoding gap is robust to the embedding LR:** 44 vs 47 points. The interaction is about −3 and does not pass G6 in any cell. Candidate contribution 2 (D-035) is not an undertraining artifact at this LR.
3. **The reuse gap shrinks by about a third (22.6 → 15.4) but remains large and gated.** Part of the "pretrained reuse" benefit at base LR is optimization speed, not only prior knowledge.
   - The shuffled-letter result (D-031: wrong priors are worse than fresh rows) is unaffected by this check; LAT-P-rand was not rerun.
   - The sub-additivity analysis (D-038) used base-LR fresh arms. At ×10 the fresh-row reference points move, so its magnitudes should be read as base-LR-specific.
4. **Order of arms unchanged:** LAT-P < BN-G-iv-vm-asp < LAT-P-reinit < BN-G-matched.

## Limitations

- One alternative LR (×10) only; no sweep, so larger multipliers might shrink the reuse gap further.
- LAT-P and the pretrained arms were not rerun at ×10, since their embedding rows are already trained.
- Same as before: 2 seeds, one budget, ASR CER only.
