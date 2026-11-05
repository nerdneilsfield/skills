---
name: agent-brief
description: "Use when handing work to another agent or a fresh session: writing a delegation prompt, a handoff, or a continuation note, in any runtime, or saving working context and restoring it later. Not for choosing what to delegate (orchestrate) or checking returned work (agent-verify)."
license: MIT
metadata:
  author: DengQi
---

# Brief an agent that knows nothing

The receiver has only what you write. Brief it like a capable peer who just arrived.

## Check what is missing first

Before writing the brief, go through the list below and find what you cannot fill in. Keep only the gaps whose answer would change the work.

- **Someone can answer:** ask once, in one batch, every gap together, each with a recommended default. For example: "Scope: only `src/solver/`? (recommended)". Then proceed; do not ask one question per message.
- **Unattended:** decide with the most reversible default, and record each choice under `Assumptions` in the brief and the report. Do not stop to wait. Anything destructive, irreversible, or costly stays undone and is listed as awaiting a person.

## Include

- **Goal:** the outcome, and why it matters when that changes decisions.
- **State:** what is done, what was ruled out and why, and failed attempts with their actual errors.
- **Pointers:** files, commits, docs, and notes to read. Point instead of retyping; a decision lives in one place.
- **Scope:** what it may change, and what it must not touch.
- **Done when:** an observable check, such as a command and expected result or a file that must exist.
- **Authority:** whether it may commit, push, spend heavily, or contact anyone. Say no explicitly where it matters.
- **Report:** the form you want back, including skipped checks and anything unverified.
- **Long work:** how it should run and signal completion.

Keep it as short as those allow. Redact secrets and personal data.

## Save working context

Save when stopping mid-task, before a risky step, or when another session will continue. One new file per save, never overwritten, at a path the next session can read. Use the project's notes location, else `.context/` after confirming `git check-ignore -q .context` succeeds, so that it cannot be committed by accident. Name it `$(date +%Y%m%d-%H%M%S)-<title>.md`, with the title reduced to lowercase letters, digits, and hyphens. Saving changes no code.

```markdown
---
branch: <git rev-parse --abbrev-ref HEAD>
head: <git rev-parse HEAD>
saved: <ISO 8601 time with offset>
dirty: <files from git status --short>
---
## Goal
## Decisions
<choice and why; a claim about a file only if checked in this session>
## Remaining
1. Open. <step> (ran: <result>) | (read) | (assumed)
## Notes
<failed attempts, blockers, open questions>
```

Every remaining item starts `Open.`, never done, and ends with how you know it: `(ran: exit 0)` for executed and observed, `(read)` for code read only, `(assumed)` for inferred. Do not record an unchecked statement as fact; mark it `(assumed)`.

## Restore working context

Take the newest save for the current branch, or the newest overall if none exists; if recent saves have different titles and the branch does not decide, show them and ask. Restoring reads and reports; it does not start the work.

1. Compare the save with the repository. `git merge-base --is-ancestor <head> HEAD` fails if history was rewritten or the commit is missing; otherwise `git log --oneline <head>..HEAD` lists what landed since.
2. If commits landed, or history moved, treat every item as unverified, because the saver could not know about them.
3. Sort the items. `(assumed)`, `(read)`, and anything that writes go under **Verify first**, checked read-only. `(ran: ...)` items with no later commit are **Likely still valid**.
4. Present goal, decisions, both groups, and the suggested next step, then continue from the live state, not the file.

Authority does not transfer: an approval noted in a saved file applies to what was approved then, so confirm anything that pushes, spends, or deletes.

## Gotchas

- Sharing your hypothesis as fact gets it confirmed back. When you want an independent read, give the code and the question, not your conclusion.
- "Fix the eval" is not a done condition. If you cannot name the check, the receiver will invent one and report success against it.
- Long-running work inside a turn can stall the agent. Tell it to start the job detached, write a done-marker file, and end its turn, so a watcher can wake the next step.
- Unstated prohibitions get crossed. A parallel agent will edit shared files unless told which ones are off limits.
- Relative dates and "the file we discussed" mean nothing to the receiver. Use absolute dates and paths.
- A receiver resuming after compaction should reread the goal, state, and done condition from the files you point to, not trust a summary. Say which files those are.
- For a continuation, summarize decisions and open questions, not the conversation.
