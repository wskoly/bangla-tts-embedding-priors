# G2P v1 (character transformer on the Google bn lexicon)

Split (words): train 58462, dev 3248, test 3248; seed 20261006; model {'d': 256, 'heads': 4, 'layers': 3, 'ff': 1024, 'dropout': 0.1}; best dev epoch 60; device cuda.

| set | words | WER % | WER (ignore syllable dots) % | PER % |
|---|---|---|---|---|
| test | 3248 | 17.76 | 16.69 | 3.37 |

Dev curve:

| epoch | train loss | dev WER | dev WER_nodot | dev PER |
|---|---|---|---|---|
| 5 | 1.054 | 60.53 | 60.07 | 22.40 |
| 10 | 0.878 | 32.24 | 31.40 | 8.62 |
| 15 | 0.819 | 26.14 | 25.25 | 5.80 |
| 20 | 0.787 | 22.14 | 21.21 | 4.43 |
| 25 | 0.769 | 20.44 | 19.58 | 4.00 |
| 30 | 0.758 | 19.58 | 18.72 | 3.78 |
| 35 | 0.751 | 18.97 | 18.07 | 3.55 |
| 40 | 0.741 | 17.73 | 16.78 | 3.23 |
| 45 | 0.731 | 17.24 | 16.19 | 3.19 |
| 50 | 0.726 | 17.00 | 16.10 | 3.09 |
| 55 | 0.723 | 17.06 | 16.13 | 3.08 |
| 60 | 0.722 | 16.81 | 15.89 | 3.06 |

SLR37 out-of-lexicon words: 188 types / 574 tokens; predictions in `data/derived/g2p/slr37_oov_g2p_v1.tsv` (column `verified_google` for human review).

Sample test errors (word | reference | prediction):

- domain | `D o . m e i^ n` | `D o . m a i^ n`
- অভিনন্দনও | `O . bh i . n O n . d o . n o` | `o . bh i . n O n . d o n . o`
- সন্ধের | `sh o n . dh e r` | `sh O n . dh e r`
- জনসম্মুখে | `j O . n o . s O m . m u . kh e` | `j O . n o . sh o m . m u . kh e`
- pabna | `p a b . n a` | `p E b . n a`
- প্রজন্মও | `p r o . j O n . m o o^` | `p r o . j O n . m o . o`
- motamot | `m O . t a . m O t` | `m o . T a . m O T`
- হাসনাত | `h a s . n a t` | `h a sh . n a t`
- টেগোর | `T E . g o r` | `T e . g o r`
- ডাকসাইটে | `D a k . sh a i^ . T e` | `D a k . s a i^ . T e`
- legends | `l i . j e n D s` | `l e . j e n D s`
- সরাসরি | `sh O . r a . s o . r i` | `sh O . r a . sh o . r i`
- জীবনেই | `j i . b O . n e i^` | `j i . b o . n e i^`
- তারকাই | `t a . r o . k a . i` | `t a . r o . k a i^`
- নামটাও | `n a m . T a . o` | `n a m . T a o^`
- কাউন্সিলররাও | `k a . u n . s i . l a r . r a . o` | `k a . u n . s i . l O r . r a o^`
- যৌনকর্মে | `j o o^ . n o . k O r . m e` | `j o u^ . n o . k O r . m e`
- iucn | `a i^ . i u^ . s i . e n` | `a i^ . s i . i^ u . e n`
- বস্তুকে | `b o sh . t u . k e` | `b o s . t u . k e`
- সহস্রাব্দের | `sh O . h o . s r a b . d e r` | `sh O . h o s . r a b . d e r`
- মোস্তফাকে | `m o sh . t o . f a . k e` | `m o s . t o . f a . k e`
- মহব্বতের | `m O . h o b . b O . t e r` | `m O . h o b . b o . t e r`
- ফর্দ | `f O r . d o` | `f O r d`
- উইন্ডিশ্চ | `u^ i n . D i sh c` | `u^ i n . D i sh . c o`
- original | `o . r i . j i . n a l` | `O . r i . j i . n a l`
- উইন্ডিশ্চের | `u^ i n D . i sh . c e r` | `u^ i n . D i sh . c e r`
- broken | `b r o . k e n` | `b r a . k e n`
- নকআউট | `n O k . a u^ T` | `n O k . a . u T`
- বৌদ্ধবিহারে | `b o o^ d . dh o . b i . h a . r e` | `b o u^ d . dh o . b i . h a . r e`
- spy | `s p a i^` | `e s . p i . a i^`
- এমনিই | `e m . n i i^` | `e m . n i . i`
- wait | `o . e T` | `o . a i^ T`
- caught | `k O T` | `k a g T`
- শবনমের | `sh O b . n o . m e r` | `sh O b . n O . m e r`
- honduras | `h o n . D u . r a s` | `h O n . d u . r a s`
- কটিই | `k O . T i . i^` | `k o . T i . i`
- অতিপ্রাকৃতিক | `o . t i . p r a . k r i . t i k` | `o . t i . p r a k . r i . t i k`
- যুক্তরাষ্ট্র | `j u k . t o . r a s . T r o` | `j u k . t o . r a sh . T r o`
- নম্বরই | `n O m . b o . r i` | `n O m . b o r . i`
- regia | `r e . j i . a` | `r i . j i . a`
