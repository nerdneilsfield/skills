---
name: project-learning
description: Persist verified, durable, reusable, non-obvious knowledge discovered during real repository work into the narrowest existing project guidance or, rarely, a concise historical learning log.
---

# Project Learning

Persist knowledge only when rediscovering it later would impose real cost. The usual result is no change.

## Current project truth

Use the narrowest existing applicable `AGENTS.md` for verified, durable, reusable, non-obvious facts such as correct build or test commands, source-of-truth and generated directories, required environment variables, fixtures, repository conventions, long-lived limitations, and recurring project-specific gotchas.

Keep `AGENTS.md` short. Merge or replace stale statements instead of appending chronology. Do not create nested files for taxonomy alone, and do not duplicate information already clear from code or documentation.

## Important history

Use a learning log only for an unusual episode worth preserving: a hidden recurring failure, counterintuitive experiment, plausible routes disproved by evidence, special compiler or platform behavior, or a non-obvious compatibility or performance decision.

Prefer an existing `docs/notes/`, `docs/incidents/`, `docs/decisions/`, or equivalent location. Only when none fits, use `docs/agent-notes/`. Keep the smallest useful form:

```markdown
# <Topic>

## Finding

...

## Evidence

...

## Resolution

...
```

Do not store routine recaps, chat transcripts, reasoning dumps, command logs, current diff descriptions, or process narration. If a historical note contains a current fact every agent needs, distill one or two lines into `AGENTS.md` and link the note only when its evidence matters.

Use these boundaries:

```text
AGENTS.md = current manual
Learning log = important history
Git = implementation history
Source = implementation truth
```
