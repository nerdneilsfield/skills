---
name: orchestrate
description: "Run when the user explicitly starts multi-agent coordination of a long or parallel goal: decide what to delegate, split the work, track task state, and integrate results. Independent of the agent runtime. Not for a task one agent can finish, and not for runtime commands, which belong to that runtime's own skill."
license: MIT
compatibility: Needs an agent runtime that can start other agents, such as Paseo, Orca, or built-in subagents.
metadata:
  author: DengQi
disable-model-invocation: true
---

# Orchestrate agents toward one goal

You own the goal and its outcome. Agents do parts of it; responsibility does not move with the work. This skill defines intent and evidence only. For how to start, message, or stop an agent, use the skill of the runtime in use, and do not guess its interface.

## Decide whether to delegate

Delegate when work is independent and can run in parallel, is a side quest that should not block the user, or would flood your context with file contents. Do it yourself when it is a few tool calls, when your next step depends on it immediately, or when you cannot yet describe it clearly. If you cannot write the brief, you do not understand the task well enough to hand it off.

Each agent costs tokens and review attention. Use the fewest that fit.

## Run the goal

1. State the goal and how it will be checked, and confirm with the user if the goal is ambiguous.
2. Split it into tasks that each fit one fresh session. Note which tasks block which. Do prefactoring first.
3. Give each task an owner and a brief through `agent-brief`. Parallel tasks must not write the same files. Use separate worktrees or an explicit file boundary.
4. Keep the status table below in one file, so the goal survives compaction and a new session.
5. Wait for notifications instead of polling. Stay available to the user.
6. Accept each result through `agent-verify` before anything builds on it.
7. Merge accepted work through the controller below. Then run the whole-goal check yourself and report.

## Task status protocol

Keep one row per task, with one owner at a time. Check the table before starting anyone, so no two agents claim the same work.

| Field | Meaning |
| --- | --- |
| Task, owner | What, and which single agent holds it |
| Inputs | Paths or commits it depends on |
| Done when | The observable check from the brief |
| State | `queued`, `running`, `blocked`, `reported`, `accepted`, `merged`, `abandoned` |
| Blocked on | The task or the user decision it needs |
| Attempts | Count against the limit below |

Only `agent-verify` moves a task to `accepted`; an agent's report moves it to `reported`. Retry a failed or stalled task at most twice. Then change something real, such as the approach, the agent, or the scope, or ask the user. Do not resend the same prompt.

## One controller merges, on READY only

You are the controller, and the only one who merges. A worker's job ends at a READY block. A green check, a report, or "looks good" is not a READY.

```text
READY <task> <full commit sha>
base: <branch>@<sha it was built on>
check: <command> -> <result at this sha>
scope: <files changed, inside the brief's boundary: yes or no>
unverified: <each claim not checked at this sha, or none>
frozen: no pushes after this block
```

Refuse and send back when the sha is short or is not the branch head, the check ran on another commit, any field is missing, or the scope left its boundary. A missing `unverified` line is asked for, never assumed to be `none`. After READY the commit is frozen; a new commit needs a new READY.

READY moves a task to `reported`, and `agent-verify` still decides `accepted`. Then:

1. Fix the order: dependencies first, then the smallest change. Announce it.
2. For each task, confirm the branch head still equals the READY sha (`git rev-parse <branch>`).
3. Merge that one commit, run the check on the merged result, and mark it `merged`.
4. Merge nothing else until that check passes. If it fails, back out that merge and return the task to its owner with the failure. The rest of the order waits.

A real conflict goes back to the worker that owns the change. The controller does not edit or fix a worker's branch, and it does not resolve meaning it cannot verify. Decisions from the user reach workers through the controller, in the user's words.

## Recover after compaction or a new session

Before acting, reread the goal, the status table, each open task's done condition, and what is still unverified. Treat your summary of past work as a claim: confirm the state from files and commits. A task reported before the break stays `reported` until checked.

## Gotchas

- Results are confident whether right or wrong. A fresh agent handed your hypothesis tends to return it confirmed, so give it the evidence, not your conclusion.
- Actions the user approved for one agent do not extend to others. Pushing, publishing, and deleting need their own authorization.
- A parallel agent sharing your working tree can edit a file you are about to change. Finish or sequence edits to shared files such as hubs and indexes.
- A check that passed on each branch can fail on the merge. Green at READY does not cover the merged tree.
- A failure that passes on rerun is a flake to report, not a pass. A second failure is real.
- An agent's final report is not visible to the user. Relay what matters, including failures.
- Never predict the result of an agent still running. If asked, say it is still running.

## Report

State what was accepted and how it was checked, what was abandoned and why, and what remains unverified.
