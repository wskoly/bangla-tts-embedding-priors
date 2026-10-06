# Phase 4: representation benchmark (text only, SLR37 bn_bd, 1,891 utterances)

G2P for out-of-lexicon words: `runs/g2p/v1`; BPE tokenizer: `Qwen/Qwen3-0.6B`.

| rep | chars/word | chars/utt | chars/speech-s | unique syms | % chars new emb. | % non-ASCII | % words via G2P | SLR37 type collisions | lexicon type collisions | BPE tok/word | BPE chars/tok |
|---|---|---|---|---|---|---|---|---|---|---|---|
| BN-G | 5.45 | 51.5 | 14.42 | 63 | 85.6 | 85.6 | 0.0 | 0 | 0 | 6.97 | 0.94 |
| LAT-G-det | 6.62 | 61.1 | 17.10 | 38 | 0.0 | 0.0 | 0.0 | 1 | 64 | 3.46 | 2.27 |
| LAT-G-iso | 6.40 | 59.2 | 16.60 | 41 | 1.7 | 24.2 | 0.0 | 1 | 64 | 4.64 | 1.62 |
| LAT-G-colloq | 6.61 | 60.9 | 17.06 | 24 | 0.0 | 0.0 | 0.0 | 115 | 5155 | 2.79 | 2.76 |
| LAT-uroman | 7.56 | 68.7 | 19.33 | 24 | 0.0 | 0.0 | 0.0 | 5 | 163 | 3.33 | 2.66 |
| LAT-P | 5.86 | 54.9 | 15.31 | 30 | 0.0 | 0.0 | 0.0 | 100 | 3394 | 2.85 | 2.43 |
| LAT-P-dots | 7.11 | 65.0 | 18.15 | 29 | 0.0 | 0.0 | 0.0 | 96 | — | 3.65 | 2.28 |
| IPA-P | 5.69 | 53.5 | 14.94 | 32 | 6.2 | 17.2 | 0.0 | 100 | 3394 | 3.76 | 1.80 |

Collisions = distinct Bengali word types mapping to the same string (information lost). For lexicon-based arms these are homophones by construction (e.g. nasal vowels are not transcribed).

Collision examples (lexicon):

- LAT-G-det: [['অই', 'ঐ'], ['অকস্মাত্', 'অকস্মাৎ'], ['অথই', 'অথৈ'], ['অভিজিত্', 'অভিজিৎ'], ['অর্থাত্', 'অর্থাৎ']]
- LAT-G-iso: [['অই', 'ঐ'], ['অকস্মাত্', 'অকস্মাৎ'], ['অথই', 'অথৈ'], ['অভিজিত্', 'অভিজিৎ'], ['অর্থাত্', 'অর্থাৎ']]
- LAT-G-colloq: [['অ', 'আ'], ['অই', 'আই', 'ঐ'], ['অইছে', 'আইছে'], ['অইব', 'আইব'], ['অইলে', 'আইলে']]
- LAT-uroman: [['অই', 'ঐ'], ['অকস্মাত', 'অকস্মাৎ'], ['অথই', 'অথৈ'], ['অনুচিত', 'অনুচিৎ'], ['অভিজিত', 'অভিজিৎ']]
- LAT-P: [['অংশগ্রহণের', 'অংশগ্রহনের'], ['অকস্মাত', 'অকস্মাৎ'], ['অকুল', 'অকূল'], ['অক্ষুণ্ণ', 'অক্ষুণ্ন', 'অক্ষুন্ন'], ['অগস্ট', 'অগাস্ট']]
- IPA-P: [['অংশগ্রহণের', 'অংশগ্রহনের'], ['অকস্মাত', 'অকস্মাৎ'], ['অকুল', 'অকূল'], ['অক্ষুণ্ণ', 'অক্ষুণ্ন', 'অক্ষুন্ন'], ['অগস্ট', 'অগাস্ট']]

Phenomenon totals over the corpus (canonical Bengali):

| words | conjunct_viramas | aspirate_letters | retroflex_letters | dental_letters | chandrabindu | anusvara | visarga | khanda_ta | lexicon_oov_words |
|---|---|---|---|---|---|---|---|---|---|
| 15394 | 5369 | 3470 | 3441 | 9962 | 256 | 644 | 48 | 55 | 546 |
