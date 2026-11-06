---
name: academic-writing
description: "Use when the user asks to write, revise, audit, or answer reviewers for their own academic manuscript on algorithms, hardware, circuits, FPGA, co-design, systems, SLAM, LiDAR, or autonomous driving: paper structure, claim-to-evidence, evaluation fairness, venue rules (IEEE, ACM, CVF, ISSCC, DAC, FCCM, RA-L, ICRA), LaTeX or Typst checks, cover and revision letters, in English or Chinese. Not for engineering docs (technical-writing), a de-AI-only pass (deai), a literature survey from many sources (research-report), or reading someone else's paper (qi-read-paper)."
license: MIT
compatibility: Works without tools. scripts/check_paper.py needs python3 only. Compile checks need whatever LaTeX or Typst toolchain the venue uses. Venue facts need web access to the current call.
metadata:
  author: DengQi
---

# Academic writing

Write papers whose claims are backed by evidence the reader can check. The author is accountable for every sentence, number, and citation; this skill never supplies a fact. Engineering documentation is `technical-writing`, de-AI-only editing is `deai`, a multi-source survey document is `research-report`, reading another paper is `qi-read-paper`, finding papers is `paper-search`, figures are `research-figure`.

## Determine the task

- mode: `write`, `revise`, `audit`, or `respond` (to reviewers); see [references/modes.md](references/modes.md)
- paper type, venue and year, language (English, Chinese, both), existing material
- Fill gaps with the intake rules in [references/intake.md](references/intake.md): ask once in one batch with recommended defaults; unattended, decide and record assumptions.

## Read references on demand

Always read [references/modes.md](references/modes.md) and [references/integrity.md](references/integrity.md). Then look for the author's house style: `.house-style.md` in the paper repository, or a private config the user names. If found, it overrides the defaults below, except for venue rules and integrity. [references/house-style.md](references/house-style.md) is only a public template of what such a file may hold; never write the user's rules into it.

Then read what the task needs:

- paper type and what reviewers expect: [references/paper-types.md](references/paper-types.md)
- title, abstract, introduction, contributions, related work, method, evaluation, conclusion, claim ledger: [references/sections.md](references/sections.md)
- hardware, circuit, FPGA, co-design results: [references/hardware-evaluation.md](references/hardware-evaluation.md)
- algorithm, SLAM, perception results: [references/algorithm-evaluation.md](references/algorithm-evaluation.md)
- venue, template, anonymity, page limits, policy: [references/venues.md](references/venues.md)
- LaTeX or Typst, bibliography, cross references, compile checks: [references/latex-typst.md](references/latex-typst.md)
- Chinese or English prose, cover letter, revision letter, rebuttal: [references/bilingual-and-letters.md](references/bilingual-and-letters.md)
- provenance and licences: [references/sources.md](references/sources.md)

## Workflow

1. Get venue facts from the current call, not memory ([references/venues.md](references/venues.md)). Note the URL and date. If you cannot fetch it, say so and mark the numbers unverified.
2. Build the claim ledger: each claim in the abstract and introduction maps to a table, figure, proof, or measurement, with its conditions ([references/sections.md](references/sections.md)).
3. Write or edit by section. Put the evidence level in the wording: measured, post-layout, simulated, on dataset X.
4. For LaTeX, run the checker and fix errors; review warnings by hand:

   ```sh
   python3 scripts/check_paper.py main.tex --bib refs.bib
   ```

   It finds undefined citations and references, duplicate and unused labels, unused or incomplete bib entries, placeholder text, and abstract numbers that never reappear in the body. It does not verify that a reference exists or that a result is true.
5. Compile with the venue's toolchain and check the page count by the call's rule.
6. Pass finished prose through `deai --mode check` only if it reads templated; keep numbers, citations, and math unchanged.

## Gotchas

- Page limits, anonymity rules, and AI-disclosure policies change by year and track. A remembered number is a defect.
- Never write a BibTeX entry from memory. A plausible but unverified reference is worse than a gap.
- Do not mix evidence levels in one comparison row (silicon next to post-synthesis) without labelling each.
- Power or area without voltage, frequency, scope, and corner cannot be compared. FPGA results need device, speed grade, tool version, and whether post-synthesis or post-implementation.
- Normalised metrics and FoMs hide the raw numbers. Show both, and define the formula in the paper.
- A baseline you tuned less than your method is a result about tuning. Report the budget.
- A single run or single sequence is an anecdote. Report separately: algorithm randomness (seeds, or state it is absent), measurement repeatability (repeated timing and power runs, even for a deterministic kernel), and sample coverage (several scenes or sequences, even for a deterministic SLAM).
- In a double-blind submission, self-citation in the third person, scrubbed metadata, and anonymous links are required; "omitted for review" placeholders are often barred.
- A journal extension without disclosed overlap and new content is a reuse problem.
- Do not upload unpublished manuscripts or confidential reviews to external tools beyond what the venue and data owners allow.
- If no `.house-style.md` is found, do not invent a house style.

## Final check

- Every claim in the abstract, introduction, and conclusion has evidence and matches the numbers in the tables and conditions.
- Contributions are testable and few.
- Evaluation setup is complete for the paper type (hardware or algorithm reference).
- Every citation was checked against a real source; none is invented; unverified items are listed.
- The checker reports no errors; warnings are reviewed; the PDF compiles within the page rule of the current call.
- Anonymity, disclosure, and overlap rules of the venue are met.
- Assumptions and unverified items are listed for the author.
