---
name: spec
description: "Use when the user asks to turn a discussion into a specification, a plan of record, or a set of tickets for later sessions or for another agent: synthesize what was already said into goal, constraints, out-of-scope, and checkable acceptance, then optionally split it into tickets. Writes local files. Not for interviewing the user about unresolved choices (grill-me) or for implementing the work."
license: MIT
metadata:
  author: DengQi
disable-model-invocation: true
---

# Write the spec from what is already known

This skill synthesizes; it does not interview. If the conversation has not settled a decision, that is a question for `grill-me`, not something to invent here.

Use it only for work that crosses a session or goes to another agent. Work you will finish in this session does not need a spec file.

## 1. Gather before writing

Read the conversation, the relevant code, and any existing spec or issue it builds on. Use the project's own vocabulary. A spec that renames things the code already names differently will be ignored.

## 2. Write these sections

```markdown
# <Feature>

## Goal
What becomes possible, and for whom. One paragraph.

## Constraints
What cannot change: interfaces, dependencies, performance limits, compatibility.

## Out of scope
What this deliberately does not do. Be specific; this section prevents scope creep.

## Acceptance
Each item a check someone else can run: a command and its expected result, or a
file and the condition on it. No item that only you can judge.

## Decisions
Choices already made, each with its reason. Include the alternatives rejected.

## Open questions
What is still undecided, and who decides. Not a place to guess.
```

Acceptance is the part that earns the file. "Works correctly" is not acceptance; "`pytest tests/test_x.py` passes and `x --json` prints one record per input line" is.

## 3. Where to put it

Prefer the repository's existing home: `docs/specs/`, `docs/decisions/`, or the issue tracker. Otherwise use `.scratch/<feature-slug>/spec.md`. Do not invent a new documentation system, and do not put a spec where the repository keeps generated files.

## 4. Split into tickets only if asked

Tickets are tracer-bullet slices: each cuts a narrow but complete path through every layer, is verifiable on its own, and fits one fresh session. Give each ticket its blocking edges, and publish blockers first.

```markdown
# <NN>: <title>

**What to build:** the end-to-end behaviour this makes work.

**Blocked by:** the tickets that gate this one, or "None (can start immediately)".

- [ ] Acceptance criterion
- [ ] Acceptance criterion
```

One file per ticket under `.scratch/<feature-slug>/issues/<NN>-<slug>.md`, numbered in dependency order. Present the breakdown for approval before writing the files.

## Gotchas

- Do not interview. If a decision is missing, list it under open questions and stop; do not fill it with a plausible default.
- Do not put file paths or code snippets in the spec. They go stale within a week. A type shape or a state machine that encodes a decision is the exception, and it should be trimmed to the decision.
- An acceptance item only the author can evaluate is not acceptance. Rewrite it as a command or a condition.
- "Out of scope" is the section that prevents the next session from expanding the work. Leave it empty and the work grows.
- A spec written for a task you will finish now is overhead. Say so and skip the file.
- Tickets that are horizontal layers cannot be verified alone. Cut vertically instead.
- The spec is not the plan of record until the user approves it. Show it first.
- Do not close or rewrite a parent issue while deriving tickets from it.

## Report

State where the spec was written, the acceptance items, the open questions left for the user, and whether tickets were produced.
