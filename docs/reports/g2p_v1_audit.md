# G2P v1 audit: 188 SLR37 out-of-lexicon word types

Method: each prediction compared with Google's transcription guide and with the lexicon's own pronunciations of related stems. Model-assisted audit, **not native-speaker verification**; items marked `needs_native_check` should get a native spot check.

| # | Category | Types | % types | Tokens | % tokens |
|---|---|---|---|---|---|
| 1 | Correct | 156 | 83.0 | 516 | 89.9 |
| 2 | Minor phonological variation | 10 | 5.3 | 21 | 3.7 |
| 3 | Genuine phoneme error | 9 | 4.8 | 13 | 2.3 |
| 4 | Stress/prosody/diacritic issue | 0 | 0.0 | 0 | 0.0 |
| 5 | Word-boundary / compound segmentation issue | 1 | 0.5 | 1 | 0.2 |
| 6 | Lexicon/G2P disagreement | 1 | 0.5 | 1 | 0.2 |
| 7 | Clearly incorrect pronunciation | 1 | 0.5 | 1 | 0.2 |
| 8 | Unhandled input (abbreviation) | 3 | 1.6 | 4 | 0.7 |
| 9 | Transcript misspelling (G2P faithful to the misspelled input) | 7 | 3.7 | 17 | 3.0 |
| | **Total** | 188 | 100 | 574 | 100 |

## Examples by category

**1. Correct:** চৌদ্দ `c o u^ d . d o` (×74); প্রতিষ্ঠান `p r o . t i sh . Th a n` (×43); ডিগ্রি `D i g . r i` (×34); ড্রিউ `D r i u^` (×32); এটি `e . T i` (×24); এন্ড `E n D` (×21); টেক্সটাইল `T e k s . T a i^ l` (×11); প্রতিষ্ঠিত `p r o . t i sh . Th i . t o` (×11)
Robust to transcript typos (also category 1): শুুক্রবার, পাাসিং, ধরেে, না্ম, ম্যা্নচেস্টার, আজকেে

**2. Minor phonological variation:**
- সুন্দরবনে (×6): G2P `sh u n . d o r . b O . n e` → `sh u n . d o r . b o . n e` — lexicon বনে = b o . n e (G2P: b O) [inherent_vowel]
- পোঁছাবে (×4): G2P `p o . ch a . b e` — nonstandard spelling of পৌঁছাবে (lexicon p o u^ . ch a . b e); G2P follows spelling; speaker reading unknown -> kept; needs_native_check [nonstandard_spelling, nasalization]
- ওয়েস্ট (×3): G2P `o . e s T` → `o^ e s T` — guide: ওয়া -> o^ a (on-glide); G2P split into two syllables [glide]
- নরওয়ের (×2): G2P `n O . r o . e r` → `n O r . o^ e r` — glide vs extra syllable [glide]
- পার্কওয়ের (×1): G2P `p a r k . o . e r` → `p a r k . o^ e r` — glide vs extra syllable [glide, compound]
- ওয়েবসাইটের (×1): G2P `o . e b . s a i^ . T e r` → `o^ e b . s a i^ . T e r` — glide vs extra syllable [glide]
- বিষয়ে (×1): G2P `b i . sh O e^ . e` → `b i . sh o . e` — lexicon বিষয় = b i . sh o e^; G2P sh O e^ . e [glide, inherent_vowel]
- ডেট্রয়েটে (×1): G2P `D e T . r O . e . T e` — Detroit: r O . e vs r O e^; acceptable [glide]
- এংগ্রি (×1): G2P `e N . g r i` — English 'angry'; spelled এ -> e; E arguably closer; kept spelling-faithful [loanword]
- কাজাখস্তানের (×1): G2P `k a . j a kh . s t a . n e r` — phones correct; syllable boundary kh . s t unusual; harmless for LAT-P (no dots) [syllabification]

**3. Genuine phoneme error:**
- পদ্মা (×4): G2P `p O d . m a` → `p O d . d a` — দ্ম assimilates to geminate dd (/pɔd.da/); lexicon has no দ্ম precedent except English রিদ্মিক [conjunct]
- ব্রাহ্মণবাড়িয়া (×2): G2P `b r a h . m o n . b a . r i . a` → `b r a m . m o n . b a . r i . a` — হ্ম -> mm (/bram.mon/); G2P copied spelling-style h m from Arabic names (আহ্মদ) [conjunct, compound, proper_name]
- টাচডাঊন (×1): G2P `T a c . D a n` — dropped u^ (rare independent ঊ); handled via spelling correction to টাচডাউন [rare_char, loanword]
- অস্ট্রেলিয়ায় (×1): G2P `O s . T r e . l i . a` → `O s . T r e . l i . a e^` — locative -য় dropped; lexicon অস্ট্রেলিয়া = O s . T r e . l i . a [suffix, glide]
- সক্রিয় (×1): G2P `s O k . r i . o` → `sh O k . r i . o` — স -> sh word-initially before k (/ʃɔkrio/); needs_native_check [sibilant]
- ইইউ (×1): G2P `i^ u` → `i . i u^` — initialism EU; G2P merged the two vowels [initialism]
- হার্ডওয়্যার (×1): G2P `h a r D . o . a r` → `h a r D . o^ E r` — must match সফটওয়্যার / ফুটওয়্যার (o^ E r); G2P o . a r [ya_phala, glide, compound]
- আশ্রয়স্থল (×1): G2P `a s . r o . s th O l` → `a sh . r o e^ . s th O l` — lost য় glide; শ্র is s/sh-inconsistent in the lexicon itself; needs_native_check [conjunct, glide, compound]
- দোলেস্বর (×1): G2P `d o . l e s . b O r` — medial স্ব -> geminate sh (ঈশ্বর = i sh . sh O r); handled via spelling correction to দোলেশ্বর [conjunct, proper_name]

