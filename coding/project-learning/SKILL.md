---
name: project-learning
description: "Use when real work just exposed something later agents would otherwise repeat or rediscover: a verified non-obvious fact, a user correction, a repeated failure, or an agent mistake; also when the user asks to remember a lesson, run a retro on a session, or prune stale agent guidance. Puts each lesson where it will actually change behavior. Not for enabling Counterweight (counterweight-setup), routine recaps, or user-facing documentation (technical-writing)."
license: MIT
metadata:
  author: DengQi
---

# Project Learning

Turn what this work taught into a change that alters future behavior. The usual result of a small task is no file change. A lesson that nothing will ever read is not learned.

## What counts

Look for these, and verify each before keeping it:

- A user correction, or a preference stated with a reason.
- The same failure twice, or a long detour with a short explanation.
- A fact that contradicts what the code or docs suggest.
- An agent mistake: a false claim, a skipped check, or a wasted expensive call.

Do not record what the code, tests, or git history already show, or a one-off accident.

## Put it where it will fire

Use the first place that fits. A check beats a sentence, because a sentence can be ignored.

| Lesson | Place |
| --- | --- |
| Can be detected mechanically | Test, lint rule, CI, or type |
| Can be designed away | Code or API change, if in scope; otherwise propose it |
| Applies to a task type across projects | That skill's Gotchas section |
| Current fact for this repository | Narrowest applicable `AGENTS.md` or `CLAUDE.md` |
| About the user, across projects | The agent's memory, if it has one |
| Evidence that may matter later | Learning log |

Propose code, CI, and shared-skill changes unless the user asked for them. Reference the skill by its source repository, not an installed copy.

## Current project truth

Keep `AGENTS.md` for correct build or test commands, source-of-truth and generated directories, required environment variables, fixtures, conventions, long-lived limitations, recurring gotchas, and durable user decisions about dependencies, language versions, or forbidden behavior.

Keep it short, since every agent pays for it on every run. Merge or replace stale statements instead of appending chronology. If none applies and the knowledge earns persistence, create a root `AGENTS.md`. Create nested files only when narrower scope is needed.

## Important history

Normally write a learning log only for Deep work, or for a hidden recurring failure, a counterintuitive experiment, plausible routes disproved by evidence, special compiler or platform behavior, or a non-obvious compatibility or performance decision.

Prefer an existing `docs/notes/`, `docs/incidents/`, `docs/decisions/`, or equivalent. Only when none fits, use `docs/agent-notes/`. A log entry is history: date it and name the commit it was true at. When it stops being true, add a new entry rather than rewriting it.

```markdown
# <Topic>

Date and commit: ...

## Finding

## Evidence

## Resolution
```

Do not store transcripts, reasoning dumps, command logs, or diff descriptions. If a note holds a fact every agent needs, distill one or two lines into `AGENTS.md`.

```text
AGENTS.md = current manual
Learning log = important history
Git = implementation history
Source = implementation truth
```

## Retro on request

Read the session's real record, not your memory of it. List candidates by cost, each with its evidence and proposed place. Look for detours, user corrections, repeated commands, missing checks, and information the agent could not reach. Present them for choice; do not apply a batch unasked.

## Prune on request

Guidance decays. Check each instruction: does the command still run, does the path exist, is the rule enforced elsewhere now, would behavior change without it? Remove what fails, and tell the user what went. Do not expand the file during a prune.

## Gotchas

- A lesson learned from one failure is a hypothesis. Keep it narrow until it recurs, and do not turn it into a universal rule.
- A long rules file gets skimmed. Adding a rule can weaken the others, so remove one when you can.
- Verify a recalled command by running it. Stale instructions cost more than none.
- A correction applies to its context. "Don't mock here" is not "never mock".
- Never store secrets, tokens, or private data in guidance files.
