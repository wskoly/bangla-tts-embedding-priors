# F5 vocabularies v1 (per representation)

Tokenization: one token per code point via F5 `list_str_to_idx`; `convert_char_to_pinyin` bypassed (D-016). Every split validated: unknown symbols = 0 (enforced by exception).

| rep | base size | added | final size | embedding rows × dim | new embeddings | symbols used (from base) | tokens train_full / val / test_seen / test_unseen | sha256 (first 12) |
|---|---|---|---|---|---|---|---|---|
| LAT-P-rand2 | 2545 | 0 | 2545 | 2546 × 512 | 0 | 30 (30) | 86846 / 2586 / 8401 / 5969 | `4e173934be56` |
| LAT-P-rand3 | 2545 | 0 | 2545 | 2546 × 512 | 0 | 30 (30) | 86846 / 2586 / 8401 / 5969 | `4e173934be56` |

Added symbols per arm:

- **LAT-P-rand2**: none
- **LAT-P-rand3**: none
