# C3 analysis plan (frozen before runs, 2026-10-10, D-046)

**Purpose:** robustness of the exploratory findings behind hypotheses H1–H5 (`docs/D5_rq_hypotheses.md`, Option B) on the **same corpus** (SLR37 bn-BD, train_1h).

- More seeds and an embedding-LR sweep tighten the estimates, and can **falsify** a hypothesis.
- They **cannot** establish generality. That is C1's job (second corpus).
- Results are reported as "supported / not supported on SLR37", never as "confirmed".

## Runs (unchanged training and eval: 3,000 updates, LR 1e-5, NFE 32, CFG 2, fixed eval sets)

| part | config | arms | seeds | runs |
|---|---|---|---|---|
| a | `configs/pilot_v8a.json` | LAT-P, LAT-G-det, LAT-G-asp, LAT-P-rand, LAT-P-reinit, LAT-G-det-reinit, BN-G-matched, BN-G-iv, BN-G-iv-vm, BN-G-iv-vm-asp (specs identical to their original versions) | 4242 | 10 |
| b | `configs/pilot_v8b.json` | BN-G-matched, BN-G-iv-vm-asp, LAT-P-reinit at embedding LR ×3 and ×30 (×10 already in pilot_v7) | 666, 1234 | 12 |

- **Order:** part a first (all hypothesis tests except the LR sweep become computable), then ×30, then ×3.
- **Queue:** `tools/run_pilot_v8.sh`, resumable, snapshots pruned after eval.
- **Hardware:** 250 W cap + clock lock 2,400 MHz (D-041).

## Metrics and decision rules

- **Primary:** Whisper-BengaliAI CER on **test_seen** at u3000, corpus-level, mean over seeds per utterance.
- **Secondary (agreement only):** wav2vec2 CER on test_seen.
- **Reported, not used for decisions:** test_unseen with both ASRs.

**Gate G6 (directional):** a difference passes when, in the predicted direction:
- |Δ| > 95 % paired-bootstrap CI half-width (2,000 resamples over utterances), **and**
- |Δ| > 2 × the maximum seed SD of the arms involved.

**Verdicts:**

| verdict | condition |
|---|---|
| supported | primary gated in the predicted direction, and wav2vec2 test_seen has the same sign |
| supported (primary only) | primary gated in the predicted direction, but wav2vec2 disagrees in sign |
| not supported | not gated |
| falsified | gated in the opposite direction |

**Equivalence (H3a only):** "supported" if the 95 % CI of Δ lies within ±5 CER.
- "Falsified" if the CI excludes 0 and |Δ| > 5; otherwise "inconclusive".
- Margin rationale: ≈ 2× the largest seed SD among the BN-G-path arms (2.25), and below half the smallest gated encoding step (≈ 10.7).

## Tests (the complete list; implemented in `tools/analyze_c3.py`)

| id | contrast (A − B) | prediction | hypothesis |
|---|---|---|---|
| H1a | LAT-P − LAT-P-reinit | < 0 | H1 prior transfer (phonemic) |
| H1b | LAT-G-det − LAT-G-det-reinit | < 0 | H1 prior transfer (ITRANS) |
| H1c-x3 / x10 / x30 | LAT-P − LAT-P-reinit-elr{3,10,30} | < 0 | H1 at higher embedding LR |
| H2 | LAT-P-rand − LAT-P-reinit | > 0 | H2 prior interference |
| H3a | BN-G-matched − BN-G-iv | \|Δ\| ≤ 5 (equivalence) | H3 inherent vowel: no meaningful effect |
| H3b | BN-G-iv − BN-G-iv-vm | > 0 | H3 vowel-form merge helps |
| H3c | BN-G-iv-vm − BN-G-iv-vm-asp | > 0 | H3 aspirate split helps |
| H4 | (BN-G-iv-vm-asp − LAT-G-asp) − (LAT-G-det-reinit − LAT-G-det) | < 0 | H4 sub-additivity |
| H5-x3 / x10 / x30 | BN-G-matched-elr{m} − BN-G-iv-vm-asp-elr{m} | > 0 | H5 encoding gap stable across embedding LR |

**Hypothesis-level verdicts:**
- **H1:** all of H1a, H1b, H1c-x3/x10/x30 supported.
- **H2:** H2 supported.
- **H3:** all of H3a, H3b, H3c supported.
- **H4:** H4 supported.
- **H5 (LR part):** H5-x3/x10/x30 and H1c-x3/x10/x30 all supported. The data-size part of H5 is already observed in D-042 (fixed budget).

**Multiplicity:** 13 tests, all listed here in advance. No correction beyond G6's seed-SD criterion, which is stricter than the CI alone. The test count is reported with the results.

**Not decided by this plan:** any new contrast suggested by the results. If one is examined, it is labelled exploratory.

## Known limitations stated in advance

- Same corpus and test sets as the exploration, so this is not a replication.
- 3 seeds for base arms (seeds 666/1234 were seen during exploration); 2 seeds for LR arms.
- The LR-swept arms are compared against LAT-P at base LR (pretrained rows are already trained).
- The encoding steps are cumulative and order-dependent (D-034).
