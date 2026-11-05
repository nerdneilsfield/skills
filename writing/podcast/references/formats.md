# Episode types

Each type below has a structure, a length, roles, and pacing. Length is spoken time; Chinese speech runs about 4.5 to 5 characters per second (about 270 per minute) with pauses included, so 20 minutes is roughly 5,000 to 5,500 characters.

## What is known and what is inferred

- Known from reports: Doubao's podcast feature (launched mid-2025) takes a document or web link, or a topic with search, and produces a two-person conversation with backchannel sounds and pauses; early testers saw occasional clipped sentences and could not always choose voices ([IT之家](https://www.ithome.com/0/861/447.htm), [Pedaily](https://news.pedaily.cn/20250521/107583.shtml), [ifanr](https://www.ifanr.com/1627538)). Its developer API is described by third parties as a WebSocket podcast endpoint with a topic mode and a link or file mode; check Volcengine's own docs before relying on that.
- Known from Google and press: NotebookLM Audio Overview offers Deep Dive (two hosts, default), Brief (short), Critique, and Debate; Deep Dive, Critique, and Debate have length choices, some English only ([TechRadar](https://www.techradar.com/ai-platforms-assistants/gemini/google-notebooklms-ai-podcast-hosts-can-now-get-into-an-argument-over-your-notes), [Android Authority](https://www.androidauthority.com/notebooklm-new-audio-overview-formats-3593717)). Third-party guides disagree on lengths. Google has not published the script prompt, so statements about how it writes analogies are inference.
- Known from press: The Daily runs about 20 minutes, one story per episode, host introduces, then interviews the reporter, with archival audio and a short close ([Poynter](https://www.poynter.org/?p=456753)). Treat the section timings below as patterns, not as any show's rules.
- Everything labelled "pattern" is the author's synthesis of common practice, to be tuned by listening.

## Deep paper or algorithm discussion

Roles: **Guide** (knows the paper, explains, owns the facts), **Stand-in** (smart outsider, asks what the listener would ask, restates in own words), optional **Skeptic** (probes evidence, limits, comparison fairness).

Length: 20 to 35 minutes; one paper per episode. Under 15 minutes cannot carry both background and mechanism.

Structure (pattern):
1. Hook, 1 to 2 min: the problem as a concrete situation, with the surprising result held back until segment 4 or hinted.
2. Background, 3 to 5 min: only what is needed to understand this paper. Explain each field term when it first matters, via the stand-in's honest confusion. Say what people did before and exactly where that failed.
3. The idea in one sentence, then in one worked example with small numbers.
4. Mechanism, 6 to 10 min: walk the algorithm in order, as a story of what happens to one input. Name the steps ("first it does X, then Y"). Equations become speech (see spoken-explanation.md). Include the real details: sizes, loss terms in words, training data, what is frozen, what is expensive.
5. Evidence, 3 to 5 min: what was compared, on what, by how much; say which numbers come from the paper and which comparison is not apples to apples.
6. Limits and disagreement, 2 to 4 min: what the authors admit, what they skip, who might disagree.
7. Close, under 1 min: what a listener could now say or try; one open question. No recap of every point.

Pacing: one new concept per 60 to 90 seconds at most; after a dense passage, a short restatement by the stand-in; alternate long guide turns (up to 25 seconds, about 120 characters) with short ones.

## News with analysis

Pattern, from the anchor-then-interview shape of daily news shows: a brief anchor section, deep analysis, then an interview.
1. Anchor brief, 1.5 to 3 min, one voice carries most of it: what happened, when, who, the numbers, plainly, no opinion. Every fact dated and sourced ("according to the filing dated ...").
2. Analysis, 8 to 12 min, two hosts: why it happened, who gains and loses, how it compares with earlier cases, what the numbers mean in everyday scale.
3. Interview, 5 to 8 min: a host questions an insider-style guest. The guest is a **fictional composite** unless a real, quotable person is in the material; the script header marks it and the audio says so in the first minute. The guest may only voice analysis grounded in the ledger and must flag guesses ("this is my reading, the source does not say").
4. Close, 1 min: what to watch next, with the dates known.

Length 15 to 25 min. Facts that are unconfirmed are said aloud as unconfirmed.

## Explainer

One concept, 8 to 15 min. Structure: a puzzle or misconception, the simplest correct model, two examples of increasing difficulty, where the simple model fails, the better model. Roles: Explainer and Stand-in only. Pacing: build, then test understanding by letting the stand-in predict an outcome before the answer.

## Interview

Host and guest (real person only if the material is their own words; otherwise fictional and labelled). 15 to 30 min. Open with a concrete story from the guest, not a biography. Questions follow the answer just given; prepared questions are a backup list. Include one challenge and one "what would change your mind".

## Roundtable

Three hosts with distinct positions (for example Builder, Skeptic, Generalist) on one question. 20 to 30 min. Open with the question, each gives a position in under a minute, then spend most time on two real points of conflict; end with where they still disagree, not a forced consensus. Avoid round-robin turns; let one voice answer another.

## Book or long-article digest

Material is long, so choose: 3 to 5 ideas, not the table of contents. 20 to 30 min. Open with why the author wrote it and the central claim, one segment per chosen idea (claim, one example from the text, the hosts' test of it), a segment on what the book gets wrong or leaves out, a close on what is worth reading in full. Say what was left out. Quotes only if verbatim from the material, and short.

## Multi-source topic roundup

If the user collects many items on one theme: group by question, not by source. Give each source one sentence of identity ("a 2024 survey of ...") the first time it appears. Mark where sources disagree.
