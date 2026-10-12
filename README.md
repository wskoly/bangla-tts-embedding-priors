# Symbol Priors or Script Structure? Bangla adaptation of a Latin-pretrained TTS model

Code, configurations, frozen analysis plans and paper sources for a controlled study of **why native-script
adaptation of a Latin-pretrained, character-level TTS model (F5-TTS) fails for Bangla**, and how much of the
failure is due to (i) missing pretrained symbol priors versus (ii) the structure of the abugida script.

Paper draft: [`paper/main.tex`](paper/main.tex) (arXiv preprint template, XeLaTeX).
Decision log (every choice, in order, with reasons): [`docs/decisions.md`](docs/decisions.md).

## Main findings

All findings are about intelligibility measured with a Bangla ASR (CER), with F5-TTS v1 Base fine-tuned on about
1 h of speech for 3,000 updates.

| | Finding | Status |
|---|---|---|
| H1 | Reusing pretrained Latin rows for phonetically plausible text beats the same text on fresh rows (−22 pp CER) | robustness (SLR37) + replicated (Rasa) |
| H2 | A scrambled relabelling onto pretrained rows is *worse* than fresh rows (+52 pp): rows carry sound-specific priors | robustness + replicated |
| H3 | With fresh rows, merging vowel forms and splitting aspirates lowers CER (−48 pp over the path); an explicit inherent vowel has no clear effect | robustness; path replicated |
| H4 | The two factors are sub-additive | robustness + replicated |
| H5 | Effects persist at 3/10/30× embedding learning rate | robustness (SLR37 only) |
| — | With 5× longer training the ITRANS/phoneme gap closes to +0.5 pp: the effects concern limited-budget adaptation | exploratory, 1 seed |

Evidence levels:
- **exploratory**: hypotheses were formed from these runs.
- **robustness**: tested by a plan frozen before the runs, on the same corpus (C3, commit `0c391f5`).
- **replicated**: tested by a plan frozen before the runs, on a second corpus and dialect (C1, commit `1aefe31`).

## Repository map

```
src/bnrep/        Bangla text: normalization, Google lexicon, G2P (g2p/), all representation converters (reps.py)
src/corpus/       corpus statistics, audio preparation (trim + 24 kHz), frozen splits, data profiles (profile.py)
src/train/        vocabularies (vocab.py), F5 fine-tuning wrapper (f5_train.py), pilot runner (pilot.py)
src/infer/        F5 inference with ground-truth durations and fixed seeds
src/eval/         ASR scoring (asr.py; Whisper-BengaliAI primary, wav2vec2 secondary), fixed eval set
configs/          frozen run configs (pilot_*.json) and per-arm vocabularies (configs/vocab/)
tools/            run queues (run_pilot_*.sh), frozen analyses (analyze_*.py), C1 data build, paper/figure scripts
docs/             plans (C1/C3/C4), decision log, literature notes (docs/lit/), reports (docs/reports/)
paper/            LaTeX sources, numbers.tex (generated), figs/ (generated), refs.bib, claims ledger
listening/        C4 listening-test template (page built by tools/c4_build_listening.py)
tests/            unit tests for the converters (pytest)
data/derived/     small tracked metadata (manifests, splits, indexes, ASR floors); audio is not tracked
```

Not in git (large or regenerable): `data/raw/`, all `*.wav`, `runs/` (checkpoints, generated audio), the compiled
PDF and the built listening page.

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
| OpenSLR **SLR37** `bn_bd` (Kjartansson et al. 2018) | CC BY 4.0 | `data/raw/slr37/bn_bd/` |
| Google **language-resources** Bangla lexicon | CC BY 4.0 | `data/external/google_language_resources_bn/lexicon.tsv` |
| **Rasa** Bengali (`ai4bharat/Rasa`, gated, auto-approval) | CC BY 4.0 | built by `tools/c1_rasa_build.py` |
| Noto Serif Bengali (paper font) | SIL OFL | `paper/fonts/` (included) |

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
you can check that a rebuild matches.

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
| Long-training check | `pilot_x1` | `run_pilot_x1.sh` | 2 runs × ~85 min |

A run needs about 10 GB of VRAM. The fixed recipe for every arm is 3,000 updates, LR 1e-5 with 300 warm-up
updates, 4,000 frames per update, bf16, NFE 32, CFG 2, ground-truth durations and a fixed seed per utterance.