**4. Stress/prosody/diacritic issue:** none (Google notation has no stress/tone marks).

**5. Word-boundary / compound segmentation issue:**
- সফটব্যাংক (×1): G2P `sh O . f o T . b E N k` → `s O f T . b E N k` — both parts in lexicon (সফট = s O f T); G2P invented a vowel (sh O . f o T) [compound, loanword]

**6. Lexicon/G2P disagreement:**
- ইয়েমেনের (×1): G2P `i . e . m e . n e r` → `i^ e . m e . n e r` — guide example ইয়েমেন = i^ e . m e n; G2P i . e [glide, proper_name]

**7. Clearly incorrect pronunciation:**
- ডাক্তারবাড়ির (×1): G2P `r a k . t a r . b a . r i r` → `D a k . t a r . b a . r i r` — initial D -> r; ডাক্তার = D a k . t a r in lexicon [compound, retroflex]

**8. Unhandled input (abbreviation):**
- মোঃ (×2): G2P `m o` — expanded to মোহাম্মদ (lexicon m o . h a m . m o d); needs ASR/listening check [abbreviation]
- লিঃ (×1): G2P `l i sh` — expanded to লিমিটেড (spelled out earlier in the same sentence) [abbreviation]
- ডঃ (×1): G2P `D O` — expanded to ডক্টর (lexicon D O k . T o r) [abbreviation]

**9. Transcript misspelling (G2P faithful to the misspelled input):**
- চট্রগ্রাম (×11): G2P `c O T . r o . g r a m` — -> চট্টগ্রাম (lexicon); 11 tokens, 1 speaker [typo, conjunct, proper_name]
- সরবারহ (×1): G2P `sh O r . b a . r O . h o` — -> সরবরাহ (lexicon) [typo]
- নিমার্ণকারী (×1): G2P `n i . m a r . n o . k a . r i` — -> নির্মাণকারী [typo]
- গুলাশানে (×1): G2P `g u . l a . sh a . n e` — -> গুলশানে [typo, proper_name]
- রিকাের (×1): G2P `r i . k a . e r` — -> রিকার (কোস্টা রিকার রাজধানী) [typo, proper_name]
- জীবনান্নদ (×1): G2P `j i . b o . n a n . n o d` — -> জীবনানন্দ [typo, proper_name]
- কলম্বিয়াের (×1): G2P `k O . l o m . b i . a . r e r` — -> কলম্বিয়ার [typo, proper_name]

## Orthographic structure of the 12 G2P errors (categories 3, 5, 6, 7)

| structure | OOV words with it (of 188) | among errors | error rate within structure |
|---|---|---|---|
| conjunct (virama) | 118 | 9 | 7.6 % |
| chandrabindu | 1 | 0 | 0.0 % |
| anusvara | 11 | 1 | 9.1 % |
| visarga | 3 | 0 | 0.0 % |
| aspirate letter | 38 | 2 | 5.3 % |
| retroflex letter | 78 | 6 | 7.7 % |
| ya-phala | 26 | 2 | 7.7 % |

Base error rate over all 188 types: 6.4 %.

Annotated phenomena among the errors: compound 5, conjunct 4, glide 4, proper_name 3, loanword 2, rare_char 1, suffix 1, sibilant 1, initialism 1, ya_phala 1, retroflex 1

## Frequency

- Top-20 most frequent OOV types (329 of 574 tokens): categories {1: 17, 9: 1, 2: 2}.
- Error types with their corpus counts: [(4, 'পদ্মা'), (2, 'ব্রাহ্মণবাড়িয়া'), (1, 'হার্ডওয়্যার'), (1, 'সফটব্যাংক'), (1, 'সক্রিয়'), (1, 'দোলেস্বর'), (1, 'ডাক্তারবাড়ির'), (1, 'টাচডাঊন'), (1, 'ইয়েমেনের'), (1, 'ইইউ'), (1, 'আশ্রয়স্থল'), (1, 'অস্ট্রেলিয়ায়')].
- Error tokens: 16 of 574 OOV tokens = 2.8 %; of all 15,394 SLR37 word tokens: 0.10 %.

