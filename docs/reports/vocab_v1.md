# F5 vocabularies v1 (per representation)

Tokenization: one token per code point via F5 `list_str_to_idx`; `convert_char_to_pinyin` bypassed (D-016). Every split validated: unknown symbols = 0 (enforced by exception).

| rep | base size | added | final size | embedding rows × dim | new embeddings | symbols used (from base) | tokens train_full / val / test_seen / test_unseen | sha256 (first 12) |
|---|---|---|---|---|---|---|---|---|
| BN-G | 2545 | 59 | 2604 | 2605 × 512 | 59 | 63 (4) | 81655 / 2362 / 7847 / 5491 | `db03fa29fa47` |
| LAT-G-det | 2545 | 0 | 2545 | 2546 × 512 | 0 | 38 (38) | 96614 / 2864 / 9369 / 6634 | `4e173934be56` |
| LAT-P | 2545 | 0 | 2545 | 2546 × 512 | 0 | 30 (30) | 86846 / 2586 / 8401 / 5969 | `4e173934be56` |
| IPA-P | 2545 | 4 | 2549 | 2550 × 512 | 4 | 32 (28) | 84566 / 2500 / 8190 / 5836 | `55b560072d8d` |
| LAT-P-dots | 2545 | 0 | 2545 | 2546 × 512 | 0 | 29 (29) | 102904 / 3044 / 9942 / 7019 | `4e173934be56` |
| LAT-G-iso | 2545 | 3 | 2548 | 2549 × 512 | 3 | 41 (38) | 93737 / 2754 / 9090 / 6448 | `b683c138ad1a` |
| LAT-G-colloq | 2545 | 0 | 2545 | 2546 × 512 | 0 | 24 (24) | 96443 / 2851 / 9332 / 6619 | `4e173934be56` |
| LAT-uroman | 2545 | 0 | 2545 | 2546 × 512 | 0 | 24 (24) | 108689 / 3232 / 10553 / 7438 | `4e173934be56` |

Added symbols per arm:

- **BN-G**: ঁ (U+0981) ং (U+0982) ঃ (U+0983) অ (U+0985) আ (U+0986) ই (U+0987) ঈ (U+0988) উ (U+0989) ঊ (U+098A) ঋ (U+098B) এ (U+098F) ঐ (U+0990) ও (U+0993) ঔ (U+0994) ক (U+0995) খ (U+0996) গ (U+0997) ঘ (U+0998) ঙ (U+0999) চ (U+099A) ছ (U+099B) জ (U+099C) ঝ (U+099D) ঞ (U+099E) ট (U+099F) ঠ (U+09A0) ড (U+09A1) ঢ (U+09A2) ণ (U+09A3) ত (U+09A4) থ (U+09A5) দ (U+09A6) ধ (U+09A7) ন (U+09A8) প (U+09AA) ফ (U+09AB) ব (U+09AC) ভ (U+09AD) ম (U+09AE) য (U+09AF) র (U+09B0) ল (U+09B2) শ (U+09B6) ষ (U+09B7) স (U+09B8) হ (U+09B9) ় (U+09BC) া (U+09BE) ি (U+09BF) ী (U+09C0) ু (U+09C1) ূ (U+09C2) ৃ (U+09C3) ে (U+09C7) ৈ (U+09C8) ো (U+09CB) ৌ (U+09CC) ্ (U+09CD) ৎ (U+09CE)
- **LAT-G-det**: none
- **LAT-P**: none
- **IPA-P**: ɖ (U+0256) ɟ (U+025F) ʈ (U+0288) ̯ (U+032F)
- **LAT-P-dots**: none
- **LAT-G-iso**: ̐ (U+0310) ̥ (U+0325) ẏ (U+1E8F)
- **LAT-G-colloq**: none
- **LAT-uroman**: none
