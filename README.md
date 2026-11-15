# Character Embedding Priors and Script Structure in Low-Resource Bangla Text-to-Speech Adaptation

Code, configurations, frozen analysis plans and analysis outputs for a controlled study of adapting a
Latin-pretrained, character-level TTS model (F5-TTS) to Bangla. The study separates two factors: (i) whether the
input symbols have pretrained embedding rows, and (ii) the structure of the Bangla abugida script.

Authors: Wahid Sadique Koly ([ORCID 0000-0001-8869-9183](https://orcid.org/0000-0001-8869-9183)) and Homaira Adiba
([ORCID 0000-0001-5285-9448](https://orcid.org/0000-0001-5285-9448)), independent researchers.

Preprint: https://doi.org/10.20944/preprints202611.0988.v1

Audio samples: https://wskoly.github.io/bangla-tts-embedding-priors/ (built from the `gh-pages` branch).

## Abstract

Character-level text-to-speech (TTS) models pretrained on Latin-script data are usually adapted to a new language by
adding its characters to the vocabulary. We ask why this works poorly for Bangla, an abugida, when F5-TTS is
fine-tuned on one hour of speech for 3,000 updates: native Bengali characters give a character error rate (CER) of
67.96%, under an ASR model that scores 1.93% on real recordings. Controlled input representations separate two factors.
On identical phonemic Latin text, pretrained embedding rows lower CER by 22.04 percentage points (pp) relative to
freshly initialized rows, while assigning the same rows to the wrong sounds raises it by 51.53 pp. With fresh rows, a
lossless re-encoding of Bengali text (explicit inherent vowel, merged vowel forms, split aspirates) lowers CER by
47.56 pp, and pretrained rows help this restructured encoding less than a standard transliteration. All five tests
specified before the runs replicate on a second corpus of another Bangla variety, and, where tested, the directions hold across three
random draws of the new embeddings; the effect sizes, however, vary strongly with the draw. In an exploratory run with
five times more updates, the gap between the two Latin representations shrinks to 0.54 pp, so the findings concern
adaptation under a limited training budget.

## Main findings

All findings are about intelligibility measured with a Bangla ASR (CER), with F5-TTS v1 Base fine-tuned on about
1 h of speech for 3,000 updates. Effect sizes are for the SLR37 seen speakers. Signed values are contrasts
Δ = CER(A) − CER(B) as defined in the paper; the other values are magnitudes.

| | Finding | Status |
|---|---|---|
| H1 | Pretrained Latin rows beat fresh rows for the same phonemic text (22 pp lower CER) | direction: robustness (SLR37) + replicated (Rasa); H1a direction holds over 3 row-init draws (one training seed each) |
| H2 | A scrambled assignment of pretrained rows is *worse* than fresh rows (52 pp higher CER): rows carry sound-specific priors | robustness + replicated + holds for 3 scrambled assignments; fresh comparator from one row-init draw, so the size depends on that draw |
| H3 | With fresh rows, the lossless re-encoding (explicit inherent vowel, merged vowel forms, split aspirates) lowers CER (48 pp over the path, mostly from the last two steps); the inherent-vowel step alone is inconclusive | single steps: robustness; path: replicated + holds over 3 row-init draws |
| H4 | The benefit of pretrained rows is smaller for the restructured encoding (sub-additive) | robustness + replicated (one row-init draw) |
| H5 | Effects persist at 3/10/30× embedding learning rate | robustness (SLR37 only; the 10× arms are exploration runs) |
| – | **Effect sizes depend on the random draw of the fresh rows**: H1a is −22, −17 and −67 pp and the H3 path +48, +28 and +38 pp for init seeds 666, 1001 and 1002 | C5a (pre-specified descriptive); sizes not established |
| – | With 5× longer training the ITRANS/phoneme gap closes to +0.5 pp: the effects concern limited-budget adaptation | exploratory, 1 seed |

The fresh-row arms vary with an SD of 11.6–27.4 pp CER across row-init draws, against 0.6–1.6 pp across training
seeds. The C3/C1 confidence intervals cover sentence sampling and the 2σ gate covers training seeds, so neither
includes this variance. Where tested, the directions held for all three draws (one training seed each), which shows
they are not tied to one draw, not that they hold for every draw; magnitudes refer to init seed 666.

Evidence levels:
- **exploratory**: hypotheses were formed from these runs.
- **robustness**: tested by a plan frozen before the runs, on the same corpus (C3, tag `plan-C3`).
- **replicated**: tested by a plan frozen before the runs, on a second corpus and Bangla variety (C1,
  tag `plan-C1`).
- **controls**: row-init seed and scrambled assignment, tested by a plan frozen before the runs on SLR37 (C5,
  tag `plan-C5`). All 6 tests pass.
- **post hoc**: two-level bootstrap, Holm correction, per-seed agreement and effect sizes for all frozen tests
  (`docs/reports/sensitivity_stats.md`). They change no verdict.

The commits that froze each analysis plan before its runs carry the annotated tags `plan-C3`, `plan-C1` and
`plan-C5` (`git tag -n1`); their commit dates come before the runs they govern. Labels such as `D-046` in code
comments, reports and commit messages refer to entries in our research log, which is not part of this repository.

## Repository map

```
src/bnrep/        Bangla text: normalization, Google lexicon, G2P (g2p/), all representation converters (reps.py)
src/corpus/       corpus statistics, audio preparation (trim + 24 kHz), frozen splits, data profiles (profile.py)
src/train/        vocabularies (vocab.py), F5 fine-tuning wrapper (f5_train.py), pilot runner (pilot.py)
src/infer/        F5 inference with ground-truth durations and fixed seeds
src/eval/         ASR scoring (asr.py; Whisper-BengaliAI primary, wav2vec2 secondary), fixed eval set
configs/          frozen run configs (pilot_*.json) and per-arm vocabularies (configs/vocab/)
tools/            run queues (run_pilot_*.sh), frozen analyses (analyze_*.py), C1 data build, number/figure scripts
docs/             frozen analysis plans (C1/C3/C5), C1 data rules, reports written by the analyses (docs/reports/)
paper/            generated outputs: numbers.tex/numbers.json, sensitivity.json, transcripts.tex, figs/, the font
tests/            unit tests for the converters (pytest)
data/derived/     small tracked metadata (manifests, splits, indexes, ASR floors); audio is not tracked
```

Not in git (large or regenerable): `data/raw/`, all `*.wav`, and `runs/` (checkpoints, generated audio, per-run
evaluation files).

## Replication

### 1. Environment

The study was run on Windows 11 with an RTX 5070 Ti (16 GB), CUDA 12.8 and Python 3.11.

```powershell
powershell -ExecutionPolicy Bypass -File tools\setup_env.ps1   # FFmpeg, uv venv, torch cu128, f5-tts
uv pip install --python .venv\Scripts\python.exe -r requirements-lock.txt   # exact versions used
```

Key versions: `f5-tts 1.1.22`, `torch 2.11.0+cu128`, `transformers 5.18.0`, `jiwer 4.0.0`,
`indic_transliteration 2.3.82`. Base checkpoint: `SWivid/F5-TTS` → `F5TTS_v1_Base/model_1250000.safetensors`.

On Linux, install torch for your CUDA version, then `pip install -r requirements-lock.txt` (drop Windows-only
packages if pip complains). Shell scripts in `tools/` are bash; the `.cmd` files only wrap them for Windows Task
Scheduler.

### 2. Data and resources

| Resource | Licence | Where it goes |
|---|---|---|
| OpenSLR **SLR37** `bn_bd` (Sodimana et al. 2018) | CC BY-SA 4.0 | `data/raw/slr37/bn_bd/` |
| Google **language-resources** Bangla lexicon | CC BY 4.0 | `data/external/google_language_resources_bn/lexicon.tsv` |
| **Rasa** Bengali (`ai4bharat/Rasa`, gated, auto-approval) | CC BY 4.0 | built by `tools/c1_rasa_build.py` |
| Noto Serif Bengali (figure font) | SIL OFL | `paper/fonts/` (included) |

```bash
python src/corpus/slr37_stats.py --root data/raw/slr37/bn_bd --out-dir data/derived/slr37_bn_bd \
       --report docs/reports/slr37_bn_bd_stats.md
python src/corpus/make_splits.py --manifest data/derived/slr37_bn_bd/manifest.tsv     # frozen splits v1
python -m src.corpus.prep_audio --out data/derived/audio24k_v1                          # trim + 24 kHz
python -m src.bnrep.g2p.train --out runs/g2p/v1 --report docs/reports/g2p_v1.md         # OOV G2P (CPU)
python -m src.train.vocab --reps BN-G,BN-G-iv,BN-G-iv-vm,BN-G-iv-vm-asp,LAT-G-det,LAT-G-asp,LAT-P,LAT-P-rand
huggingface-cli login                       # Rasa is gated
python tools/c1_rasa_build.py               # downloads only the needed shards, deletes them after extraction
```

Split, manifest and vocabulary files are tracked, together with their SHA-256 hashes in `docs/reports/`, so
you can check that a rebuild matches. The C5 vocabularies `LAT-P-rand2` and `LAT-P-rand3` are tracked in
`configs/vocab/`; their symbol inventory is identical to `LAT-P`.

### 3. Training and evaluation

One run trains one arm with one seed under a frozen config, then evaluates it: synthesis, then ASR scoring with
both models.

```bash
export PILOT_CONFIG=configs/pilot_v8a.json        # select the frozen config
python -m src.train.pilot train --rep LAT-P --seed 4242
python -m src.train.pilot eval  --rep LAT-P --seed 4242
```

Full studies are queued by `tools/run_pilot_*.sh`. The queues resume after a crash: a run is skipped once its
`train_done.json` and `eval_summary.json` exist.

| Study | Configs | Queue | Cost (RTX 5070 Ti) |
|---|---|---|---|
| Exploration (pilots v1_1–v7) | `pilot_v1_1` … `pilot_v7` | `run_pilot_v*.sh` | ~40 runs |
| **C3** robustness (3rd seed, LR sweep) | `pilot_v8a`, `pilot_v8b` | `run_pilot_v8.sh` | 22 runs × ~35 min |
| **C1** replication on Rasa | `pilot_c1a`, `pilot_c1b` (`data_profile: rasa_bn_v1`) | `run_pilot_c1a.sh`, `run_pilot_c1b.sh` | 24 runs × ~36 min |
| **C5** controls (row-init seed, scrambled assignment) | `pilot_c5` | `run_pilot_c5.sh` | 10 runs × ~35 min |
| Long-training check | `pilot_x1` | `run_pilot_x1.sh` | 2 runs × ~85 min |

A run needs about 10 GB of VRAM. The fixed recipe for every arm is 3,000 updates, LR 1e-5 with 300 warm-up
updates, 4,000 frames per update, bf16, NFE 32, CFG 2, ground-truth durations and a fixed seed per utterance.
New embedding rows are drawn with a fixed generator (`init_seed`, default 666); the C5 arms named `*-is1001` and
`*-is1002` use other seeds.

### 4. Analyses (frozen before their runs)

```bash
python tools/analyze_c3.py                             # -> docs/reports/c3_hypothesis_tests.md
DATA_PROFILE=rasa_bn_v1 python tools/analyze_c1.py     # -> docs/reports/c1_replication_tests.md
python tools/analyze_c5.py                             # -> docs/reports/c5_controls.md
python tools/analyze_x1.py                             # long-training check (exploratory)
python tools/sensitivity_stats.py                      # post hoc -> docs/reports/sensitivity_stats.md
python tools/letter_confusion.py                       # post hoc -> docs/reports/letter_confusion.md
```

**Decision rule (G6).** A test passes when, in the predicted direction:
- |Δ| exceeds the 95 % paired-bootstrap CI half-width;
- |Δ| exceeds twice the largest seed SD of the arms involved (C5a: the C3 training-seed SD as a stand-in);
- wav2vec2 agrees in sign.

Plans: `docs/C3_analysis_plan.md`, `docs/C1_analysis_plan.md`, `docs/C5_analysis_plan.md`.

### 5. Numbers, figures and transcripts reported in the paper

```bash
python tools/paper_numbers.py      # every reported number; fails if any differs from the frozen reports
python tools/paper_figs.py         # figures (paper/figs/)
python tools/paper_transcripts.py  # example transcripts table (paper/transcripts.tex)
```

`paper_numbers.py` reads the per-run evaluation files under `runs/` and writes `paper/numbers.tex` (one macro per
number) and `paper/numbers.json`. Running it on our run outputs reproduces the tracked `paper/numbers.tex` exactly.

## Known limitations

- **Measurement:** intelligibility is measured by ASR only; naturalness has not been assessed.
- **Row initialization:** all C3/C1 arms share one draw of the fresh rows. C5a shows that effect sizes change by
  tens of pp with the draw (SLR37, one training seed per draw); Rasa, H1b, the single H3 steps, H2 (against other
  fresh-row draws), H4 and H5 were not re-tested over draws.
- **Scope:** one model, one language, about 1 h of data, a 3k-update budget, and one unseen speaker per corpus.
- **Design:** the encoding steps are cumulative and order-dependent. LAT-G-asp uses different letters than ITRANS.
- **Lexicon:** the Google lexicon is bn-BD, and its token coverage on the bn-IN Rasa seen-speaker test set is 84.7 %.
- **Letter choices:** LAT-P (from the lexicon) and LAT-G-asp write চ as `c`, which the English prior reads as /k/
  early in training. Case spellings (`T`/`t`, `D`/`d` in LAT-P and ITRANS) push retroflex words toward the
  dental letter with pretrained rows; `th`, `v` and `Ch` showed no clear effect (post hoc,
  `docs/reports/letter_confusion.md`). No arm tested prior-aligned spellings such as `ch`/`chh`.
- **Hardware:** the original machine hard-reset under sustained GPU load, so the queues are resumable.

## Citation

```bibtex
@article{koly2026embeddingpriors,
  title   = {Character Embedding Priors and Script Structure in Low-Resource Bangla Text-to-Speech Adaptation},
  author  = {Koly, Wahid Sadique and Adiba, Homaira},
  journal = {Preprints},
  year    = {2026},
  doi     = {10.20944/preprints202611.0988.v1},
  url     = {https://doi.org/10.20944/preprints202611.0988.v1},
  note    = {Preprint}
}
```

## Licences

| Part | Licence |
|---|---|
| Code (`src/`, `tools/`, `tests/`, `configs/`) | Apache-2.0, see `LICENSE`. Copyright 2026 Wahid Sadique Koly and Homaira Adiba. |
| Files derived from SLR37 (`data/derived/slr37_bn_bd/`, `splits/`, `audio24k_v1/`, `eval/`, `asr_floor_v1/`, `rep_bench_v1/`, `g2p/`) | CC BY-SA 4.0, as SLR37 (Sodimana et al. 2018) |
| Files derived from Rasa (`data/derived/rasa_bn/`, `audio24k_rasa_v1/`, `eval_rasa_v1/`, `asr_floor_rasa_v1/`) | CC BY 4.0, as Rasa (Varadhan et al. 2024) |
| Google Bangla lexicon (`data/external/google_language_resources_bn/`) and the curation files in `data/curation/` | CC BY 4.0 (see the `LICENSE` and `PROVENANCE.txt` there) |
| Audio samples (`gh-pages` branch) | Synthetic speech from models fine-tuned on SLR37 and Rasa, in the voices of those corpora's speakers: CC BY-SA 4.0 for SLR37 voices, CC BY 4.0 for Rasa voices. Do not use them to imitate the speakers. |
| Reports, generated numbers and figures (`docs/`, `paper/`) | CC BY 4.0 |
| Noto Serif Bengali (`paper/fonts/`) | SIL Open Font License (`paper/fonts/OFL.txt`) |

Model checkpoints are not released. The pretrained F5-TTS weights are not part of this repository and keep their own
licence.
