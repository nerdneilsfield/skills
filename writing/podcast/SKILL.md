---
name: podcast
description: "Use when the user wants collected material (papers, articles, notes, news, a book) turned into a podcast to listen to: a two or three host spoken-dialogue script, mostly in Chinese, then audio through a TTS service they configure (Xiaomi MiMo, an OpenAI-compatible speech server, or a local model). Covers episode type, spoken explanation, dialogue craft, fidelity to sources, and synthesis. Not for a written report or survey (research-report), reading one paper for the user's own notes (qi-read-paper), docs (technical-writing), or slide decks."
license: MIT
compatibility: Writing the script needs no tools; checking facts and the TTS provider's current docs needs web access. scripts/synthesize.py needs python3 only and a reachable TTS endpoint; ffmpeg is optional and needed for mp3 output and loudness normalisation.
metadata:
  author: DengQi
---

# Podcast

Turn material into a conversation a person can follow with eyes closed. The material is the only source of facts; hosts add explanation, not claims. Written reports are `research-report`, close reading for notes is `qi-read-paper`.

## Workflow

1. **Intake.** Ask once, in one batch, with a recommended default for each: material and what to leave out; episode type ([references/formats.md](references/formats.md)); target length (default 15 to 25 minutes, about 4,000 to 7,000 Chinese characters); listener level (default: smart, outside the field); language (default Chinese, English terms kept); hosts (default two, three only for a roundtable); TTS backend. Unattended: decide, then record the choices at the top of the fact ledger.
2. **Fact ledger.** Read all material. List every claim, number, name, and quote the episode may use, each with its source location and a mark: stated, inferred, or unverified. Anything outside the material must be searched for, cited in the ledger, or left out. Never invent a study, quote, or number.
3. **Outline.** Pick the shape for the type, split the length into segments with a time budget, and write for each segment the one thing the listener should be able to say afterwards. Decide where background goes (before the term first appears, not in a block).
4. **Script.** Write in the structured format in [references/script-format.md](references/script-format.md). Spoken language rules are in [references/spoken-explanation.md](references/spoken-explanation.md); character and dialogue rules in [references/dialogue.md](references/dialogue.md).
5. **Listen-through revision.** Read every line aloud in your head at speaking speed. Cut any line a listener could not parse in one hearing. Run the Gotchas check and tick each claim against the ledger. Show the user the script before spending TTS credit unless they said to go straight through.
6. **Synthesis.** Set up the backend ([references/tts-backends.md](references/tts-backends.md)), run `python3 scripts/synthesize.py script.txt --config tts.json --dry-run`, report line count and estimate, then run without `--dry-run`. Reruns only fetch changed lines.
7. **QA.** Listen to the first two minutes and one hard passage. Check the chapters file, mispronounced terms (fix by respelling in the script and rerun), clipped lines, and volume jumps between hosts. Tell the user which facts stayed uncertain.

## Fictional voices and real people

An invented insider, expert, or caller is allowed only when the script header marks the speaker `fictional` and a host says so in the first minute of audio ("the guest is an imagined practitioner, not a real person"). Never give a real named person invented words, and never clone a real person's voice without their consent. Opinions attributed to real people must be quoted from the material.

## Gotchas

- Equations, tables, code, figure references ("as shown above") and bullet lists do not exist in audio. Rewrite them as speech: what the thing does, one worked number, then the name. See spoken-explanation.md.
- Do not start with "Welcome to our podcast" followed by a topic list. Start with the thing that makes the listener care.
- Do not write "great question", "exactly!", "wow", or a host who only agrees. Real disagreement, with a reason, must appear at least once in anything over ten minutes.
- An analogy without its limit teaches something false. Say where it breaks, aloud.
- Numbers, units, abbreviations, and English terms in Chinese lines are read wrongly by TTS unless respelled. Check them against the table in spoken-explanation.md.
- Long lines (over about 150 characters) make flat delivery and are split mechanically at sentence ends; write short turns instead.
- Style tags differ per backend. The same tag text can be read aloud by a model that does not understand tags; test one line first.
- A cached line is keyed by text, voice, style, and model. Changing any of those re-bills only that line; changing the backend re-bills everything.
- API keys and base URLs go in environment variables or a config file kept out of the repository. Never paste them into the script, a commit, or a report.
- The user's TTS may have a licence that forbids commercial or public release. For private listening this rarely matters; ask before publishing.
- The Doubao and NotebookLM format details in formats.md are partly inferred from outside reports; treat them as design hints, not specifications.

## References

- [references/formats.md](references/formats.md): structure, length, roles, and pacing for each episode type
- [references/spoken-explanation.md](references/spoken-explanation.md): analogy and build-up, visual content as speech, TTS text rules
- [references/dialogue.md](references/dialogue.md): characters, interruption, disagreement, fidelity
- [references/tts-backends.md](references/tts-backends.md): MiMo API facts, OpenAI-compatible servers, local models and licences, config file
- [references/script-format.md](references/script-format.md): script syntax, a full example, synthesize.py usage
