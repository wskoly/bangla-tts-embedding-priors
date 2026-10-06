# SLR37 statistics (computed from files on disk)

Root: `data\raw\slr37\bn_bd`  
Transcript SHA-256: `7de5325b40d13dd5897b97d763e66c3fdd423ea0d1ebc5aadb9bd2bc2f8f814a`

| Quantity | Value |
|---|---|
| Utterance ids (audio ∪ transcript) | 1891 |
| WAV files | 1891 |
| Transcript lines | 1891 |
| Audio without transcript / transcript without audio | 0 / 0 |
| Unreadable audio | 0 |
| **Total duration** | **2.939 h** |
| Utterance duration (s) | mean 5.59 (sd 2.14); median 5.21; min 1.79; p05 2.82; p95 9.64; max 18.01 |
| Sample rates | {48000: 1891} |
| Channels / subtype | {1: 1891} / {'PCM_16': 1891} |
| **Speakers** (from filename) | **6** |
| Utterances per speaker | mean 315.2 (sd 131.8); median 289.0; min 110.0; p05 110.0; p95 467.0; max 473.0 |
| Minutes per speaker | mean 29.39 (sd 11.14); median 29.05; min 13.34; p05 13.34; p95 37.31; max 46.62 |
| Characters per utterance | mean 51.5 (sd 28.6); median 45.0; min 4.0; p05 12.0; p95 103.0; max 197.0 |
| Words per utterance | mean 8.2 (sd 4.5); median 8.0; min 1.0; p05 2.0; p95 16.0; max 30.0 |
| Characters per second | mean 8.79 (sd 2.59); median 8.95; min 1.27; p05 3.91; p95 12.77; max 16.30 |
| Peak amplitude | mean 0.764 (sd 0.135); median 0.804; min 0.249; p05 0.481; p95 0.914; max 1.000 |
| RMS (dBFS) | mean -22.0 (sd 2.3); median -21.5; min -32.4; p05 -26.9; p95 -19.2; max -15.3 |
| Leading silence (s) | mean 0.87 (sd 0.29); median 0.84; min 0.06; p05 0.48; p95 1.36; max 3.16 |
| Trailing silence (s) | mean 1.11 (sd 0.69); median 0.92; min 0.00; p05 0.44; p95 2.62; max 5.90 |
| Unique transcripts | 1848 |
| Duplicate-text groups / utterances | 30 / 73 |
| Duplicate texts read by >1 speaker | 26 |
| Transcripts with: NFC change / Latin letters / ASCII digits / Bengali digits / ZWJ-ZWNJ / punctuation | 176 / 2 / 0 / 0 / 18 / 472 |
| Flag counts | {'long_edge_silence': 1028, 'dup_text': 73, 'dur_low_tail': 9, 'dur_high_tail': 9} |
| Overlap with Google `prompts.tsv` | {'google_prompts': 1891, 'ids_in_slr37': 1891, 'same_text_for_shared_ids': 1891, 'slr37_unique_texts_in_google': 1848} |
| Non-WAV files | line_index.tsv |

Gender: not inferred. Report only if corpus metadata provides it.

## Speakers (top 15 by duration)

| speaker | utts | minutes |
|---|---|---|
| 03042 | 473 | 46.6 |
| 00737 | 467 | 37.3 |
| 01232 | 348 | 31.6 |
| 02194 | 289 | 29.1 |
| 00779 | 204 | 18.3 |
| 01701 | 110 | 13.3 |

Full list: `speakers.tsv`. Cross-speaker duplicate texts (first 10, truncated): ['জয়দেবপুর টাঙ্গাইল জামালপুর মহাসড়ক এর স', 'সাভার মানিকগঞ্জ মহাসড়ক এর সাথে চলতে থাক', 'বন্ধ সকাল এগারো টায় খুলবে', 'ঢাকা কুষ্টিয়া মহাসড়ক এর সাথে চলতে থাকু', 'বাতিল', 'রাজেন্দ্রপুর কাপাসিয়া টোক সড়ক এর সাথে ', 'মাদারীপুর ঢাকা মহাসড়ক এ থাকতে ডান দিক ধ', 'কিছু বিড়ালের ছবি এই নিন', 'আর্টিস্ট তালিকা', 'ঢাকা আরিচা মহাসড়ক এ থাকতে অল্প ডান দিক ']

Flag definitions: clipping = >0.1 % samples at |x| ≥ 0.999; long_edge_silence = >1 s below -40.0 dBFS at either edge; dur_low/high_tail = outside the 0.5–99.5 percentile range.
