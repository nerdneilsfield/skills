---
name: project-learning
description: Persist verified, durable, reusable, non-obvious knowledge discovered during real repository work into the narrowest existing project guidance or, rarely, a concise historical learning log.
---

# Project Learning

Persist knowledge only when rediscovering it later would impose real cost. The usual result is no change.

## Current project truth

Use the narrowest existing applicable `AGENTS.md` for verified, durable, reusable, non-obvious facts such as correct build or test commands, source-of-truth and generated directories, required environment variables, fixtures, repository conventions, long-lived limitations, recurring project-specific gotchas, and durable project-level user decisions about dependencies, language versions, or forbidden speculative behavior.

Keep `AGENTS.md` short. Merge or replace stale statements instead of appending chronology. If no applicable `AGENTS.md` exists and the knowledge clearly earns persistence, create a root `AGENTS.md`. Do not create nested files unless narrower scope is actually needed, and do not duplicate information already clear from code or documentation.

## Important history

Normally consider a learning log only for Deep work. Direct or Managed work should create one only for an exceptional finding whose historical evidence is likely to matter later: a hidden recurring failure, counterintuitive experiment, plausible routes disproved by evidence, special compiler or platform behavior, or a non-obvious compatibility or performance decision.

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
