# Pilot v1_1: first representation comparison (observations, no claims)

**Date:** 2026-10-07
**Configuration:** `configs/pilot_v1_1.json` (frozen; online-weight evaluation, D-024)
- F5-TTS v1 Base, `train_1h` (1.053 h trimmed audio, 5 speakers)
- 3,000 updates, effective batch 4,000 frames, LR 1e-5, warmup 300
- Seeds 666 and 1234; 3 arms

**Evaluation:**
- Whisper-medium BengaliAI (primary) and wav2vec2-XLS-R bn (secondary).
- Bengali-script references, scoring normalization fixed in advance (D-015).
- Ground-truth durations, identical across arms (D-022).
- ASR floor on real speech: CER 1.93 % (test_seen).

Full tables: `pilot_v1_1_analysis_tugstugi_bengaliai-asr_whisper-medium.md` and `pilot_v1_1_analysis_wav2vec2-xls-r-300m-bengali.md`.

## 1. Learning curves (fixed 50-utterance set, Whisper CER %, mean of 2 seeds)

| arm | u0 (zero-shot) | u500 | u1000 | u2000 | u3000 |
|---|---|---|---|---|---|
| BN-G (Bengali script) | 105.2 | 93.3 | 90.4 | 79.6 | 71.5 |
| LAT-G-det (ITRANS) | 64.5 | 37.6 | 22.6 | 13.8 | 11.4 |
| LAT-P (Google ASCII phonemes) | 38.2 | 21.6 | 14.1 | 9.1 | 8.0 |

## 2. Final test sets (update 3,000, Whisper CER %)

| arm | test_seen (primary) | test_unseen | seed SD (seen) |
|---|---|---|---|
| BN-G | 67.97 (66.81, 69.12) | 73.32 | 1.64 |
| LAT-G-det | 11.10 (11.01, 11.18) | 10.54 | 0.12 |
| LAT-P | **7.54** (7.83, 7.25) | **6.05** | 0.41 |

**Gate G6** requires |ΔCER| > paired-bootstrap CI half-width AND > 2 × seed SD. It **passes for every pair** on test_seen, test_unseen and the fixed set, and with the secondary ASR as well:
- BN-G − LAT-P: +60.4 [+59.0, +61.8]
- BN-G − LAT-G-det: +56.9 [+55.3, +58.4]
- LAT-G-det − LAT-P: +3.6 [+2.4, +4.6]

The secondary ASR has higher absolute CER (LAT-P 18.4, LAT-G-det 21.3, BN-G 65.5 on test_seen) but the same ordering and G6 outcome.

## 3. What the pilot does and does not show

**Observed:**
- The ordering LAT-P < LAT-G-det < BN-G holds at every checkpoint, for both seeds, both test sets and both ASRs.
- Seed-to-seed variation is small relative to the arm differences.

**The within-Latin comparison is the cleaner one.** LAT-G-det and LAT-P both reuse pretrained Latin embeddings, so neither needs new embeddings, and they differ in phonological content. Pronunciation-explicit input is ahead at every checkpoint:
- u1000: 14.1 vs 22.6
- u3000: 7.5 vs 11.1 on test_seen

**The BN-G gap is NOT interpretable as a pure "script" effect yet.** Under this configuration BN-G must learn 59 new embeddings that are:
- initialized N(0, 1), whereas trained rows have std 0.62 (official `expand_model_embeddings`, D-019);
- trained at LR 1e-5 for 3,000 updates.

Its curve is still falling steeply at u3000. The gap therefore mixes two things that this pilot cannot separate:
- (a) the benefit of reusing pretrained Latin embeddings (script);
- (b) slow optimization of new embeddings under this initialization / LR / budget.

**The zero-shot point (u0) is not a fair BN-G comparison** (random new embeddings). It does show that the English/Chinese-pretrained model reading LAT-P is already partly intelligible (38 % CER) before any Bangla training, and reading ITRANS somewhat less so (64.5 %).

**Scope:** one data size (1 h), one corpus (SLR37 bn-BD read speech), one model, 3,000 updates, ASR-based intelligibility only (no PER, no listening test, no naturalness yet).

## 4. Controls needed before interpreting the script factor (pre-registered in D3 §6 / D-019)

| control | isolates |
|---|---|
| BN-G with matched-statistics init (new rows ~ N(0, 0.62)) | initialization scale vs script |
| LAT-P-reinit (Latin symbols, embeddings freshly initialized) | reuse of pretrained embeddings vs Latin symbols per se |
| LAT-P-rand (random bijective letter remap, same information and length) | pretrained Latin *phonetic* prior vs any reused embedding |
| (later) BN-P (phonemes in Bengali glyphs) | completes the script × content factorial |

## 5. Pipeline incidents during the pilot (no effect on computation)

- Background processes were killed when the terminal closed; the queue now runs under Task Scheduler (D-025).
- Windows EcoQoS halved training speed; the processes now opt out (D-026, incl. a ctypes fix).
- Interrupted runs restarted from scratch with the same seed (gated by `train_done.json`).
- An apparent identical BN-G u500 CER across seeds was a rounding coincidence (93.331 vs 93.293). Weights and hypotheses differ.
