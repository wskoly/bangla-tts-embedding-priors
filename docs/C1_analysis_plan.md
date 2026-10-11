# C1 analysis plan (frozen before the full C1 runs, 2026-10-11, D-061)

**Purpose:** test whether the C3 findings behind H1–H4 (`docs/D5_rq_hypotheses.md`, Option B) **replicate on a second corpus**: Rasa Bengali (bn-IN, neutral styles), with the data rules in `docs/C1_data_rules.md`.

- Results are reported as "replicated / not replicated on Rasa".
- Same model, recipe and evaluation as C3: 3,000 updates, LR 1e-5, NFE 32, CFG 2, ground-truth durations, train_1h.
- H5 (embedding-LR sweep) is not part of C1.

## Runs

| part | config | arms | seeds | runs |
|---|---|---|---|---|
| pilot (done) | `configs/pilot_c1a.json` | LAT-P, LAT-P-reinit, LAT-P-rand, BN-G-matched, BN-G-iv-vm-asp | 666 | 5 |
| full | `configs/pilot_c1b.json` | the 5 pilot arms + LAT-G-det, LAT-G-det-reinit, LAT-G-asp | 666 (new arms only), 1234, 4242 | 19 |

- The pilot runs count as seed 666, because nothing changed after the pilot (D-060).
- Arm specs are identical to C3 (`configs/pilot_v8a.json`).
- **Order:**
  1. the new arms at seed 666, so all 8 arms have one seed;
  2. all 8 arms at seed 1234;
  3. all 8 arms at seed 4242.
- **Queue:** `tools/run_pilot_c1b.sh`, resumable, snapshots pruned after eval.

## Metrics and decision rules (identical to C3 except for the coverage rule)

- **Primary:** Whisper-BengaliAI CER on **test_seen** (rasaF) at u3000, corpus-level, mean over 3 seeds per utterance.
- **Coverage rule (pre-registered in `docs/C1_corpus_shortlist.md`, triggered in D-058):**
  - Tests that involve a LAT-P arm (H1a, H2) use the **coverage-restricted** test_seen subset as primary: every word in lexicon + supplement, n = 47.
  - All other tests use all of test_seen (n = 160).
  - The other subset is reported for every test, not used for decisions.
- **Secondary (agreement only):** wav2vec2 CER on the same subset.
- **Reported, not used for decisions:** test_unseen (rasaM, n = 109 all / 30 covered) with both ASRs.

**Gate G6 (directional),** in the predicted direction:
- |Δ| > 95 % paired-bootstrap CI half-width (2,000 resamples over utterances), **and**
- |Δ| > 2 × the maximum seed SD of the arms involved.
- The seed SD is computed on the same subset.

**Verdicts:**

| verdict | condition |
|---|---|
| replicated | primary gated in the predicted direction, and wav2vec2 has the same sign |
| replicated (primary only) | primary gated in the predicted direction, but wav2vec2 disagrees in sign |
| not replicated | not gated |
| reversed | gated in the opposite direction |

## Tests (the complete list; implemented in `tools/analyze_c1.py`)

| id | contrast (A − B) | prediction | primary subset | hypothesis |
|---|---|---|---|---|
| H1a | LAT-P − LAT-P-reinit | < 0 | covered | H1 prior transfer (phonemic) |
| H1b | LAT-G-det − LAT-G-det-reinit | < 0 | all | H1 prior transfer (ITRANS) |
| H2 | LAT-P-rand − LAT-P-reinit | > 0 | covered | H2 prior interference |
| H3-path | BN-G-matched − BN-G-iv-vm-asp | > 0 | all | H3 encoding path (H3b + H3c combined) |
| H4 | (BN-G-iv-vm-asp − LAT-G-asp) − (LAT-G-det-reinit − LAT-G-det) | < 0 | all | H4 sub-additivity |

- **H3-path** tests the whole BN-G → BN-G-iv-vm-asp path. C1 does not run BN-G-iv or BN-G-iv-vm, so H3a/H3b/H3c are not tested separately. In C3 the H3a step was inconclusive and the gain came from H3b and H3c.
- **Hypothesis-level:** H1 replicated = H1a ∧ H1b; H2, H3-path and H4 each stand alone.
- **Multiplicity:** 5 tests, all listed here in advance. No correction beyond G6.

**Not decided by this plan:** any other contrast (for example LAT-P vs LAT-G-det, or pilot-arm CER differences between corpora). If one is examined, it is labelled exploratory.

## Known limitations stated in advance

- One new corpus, one training speaker (rasaF) and one unseen speaker (rasaM).
- Rasa is bn-IN read speech, while the lexicon and G2P are bn-BD (Google). Lexicon coverage is ~84 %, so the LAT-P primary subset is small (47) and selects easier text: every arm has lower CER on it (D-060).
- Seed 666 was seen in the pilot. The pilot used no tuning, but its direction was known before this plan was written.
- The encoding path is cumulative and order-dependent (D-034).
