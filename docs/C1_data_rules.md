# C1 data rules: Rasa Bengali pilot (rasa_bn_v1), fixed before any audio download (2026-10-11, D-057)

**Source:** `ai4bharat/Rasa`, Bengali config (CC BY 4.0). Accessed with our HF account after we accepted the gating conditions.
- Metadata survey without audio: `tools/c1_rasa_survey.py` → `data/raw/rasa_bn/meta.tsv`.
- Shards are sorted by speaker (Male first, then Female); official test shards: 0–2 Male, 3 mixed, 4–6 Female.

## Speakers and styles

- **Seen / training speaker: Female. Unseen speaker: Male.** Fixed now; not changed after results.
- **Neutral styles only:** ALEXA, BB, BOOK, CONV, DIGI, INDIC, NEWS, SANGRAH, UMANG, WIKI.
- **Excluded emotion styles:** ANGER, DISGUST, FEAR, HAPPY, SAD, SURPRISE.

## Text rule (applied identically to every arm, before `normalize()`)

| step | rule |
|---|---|
| 1 | U+09F7 (৷, used as a danda look-alike) → । |
| 2 | remove U+200B, U+FEFF and quotes / brackets: `' " ‘ ’ “ ” ( )` |
| 3 | `-` → space; `,` `;` `:` `?` `!` → `.` |
| 4 | `normalize()` (unchanged: NFC, ZW removal, audited corrections, danda → `.`) |
| 5 | **exclude** an utterance if it contains Bengali or ASCII digits, Latin letters, or any symbol outside the frozen v1 vocabulary of any arm after conversion |

- **Only `.` remains as punctuation, exactly as in SLR37** (SLR37 text uses only `.`).
  Keeping `, ? !` would add symbols that the -reinit arms re-initialize but the BN-G arms keep pretrained, an asymmetry absent in the exploration.
  Pause cues are reduced for every arm equally; CER scoring ignores punctuation.
- **Vocabularies stay v1** (no new symbols are admitted; step 5).
- **LAT-P:** out-of-lexicon words go through G2P v1 (profile `allow_g2p`). The coverage and G2P share are reported. The coverage-restricted test subset is the primary analysis for LAT-P hypotheses (see `C1_corpus_shortlist.md`).

## Audio rule

- Raw duration 1.0–15.0 s.
- Edge-silence trim + resample 48 → 24 kHz with the unchanged `prep_audio` rule (−40 dBFS, 20 ms frames, 0.1 s margin).

## Splits (deterministic order: sha256(filename + "20261011"))

| split | source | size |
|---|---|---|
| test_seen | Female neutral rows of official test shard `test-00004` | 160 utterances |
| test_unseen | Male neutral rows of official test shard `test-00000` | 110 utterances |
| val | Female neutral rows of the training shards | 50 utterances |
| train_1h | Female neutral rows of the training shards, in hash order, until 1.0 h of edge-trimmed speech | ≈ 1.0 h |

- **Text-disjoint:** any NFC text in test_seen / test_unseen / val is removed from the train pool.
- **Training shards:** the first all-Female `train-*` shards in name order, as many as needed to reach val + 1 h (expected 2). Nothing beyond what is needed is downloaded.

## Eval set and references

- **fixed set:** the first 40 test_seen + the first 10 test_unseen items in hash order, used for the curves only. There are no tag quotas (the SLR37 quotas used SLR37-specific tags).
- **Reference per speaker:**
  - Female: from val; Male: from test_unseen items not in the fixed set.
  - Choose the utterance closest to 4.0 s of trimmed speech whose words are all in the lexicon or supplement.
  - Stored as `data/derived/eval_rasa_v1/{fixed_v1,refs_v1}.tsv` (same file names as SLR37, separate directory).

## Pilot go / no-go (fixed in D-055; unchanged)

- All 5 runs complete.
- ASR floor (ground-truth audio) Whisper CER ≤ 10 on test_seen and test_unseen.
- LAT-P test token coverage ≥ 85 %; otherwise LAT-P is judged on the coverage-restricted subset only.
