# Script format and synthesize.py

## Syntax

A plain text file. Blank lines and lines starting with `//` are ignored.

```
---
title: 为什么向量检索不会精确
language: zh
speaker.A: 林岚 | Guide
speaker.B: 周远 | Stand-in
speaker.C: 老K | Skeptic | fictional
sources: ledger.md
---
# 开场
A [calm] {0.4}: 一句话：你问一百万篇文章里哪一篇最像这句话，它给你的是一个很接近的答案，而不是唯一的答案。
B [curious]: 接近？那接近和对有什么区别？
// 这里插入一段话
```

- Header between two `---` lines: `key: value`. `speaker.<id>: name | role [| fictional]` declares a host; ids are ASCII (`A`, `host1`). Mark invented people `fictional`.
- `# Title` starts a chapter; each becomes an entry in the chapters file with its start time.
- A line is `id [style] {pause}: text`. `[style]` and `{pause}` are optional. `style` is free text (an emotion or manner such as `curious`, `压低声音`, `slower`); how it reaches the model depends on `style_mode`. `{0.4}` or `{0.4s}` is seconds of silence after the line; the default is `default_pause` (0.35).
- One line per speaking turn. Keep each under about 150 characters; longer lines are split at sentence ends (then clause ends) and the pieces get a short `split_pause` between them.
- Write the text exactly as it should be spoken (numbers and terms respelled, see spoken-explanation.md). Do not put markdown or stage directions in text.
- A fictional speaker needs a spoken disclosure in the first 8 lines; the tool warns when it finds none (looks for 虚构, fictional, imaginary, 假想, 杜撰).

## synthesize.py

```
python3 scripts/synthesize.py script.txt --config tts.json --dry-run
python3 scripts/synthesize.py script.txt --config tts.json --out episode.mp3 --normalize
```

- `--dry-run` parses, lints, and prints line count, request count (after splitting), characters, cached versus to-call, a rough speaking time, and a cost estimate if `price_per_1k_chars` is set. No network, no key, no base URL needed.
- Each request is cached under `<out dir>/.tts-cache/` by a hash of backend, normalised base URL (never the key), model, voice, voice instruction, style, speed (OpenAI-style only), style mode, format, and text. `max_chars` must be a positive integer. Rerunning after an edit calls only changed lines.
- Retries: up to `retries` (default 4) with exponential backoff from `backoff` seconds (default 1) on timeouts, connection errors, 408, 429, and 5xx. Other 4xx errors fail at once.
- If any line fails, nothing is written; the tool lists each failed line number, speaker, and error, keeps the successful cache, and exits 1. Fix the cause (key, voice name, base URL) and rerun.
- Output: `.mp3` or `.wav` plus `<name>.chapters.txt` (`HH:MM:SS Title`). Without ffmpeg only wav-to-wav joining works (mono 16-bit at `sample_rate`, default 24000); with ffmpeg any clip format is decoded, `--normalize` applies a loudnorm filter (I=-16 LUFS) and keeps the source sample rate, and mp3 is encoded with libmp3lame.
- Exit codes: 0 done, 1 some lines failed, 2 configuration or script error.
- Tests: `python3 -m unittest tests.test_podcast` runs against a local fake server; no paid service is called.

## Full short example

```
---
title: 试讲
speaker.A: 林岚 | Guide
speaker.B: 周远 | Stand-in
---
# 开场
B: 我先说我的困惑：这个方法为什么需要两个网络？
A [calm]: 先看只有一个网络会怎样。它既要出题，又要判卷，所以它总能让自己满分。
B [skeptical] {0.5}: 听起来像自己给自己打分。
A: 就是这个意思。不过这个比方有个漏洞：判卷的网络也在学，所以不是一成不变的标准。
```
