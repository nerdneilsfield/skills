---
name: project-learning
description: "Use when real work just exposed something later agents would otherwise repeat or rediscover: a verified non-obvious fact, a user correction, a repeated failure, or an agent mistake; also when the user asks to remember a lesson, run a retro on a session, or prune stale agent guidance. Chooses the user or project layer and puts each lesson where it will change behavior. Not for enabling Counterweight (counterweight-setup), routine recaps, or user-facing documentation (technical-writing)."
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

## Choose the layer first

Every agent separates two layers. Ask who the lesson is about, not where it was found.

| Layer | Holds | Test |
| --- | --- | --- |
| **User (system)** | Your preferences, toolchain, working style, and lessons about tasks in general | Still true in an unrelated repository |
| **Project** | Commands, paths, conventions, limits, and decisions of this repository | Useless or wrong elsewhere |

Then split each layer by who maintains it:

- **Instructions** are curated, always loaded, and must be followed. Put rules here.
- **Memory** is agent-written recall for background and preferences. It may be stale, may be absent, and is not enforced. Never make it the only home of a rule that must hold.

[Memory locations](references/memory-locations.md) maps these onto each tool. Use the running agent's own files, and read that reference before writing to one you have not used.

Start at project scope. Promote to user scope only when the same lesson proved true in a second project, or the user states it as a general preference; then delete the project copy. A shared project file must not hold personal paths or preferences; use the private project file or user layer. Ask before changing a user-level file, since it affects every project.

## Put it where it will fire

Within the layer, use the first place that fits. A check beats a sentence, because a sentence can be ignored.

| Lesson | Place |
| --- | --- |
| Can be detected mechanically | Test, lint rule, CI, type, or hook |
| Can be designed away | Code or API change, if in scope; otherwise propose it |
| Applies to a task type across projects | That skill's Gotchas section |
| A rule or fact for this repository | Narrowest project instructions file |
| A personal rule for every project | User instructions file |
| A preference or context worth recalling | The agent's memory, if it has one |
| Evidence that may matter later | Learning log |

Propose code, CI, and shared-skill changes unless the user asked for them. Reference the skill by its source repository, not an installed copy.

## Approve before it persists

Write at once only what the user explicitly asked to remember. Everything you inferred yourself goes to a pending list, not to live guidance, and the user approves it.

Keep the list in `pending.md` in the agent's project memory directory. Without one, use a gitignored `.agent-learnings/pending.md`. Never load it as guidance, and never list it in a memory index. Add one entry per lesson:

```markdown
- 2026-11-05 | project | AGENTS.md | `make test` skips GPU tests without CUDA_VISIBLE_DEVICES
  Evidence: failed twice in this session; see tests/README.md
```

Give the date, layer, proposed place, the lesson, and its evidence. At the end of the work, show new entries in one short batch, and ask once. On approval, write the entry to its place and remove it. On rejection, remove it. Offer to drop entries older than 90 days. Anything aimed at the user layer always waits here. Tools with their own review inbox, such as Gemini Auto Memory, keep using it.

## Project instructions

Keep `AGENTS.md` for correct build or test commands, source-of-truth and generated directories, required environment variables, fixtures, conventions, long-lived limitations, recurring gotchas, and durable user decisions about dependencies, language versions, or forbidden behavior. Use `CLAUDE.md` or `GEMINI.md` when that is what the repository already has.

Keep it short, since every agent pays for it on every run. Merge or replace stale statements instead of appending chronology. If none applies and the knowledge earns persistence, create a root `AGENTS.md`. Create nested files only when narrower scope is needed.

## Memory files

Several agents now maintain this layer themselves: they extract after a session, consolidate in the background, and generate the index. Where one does, do not fight it. Write through its own save mechanism or to topic files, never to a generated index, and put must-hold rules in instructions files instead. Do the same four jobs by hand where nothing automates them: save, consolidate duplicates, recall with verification, and forget on request.

Classify an entry as `user`, `feedback`, `project`, or `reference`. Do not save code patterns, git history, debug recipes, task state, or what instructions files already say. One fact per file, with an index of one-line pointers, where the tool allows it. Check for an existing entry and update it rather than adding a duplicate. Write absolute dates, and give the reason with the fact so a later agent can judge edge cases. Delete what proved wrong. A memory that names a file, flag, or command is a claim from the past: verify it before acting on it.

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
- A fact held in two layers drifts. Keep one home and point to it.
- Layers usually concatenate rather than override, so a conflict between user and project files may resolve arbitrarily. Remove one side.
- Never store secrets, tokens, or private data in guidance or memory files.
