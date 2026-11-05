---
name: agent-verify
description: "Use when another agent reports it finished, or looks stalled, and its work is about to be accepted, merged, or built on: check claims against files and commands, and decide accept, retry, or replace. Not for a routine review of your own diff, or for a small result you already inspected."
license: MIT
metadata:
  author: DengQi
---

# Verify agent work against evidence

A report is a claim. Accept work on what you can observe.

## Accept or reject

1. Re-read the brief's done condition.
2. Inspect the artifacts: `git status`, the diff, the commit, and the output files, with their timestamps.
3. Run the check yourself when it is cheap. Otherwise read the raw output, not the summary of it.
4. Compare scope: did it touch files outside the brief? Did it weaken a test, an assertion, or a grader to get a pass?
5. Spot-check the claims most likely to be wrong: numbers, external facts, and anything marked as done from memory.
6. Decide `accepted`, `retry` with a specific correction, or `abandoned`, and state the evidence.

Match effort to risk. A one-line fix needs less than a 45-file change. Check a large change by sampling the diff and running the tests.

## Detect a stall

Before calling an agent stuck, separate its status from real progress:

| Evidence | Meaning |
| --- | --- |
| Its process is alive and the log or files are changing | Working; leave it alone |
| Status says idle or finished, but expected files are absent | It ended without doing the work |
| Repeated identical reply across turns | Looping; a resend will not help |
| No file changes across a window longer than one step should take | Probably stuck; inspect its recent activity |

Allow one specific nudge that changes something. If it stalls again, replace it, handing over the existing artifacts through `agent-brief`. Do not keep nudging.

## Gotchas

- "Finished" reports that the turn ended, not that the work succeeded. Agents have ended a turn right after a wait command, with nothing done.
- A passing grader proves little if the grader never ran its checks. Zero tokens, an empty transcript, or a check that cannot fail means the run does not count.
- A skipped test is not a pass. Read skip and NA counts, since a missing dependency can quietly remove a check.
- Your own earlier statements are also claims. Do not cite a result as verified because you repeated it.
- A real but unverified claim should be reported as unverified, not dropped and not upgraded.
