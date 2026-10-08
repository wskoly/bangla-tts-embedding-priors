# F5 vocabularies v1 (per representation)

Tokenization: one token per code point via F5 `list_str_to_idx`; `convert_char_to_pinyin` bypassed (D-016). Every split validated: unknown symbols = 0 (enforced by exception).

| rep | base size | added | final size | embedding rows × dim | new embeddings | symbols used (from base) | tokens train_full / val / test_seen / test_unseen | sha256 (first 12) |
|---|---|---|---|---|---|---|---|---|
| BN-G-iv | 2545 | 58 | 2603 | 2604 × 512 | 58 | 62 (4) | 91917 / 2718 / 8936 / 6300 | `f555d44fed7a` |
| BN-G-iv-vm | 2545 | 48 | 2593 | 2594 × 512 | 48 | 52 (4) | 91917 / 2718 / 8936 / 6300 | `728f818a57e4` |
| BN-G-iv-vm-asp | 2545 | 38 | 2583 | 2584 × 512 | 38 | 42 (4) | 94798 / 2795 / 9226 / 6522 | `28cca0a30773` |

Added symbols per arm:

- **BN-G-iv**: ঁ (U+0981) ং (U+0982) ঃ (U+0983) অ (U+0985) আ (U+0986) ই (U+0987) ঈ (U+0988) উ (U+0989) ঊ (U+098A) ঋ (U+098B) এ (U+098F) ঐ (U+0990) ও (U+0993) ঔ (U+0994) ক (U+0995) খ (U+0996) গ (U+0997) ঘ (U+0998) ঙ (U+0999) চ (U+099A) ছ (U+099B) জ (U+099C) ঝ (U+099D) ঞ (U+099E) ট (U+099F) ঠ (U+09A0) ড (U+09A1) ঢ (U+09A2) ণ (U+09A3) ত (U+09A4) থ (U+09A5) দ (U+09A6) ধ (U+09A7) ন (U+09A8) প (U+09AA) ফ (U+09AB) ব (U+09AC) ভ (U+09AD) ম (U+09AE) য (U+09AF) র (U+09B0) ল (U+09B2) শ (U+09B6) ষ (U+09B7) স (U+09B8) হ (U+09B9) ় (U+09BC) া (U+09BE) ি (U+09BF) ী (U+09C0) ু (U+09C1) ূ (U+09C2) ৃ (U+09C3) ে (U+09C7) ৈ (U+09C8) ো (U+09CB) ৌ (U+09CC) ৎ (U+09CE)
- **BN-G-iv-vm**: ঁ (U+0981) ং (U+0982) ঃ (U+0983) অ (U+0985) আ (U+0986) ই (U+0987) ঈ (U+0988) উ (U+0989) ঊ (U+098A) ঋ (U+098B) এ (U+098F) ঐ (U+0990) ও (U+0993) ঔ (U+0994) ক (U+0995) খ (U+0996) গ (U+0997) ঘ (U+0998) ঙ (U+0999) চ (U+099A) ছ (U+099B) জ (U+099C) ঝ (U+099D) ঞ (U+099E) ট (U+099F) ঠ (U+09A0) ড (U+09A1) ঢ (U+09A2) ণ (U+09A3) ত (U+09A4) থ (U+09A5) দ (U+09A6) ধ (U+09A7) ন (U+09A8) প (U+09AA) ফ (U+09AB) ব (U+09AC) ভ (U+09AD) ম (U+09AE) য (U+09AF) র (U+09B0) ল (U+09B2) শ (U+09B6) ষ (U+09B7) স (U+09B8) হ (U+09B9) ় (U+09BC) ৎ (U+09CE)
- **BN-G-iv-vm-asp**: ঁ (U+0981) ং (U+0982) ঃ (U+0983) অ (U+0985) আ (U+0986) ই (U+0987) ঈ (U+0988) উ (U+0989) ঊ (U+098A) ঋ (U+098B) এ (U+098F) ঐ (U+0990) ও (U+0993) ঔ (U+0994) ক (U+0995) গ (U+0997) ঙ (U+0999) চ (U+099A) জ (U+099C) ঞ (U+099E) ট (U+099F) ড (U+09A1) ণ (U+09A3) ত (U+09A4) দ (U+09A6) ন (U+09A8) প (U+09AA) ব (U+09AC) ম (U+09AE) য (U+09AF) র (U+09B0) ল (U+09B2) শ (U+09B6) ষ (U+09B7) স (U+09B8) হ (U+09B9) ় (U+09BC) ৎ (U+09CE)
