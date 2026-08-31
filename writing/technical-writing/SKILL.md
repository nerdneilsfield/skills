---
name: technical-writing
description: Write, rewrite, and review software, hardware, and engineering documentation. Use for READMEs, tutorials, how-to guides, concepts, references, API/CLI documentation, troubleshooting, deployment guides, design/interface specifications, hardware references, user manuals, and test/verification documents in Chinese, English, or mixed-language text. Do not use for academic papers or scholarly manuscripts.
---

# Technical writing

Put technical correctness first. Then make the document precise, unambiguous, complete, consistent, scannable, and useful for the reader's task.

## Determine the task

Infer the following from the request and source material. If the user specifies a value, use it without reconfirming:

- mode: `write`, `rewrite`, or `review`
- document type: see [references/structure-document-types.md](references/structure-document-types.md)
- language: Chinese, English, or mixed
- audience, reader goal, operating environment, and known constraints

Ask only when missing information would materially change technical content or a safety conclusion. Otherwise, make the fewest conservative assumptions and mark unresolved facts for confirmation.

## Read references on demand

Always read:

- [references/principles.md](references/principles.md)
- [references/clarity-terminology.md](references/clarity-terminology.md)
- [references/structure-document-types.md](references/structure-document-types.md)

Then read only what the task needs:

- Chinese, English, or mixed-language prose: [references/language.md](references/language.md)
- tutorial, quick start, how-to, troubleshooting, deployment, user manual, or test-verification: [references/procedures.md](references/procedures.md)
- reference, API, CLI, interface, or hardware reference: [references/reference-writing.md](references/reference-writing.md) and [references/code-numbers-units.md](references/code-numbers-units.md)
- human, equipment, data, security, or environmental risk: [references/warnings-safety.md](references/warnings-safety.md)
- `review` mode: [references/review.md](references/review.md)

Use a matching file from [templates](templates/) only when creating a document whose structure is stable enough to benefit from one. Delete inapplicable sections. Never fill a placeholder with an invented fact.

## Plan language before drafting; use deai afterward

For `write` and `rewrite`, define a short language contract from this skill's [language rules](references/language.md) before drafting. Do not rely on post-editing to repair the prose. Record:

- target language, locale, tone, and reader expertise;
- preferred terms, abbreviations, proper names, and protected spans;
- actor, action, conditions, sequence, and grammatical backbone;
- repetitive sentence patterns, formulaic openings/endings, empty connectors, nominalization stacks, and unsupported claims to avoid;
- structures required by the document type, such as parallel actions in a procedure or repeated field order in a reference.

Draft against that contract. Only after the final draft exists, invoke `$deai --mode check`. Let it detect the language, or pass `--lang zh|en|mixed` and `--profile generic`. Act only on meaningful findings. If a rewrite is needed, change flagged prose only; do not optimize mechanically for a detector score.

Technical correctness, formal grammar, stable terminology, semantic parallelism, and protected spans override de-AI variation. Do not break procedures, parameter tables, register tables, test criteria, or other meaningful repetition merely to vary sentence structure. After the de-AI pass, recheck immutable facts and grammar. If the rules conflict, keep the technically correct, grammatically unambiguous version.

## Mode: write

1. Identify what the reader must accomplish, find, or understand. Choose the closest document type. A README can combine overview, quick start, configuration, and reference content; do not force it into one information type.
2. Gather verifiable interfaces, parameters, versions, units, ranges, defaults, prerequisites, timing, results, and safety constraints. Mark missing facts for confirmation instead of guessing.
3. Organize content for the document type. Put information needed for action or judgment before background and implementation detail.
4. Cross-check prose, examples, commands, diagrams, and tables. Ensure that procedures are executable and results are verifiable.

## Mode: rewrite

Create an immutable-facts list before editing. Do not silently change:

- APIs, CLIs, protocols, registers, signals, paths, or code identifiers;
- parameter names, types, values, units, ranges, defaults, return values, or error conditions;
- step order, dependencies, prerequisites, expected results, or pass/fail criteria;
- safety levels, hazards, consequences, avoidance instructions, or any other technical meaning.

If the source is contradictory, incomplete, or apparently wrong, preserve the factual boundary and report the issue. Do not hide uncertainty behind fluent prose. Do not add features, constraints, or conclusions unless the user asks.

## Mode: review

Report only issues that affect correct use, reproducibility, comprehension, or consistency. Give a correction direction; do not rewrite the full document by default. Use `Critical`, `Major`, and `Minor` as defined in [references/review.md](references/review.md). If no reportable issue exists, say so. Do not invent findings to fill a quota.

## Final check

- Technical facts and examples agree; unknown information is not presented as fact.
- The de-AI pass did not alter protected spans, technical facts, normative force, or meaningful parallel structure.
- Actors, actions, conditions, sequence, and results are explicit.
- Every prose sentence has a recognizable grammatical backbone; modifier, reference, coordination, negation, and condition scope is unambiguous.
- Parameters, units, ranges, defaults, limits, and version boundaries are sufficient for use or implementation.
- Terminology, capitalization, formatting, and mixed-language text are consistent.
- Headings, lists, tables, and references are scannable; procedures are executable and verifiable.
- Risk information precedes the hazardous action and states the hazard, consequence, and avoidance method.
