# F5 vocabularies v1 (per representation)

Tokenization: one token per code point via F5 `list_str_to_idx`; `convert_char_to_pinyin` bypassed (D-016). Every split validated: unknown symbols = 0 (enforced by exception).

| rep | base size | added | final size | embedding rows × dim | new embeddings | symbols used (from base) | tokens train_full / val / test_seen / test_unseen | sha256 (first 12) |
|---|---|---|---|---|---|---|---|---|
| LAT-G-asp | 2545 | 0 | 2545 | 2546 × 512 | 0 | 43 (43) | 93205 / 2741 / 9042 / 6414 | `4e173934be56` |

Added symbols per arm:

- **LAT-G-asp**: none