### 4. Analyses (frozen before their runs)

```bash
python tools/analyze_c3.py                             # -> docs/reports/c3_hypothesis_tests.md
DATA_PROFILE=rasa_bn_v1 python tools/analyze_c1.py     # -> docs/reports/c1_replication_tests.md
python tools/analyze_x1.py                             # long-training check (exploratory)
```

**Decision rule (G6).** A test passes when, in the predicted direction:
- |Δ| exceeds the 95 % paired-bootstrap CI half-width;
- |Δ| exceeds twice the largest seed SD of the arms involved;
- wav2vec2 agrees in sign.

Plans: `docs/C3_analysis_plan.md`, `docs/C1_analysis_plan.md`, `docs/C4_listening_plan.md`.

### 5. Paper

```bash
python tools/paper_numbers.py    # recompute every number; fails if any differs from the frozen reports
python tools/paper_figs.py       # figures at print size
cd paper && tectonic main.tex    # or Overleaf / arXiv with the XeLaTeX compiler
```

No number is typed by hand: `main.tex` uses `\V{key}` macros from `paper/numbers.tex`. Claims and their evidence
levels are listed in `paper/claims.md`.

### 6. Listening test (C4, prepared, not yet run)

```bash
python tools/c4_build_listening.py   # -> listening/listening_test.html (self-contained, ~4.6 MB)
```

The test has two parts:
- **Ratings:** 10 sentences in MUSHRA style (5 systems, the hidden reference and a 3.5 kHz anchor).
- **A/B choices:** 16 pairs.

The analysis plan was frozen before collection. `listening/stimuli_map.json` maps the opaque codes to systems; keep
it private while the test runs.

## Known limitations

- **Measurement:** intelligibility is measured by ASR only; naturalness has not been assessed yet (C4 pending).
- **Scope:** one model, one language, about 1 h of data, a 3k-update budget, and one unseen speaker per corpus.
- **Design:** the encoding steps are cumulative and order-dependent. LAT-G-asp uses different letters than ITRANS.
- **Lexicon:** the Google lexicon is bn-BD, and its token coverage on bn-IN Rasa is about 84 %.
- **Letter choices:** LAT-P writes চ as `c`, which the English prior reads as /k/ early in training (D-063).
- **Hardware:** the original machine hard-reset under sustained GPU load. Queues are resumable for that reason;
  see the decision log for every reset and rerun.

## Future work

1. **Run the C4 listening test.** Recruit at least 15 native listeners and analyse per `docs/C4_listening_plan.md`.
2. **Use a second abugida (C2).** Run the same encoding path and reuse controls on Hindi (Devanagari) to test
   generality beyond Bangla.
3. **Choose letters to fit the prior.** Choose romanization letters by measuring the pretrained model's zero-shot
   reading of candidate spellings, e.g. `ch` vs `c` for চ. Then test a prior-aligned phonemic arm (D-063).
4. **Test budget and convergence curves.** Run multi-seed long-training and epoch-scaled data-size curves. They
   would show whether any representation advantage survives at convergence (D-042, D-065).
5. **Try other models and initializations.** Test a second TTS architecture, and smarter initialization of new
   rows (e.g. from phonetically similar Latin rows, cf. WECHSEL/FOCUS).
6. **Analyse errors by phonological category.** Use phone-level scoring for the inherent vowel, conjuncts,
   aspiration, retroflex vs dental, and nasalization.
7. **Check coverage of uncovered text.** Evaluate LAT-P with a bn-IN lexicon or a stronger G2P on out-of-lexicon
   words, and evaluate ITRANS on rare words and names.

## Citation

```bibtex
@misc{koly2026symbolpriors,
  title  = {Symbol Priors or Script Structure? Why Native-Script Adaptation of a Latin-Pretrained TTS Model
            Fails for Bangla},
  author = {Koly, Wahid Sadique},
  year   = {2026},
  note   = {Preprint}
}
```

## Licences

Code: add a licence of your choice before publishing; none has been chosen yet. Data and resources keep their
own licences (table above). `paper/arxiv.sty` is MIT (kourgeorge/arxiv-style). Noto Serif Bengali is under the
SIL OFL.
