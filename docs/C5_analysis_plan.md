# C5 analysis plan: causal controls (frozen before the runs, 2026-10-12, D-067)

**Purpose:** test two design choices that the C3/C1 tests held fixed. C5 adds evidence; it does not replace any
frozen C3 or C1 verdict.

- **C5a: fresh-row initialization.** All earlier fresh rows were drawn with one generator seed (666), so seed
  variation covered data order and training noise but not the initial embeddings.
- **C5b: choice of scrambled alphabet.** H2 rests on one fixed derangement of the LAT-P alphabet.

## Runs (`configs/pilot_c5.json`, recipe identical to `pilot_v8a`; SLR37 train_1h)

| Part | Arms | Training seeds | Runs |
|---|---|---|---|
| C5a | `BN-G-matched`, `LAT-P-reinit`, `BN-G-iv-vm-asp`, each with initialization seed 1001 and 1002 | 666 | 6 |
| C5b | `LAT-P-rand2`, `LAT-P-rand3` (derangements from `random.Random(20261012)` / `(20261013)`, frozen in `src/bnrep/reps.py`; no fixed points, no agreement with the original derangement) | 666, 1234 | 4 |

Reference runs, already done:
- initialization seed 666: the original C3 runs at training seeds 666 and 1234;
- `LAT-P` at seed 666;
- the original `LAT-P-rand`.

## Metrics

Same as C3:
- **Primary:** Whisper-BengaliAI corpus CER on SLR37 test_seen at u3000.
- **Secondary:** the wav2vec2 sign check.
- **Interval:** paired bootstrap over sentences, 2,000 resamples, seed 20261006.

## Tests (complete list, implemented in `tools/analyze_c5.py`)

**C5a.** For each new initialization seed k ∈ {1001, 1002}, training seed 666, one run per cell:

| id | contrast | predicted |
|---|---|---|
| C5a-H1a-k | `LAT-P` − `LAT-P-reinit` (init k) | < 0 |
| C5a-H3path-k | `BN-G-matched` (init k) − `BN-G-iv-vm-asp` (init k) | > 0 |

- **Pass criteria:** predicted sign; |Δ| > CI half-width; |Δ| > 2 × the largest C3 training-seed SD of the arms
  involved (a stand-in, because one run per cell has no seed SD of its own); and wav2vec2 agreeing in sign.
- **Conclusion "robust to the initialization seed":** both k pass for that contrast.
- **Descriptive:** for each fresh-row arm, report the SD across the 3 initialization seeds (training seed 666)
  next to the SD across the 3 training seeds (initialization seed 666).

**C5b.** For each new derangement r ∈ {2, 3}, mean over training seeds 666 and 1234:

| id | contrast | predicted |
|---|---|---|
| C5b-H2-r | `LAT-P-rand`r − `LAT-P-reinit` | > 0 |

- `LAT-P-reinit` uses initialization seed 666 and training seeds 666 and 1234.
- **Pass criteria:** gate G6 as in C3, with 2 × the largest seed SD over the two seeds, plus the wav2vec2 sign.
- **Conclusion "H2 does not depend on the particular derangement":** both r pass.
- **Descriptive:** CER of all three derangements (seeds 666 and 1234) and their spread.

## Multiplicity and reporting

- 6 tests, all listed above.
- Any failure is reported as a qualification of the corresponding finding, not hidden or re-run.

## Known limitations stated in advance

- C5a varies initialization at one training seed, so seed and initialization effects are not fully crossed.
- The C5a gate borrows the C3 seed SD as an estimate.
- C5 runs on SLR37 only.
