---
name: agent-brief
description: "Use when handing work to another agent or a fresh session: writing a delegation prompt, a handoff, or a continuation note, in any runtime. Not for choosing what to delegate (orchestrate) or checking returned work (agent-verify)."
license: MIT
metadata:
  author: DengQi
---

# Brief an agent that knows nothing

The receiver has only what you write. Brief it like a capable peer who just arrived.

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

## Gotchas

- Sharing your hypothesis as fact gets it confirmed back. When you want an independent read, give the code and the question, not your conclusion.
- "Fix the eval" is not a done condition. If you cannot name the check, the receiver will invent one and report success against it.
- Long-running work inside a turn can stall the agent. Tell it to start the job detached, write a done-marker file, and end its turn, so a watcher can wake the next step.
- Unstated prohibitions get crossed. A parallel agent will edit shared files unless told which ones are off limits.
- Relative dates and "the file we discussed" mean nothing to the receiver. Use absolute dates and paths.
- For a continuation, summarize decisions and open questions, not the conversation.
