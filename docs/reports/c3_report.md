# C3 report: third seed + embedding-LR sweep (pilot_v8a / pilot_v8b)

Status: **observations on SLR37 only** (same corpus and test sets as the exploration): robustness, not replication.

- **Plan:** `docs/C3_analysis_plan.md`, frozen before the runs (D-046). Analysis ran unchanged (`tools/analyze_c3.py`).
- **Full table:** `docs/reports/c3_hypothesis_tests.md`.
- **Runs:** 22 of 22 complete. One run (`BN-G-matched-elr30__s666`) segfaulted mid-training and was repeated from scratch with the same seed (D-054). The machine reset several times between runs; no other run was affected (resumable queue, D-049–D-053).
- **Hardware:** 250 W cap; clock lock 2,100 MHz (re-applied manually after each reboot).

## Arms: Whisper test_seen CER % at u3000

| arm | seeds | mean (per seed) | SD |
|---|---|---|---|
| LAT-P | 3 | 7.79 (7.83, 7.25, 8.29) | 0.52 |
| LAT-G-asp | 3 | 10.57 (10.22, 10.35, 11.15) | 0.51 |
| LAT-G-det | 3 | 12.39 (11.01, 11.18, 14.99) | 2.25 |
| BN-G-iv-vm-asp | 3 | 19.20 (17.77, 20.95, 18.89) | 1.62 |
| LAT-P-reinit | 3 | 29.83 (30.31, 30.01, 29.18) | 0.59 |
| LAT-G-det-reinit | 3 | 30.51 (28.28, 32.91, 30.34) | 2.32 |
| BN-G-iv-vm | 3 | 49.93 (52.11, 48.35, 49.33) | 1.95 |
| BN-G-iv | 3 | 62.78 (65.08, 62.88, 60.39) | 2.35 |
| BN-G-matched | 3 | 66.76 (66.58, 65.75, 67.97) | 1.12 |
| LAT-P-rand | 3 | 81.37 (81.12, 81.48, 81.50) | 0.21 |

Embedding-LR sweep (fresh-row arms, 2 seeds each):

| arm | ×1 (3 seeds) | ×3 | ×10 | ×30 |
|---|---|---|---|---|
| BN-G-matched | 66.76 | 66.54 | 59.92 | 44.40 |
| BN-G-iv-vm-asp | 19.20 | 18.28 | 15.66 | 12.92 |
| LAT-P-reinit | 29.83 | 28.20 | 22.98 | 14.36 |
| LAT-P (pretrained rows, ×1, reference) | 7.79 | — | — | — |

## Pre-registered tests (13)

| id | contrast | Δ primary [95 % CI] | wav2vec2 seen Δ | verdict |
|---|---|---|---|---|
| H1a | LAT-P − LAT-P-reinit | −22.04 [−23.74, −20.32] | −18.46 | supported |
| H1b | LAT-G-det − LAT-G-det-reinit | −18.12 [−19.78, −16.65] | −13.77 | supported |
| H1c-x3 | LAT-P − LAT-P-reinit-elr3 | −20.41 [−22.32, −18.62] | −17.45 | supported |
| H1c-x10 | LAT-P − LAT-P-reinit-elr10 | −15.20 [−16.92, −13.54] | −13.81 | supported |
| H1c-x30 | LAT-P − LAT-P-reinit-elr30 | −6.57 [−7.94, −5.28] | −7.35 | supported |
| H2 | LAT-P-rand − LAT-P-reinit | +51.53 [+49.45, +53.52] | +40.84 | supported |
| H3a | BN-G-matched − BN-G-iv (equivalence ±5) | +3.98 [+2.87, +5.13] | +2.13 | **inconclusive** |
| H3b | BN-G-iv − BN-G-iv-vm | +12.85 [+11.61, +14.10] | +10.95 | supported |
| H3c | BN-G-iv-vm − BN-G-iv-vm-asp | +30.73 [+29.10, +32.33] | +23.47 | supported |
| H4 | (BN-G-iv-vm-asp − LAT-G-asp) − (LAT-G-det-reinit − LAT-G-det) | −9.49 [−11.23, −7.86] | −7.26 | supported |
| H5-x3 | BN-G-matched-elr3 − BN-G-iv-vm-asp-elr3 | +48.25 [+46.46, +49.98] | +37.43 | supported |
| H5-x10 | BN-G-matched-elr10 − BN-G-iv-vm-asp-elr10 | +44.26 [+42.46, +46.03] | +33.30 | supported |
| H5-x30 | BN-G-matched-elr30 − BN-G-iv-vm-asp-elr30 | +31.48 [+29.73, +33.14] | +23.38 | supported |

All gated tests also have the same sign on test_unseen with both ASRs (see the full table).

**Hypothesis level (plan rules):**

| hypothesis | verdict on SLR37 |
|---|---|
| H1 prior transfer | supported (all 5 tests) |
| H2 prior interference | supported |
| H3 encoding steps | **not supported as a whole**: H3b and H3c supported; H3a inconclusive (CI upper bound 5.13 > 5; test_unseen Δ +7.90) |
| H4 sub-additivity | supported |
| H5 LR stability (sign) | supported (all 6 tests, same sign) |

## Observations (not pre-registered; exploratory, no tests)

1. **The reuse gap falls steadily with embedding LR:** 22.0 → 20.4 → 15.2 → 6.6 CER (×1 → ×30). Its sign is stable (H1 holds), but its size is strongly LR-dependent. A large part of the base-LR "prior transfer" effect is slow learning of fresh rows within the 3,000-update budget. Whether the gap closes completely at a higher LR or a longer budget is untested.
2. **The encoding gap also shrinks with embedding LR** (48.3 → 44.3 → 31.5) but stays far larger than the reuse gap. At ×30, BN-G-matched improves by 22 points, while BN-G-iv-vm-asp improves by 6.
3. **At ×30, fresh rows for the restructured Bengali encoding (12.9) and for Google phonemes (14.4) are close.** Both remain above LAT-P with pretrained rows at ×1 (7.8). This was not a planned contrast.
4. **H3a:** the inherent-vowel step is small but likely not zero (about +4 seen, +8 unseen). The plan's equivalence claim is not supported; the paper should state "small" rather than "no effect".
5. **Seed variance** is ≤ 2.4 CER for all arms; the third seed did not change the ordering of any arm.

## Implications for wording (to carry into the paper draft)

- H1 should be stated as "pretrained rows give a faster/better start within a fixed budget", with the LR dependence shown. It should not say "only pretraining can supply this".
- The base-LR magnitudes of H4 (sub-additivity) are specific to the base LR (as noted in controls_v7).
- The H3 claim is restricted to the vowel-merge and aspirate-split steps.

## Limitations

- Same corpus, same test sets, and two of the three seeds were seen during exploration.
- LR arms: 2 seeds; only fresh-row arms were swept.
- Single 3,000-update budget; ASR CER only (no listening test; C4 optional).
