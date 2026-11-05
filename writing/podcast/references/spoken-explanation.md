# Spoken explanation and TTS text

A listener cannot scroll back, see a symbol, or skim. Every sentence must be understood on first hearing.

## Explaining an abstract idea

Order that works (pattern, used in good explainer audio; tune by listening):
1. **Need.** Give the situation where the idea becomes necessary. "You have a million documents and one second."
2. **Concrete example first.** Small numbers, a named object. "Three words: cat, dog, car."
3. **Build up.** Add one piece per step, naming the step ("so far we only have X; now Y").
4. **Analogy.** One, from the listener's world, mapped part by part: "the index is the library catalogue; the vectors are the shelf positions".
5. **Say where the analogy breaks.** Aloud and specifically: "a catalogue gives one exact place; here two items can be close but never identical, so it's closer to a map than a catalogue".
6. **Contrast.** What it is not, or what the older method did on the same example.
7. **Restate** in different words, ideally by the stand-in, then confirmed or corrected.

Rules: one analogy per idea; do not stack three in a row. Do not reuse the same analogy for the next idea unless it genuinely fits. Define a term at the moment of first need, after the example, not before.

## No visual-only content

- **Equation.** Say what it computes and why, then read the shape: "take the score of each candidate, divide by the sum of all the scores, so they add up to one" instead of reading symbols. Give one worked number. Name the equation only if the listener may look it up.
- **Table.** Pick the two or three comparisons that matter, state them as sentences with the unit, give the direction ("about three times faster, 41 seconds against 12"). Never read a full table.
- **Code.** Describe the steps and the one surprising line; no code syntax read aloud.
- **Figure.** Describe what it shows and the conclusion; never "as you can see". If a figure is essential, say it is in the show notes.
- **List.** Use "three things: first ..., second ..., third ...", and keep to three.
- **Parenthetical and footnote.** Move into its own sentence or cut.

## Numbers, units, abbreviations (for TTS)

| Written | Write in the script | Why |
| --- | --- | --- |
| 3.14 | 三点一四 | decimals read as dates or ranges otherwise |
| 2024年 | 二零二四年 | years read digit by digit |
| 12% | 百分之十二 | symbol may be dropped |
| 1,200,000 | 一百二十万 | spoken scale is natural |
| 3-5 | 三到五 | hyphen may be read as minus or silent |
| 5×10^-3 | 千分之五 | exponent rarely read right |
| km/h, GB | 公里每小时, 千兆字节 or "G B" | units need spoken forms |
| ms | 毫秒 | |
| 1:30 | 一比三十 or 一点三十 (decide which) | ratio versus time |

Keep large exact numbers rare; round and say "about" when the source allows, but keep the exact number in the ledger.

English terms in Chinese speech: use the English term once with a Chinese gloss at first use ("注意力机制，也就是 attention"), then pick one form and stay with it. Acronyms: first time spell by letters if TTS reads them as words ("G P U"), or give the Chinese name. Names of papers and models: say the short form. For tools that mispronounce a term, respell it in the script (for example write "派森" for Python if a voice mangles it) and keep a per-project respelling list; this changes the audio only.

Polyphones: if a character is read wrongly (行 xíng/háng, 重 zhòng/chóng, 长 cháng/zhǎng, 乐, 还, 得, 着, 为), rewrite to an unambiguous phrase or substitute a homophone for the audio script. Some engines accept pinyin markup (CosyVoice 3 documents Pinyin and CMU-phoneme inpainting; IndexTTS also lists pinyin control) but a plain rewrite works everywhere. Keep the ledger copy with the proper characters.

Punctuation drives pacing: a full stop gives a longer stop than a comma; an ellipsis gives a trailing pause; avoid emoji, markdown symbols, and brackets in spoken text (brackets in the style field are fine; MiMo reads `(tag)` at line start as a style tag, see tts-backends.md).

## Sentence length

Aim for 8 to 25 characters per clause, one idea per sentence, subject early. Spoken Chinese uses shorter sentences and more connecting words than writing ("所以", "不过", "换句话说"), but do not pad. Avoid noun stacks and "对...进行...的..." forms. Repeat key nouns instead of pronouns when a listener could lose the referent.
