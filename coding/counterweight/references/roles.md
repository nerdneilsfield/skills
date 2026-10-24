# Optional roles

Read this only when the user, the project config, or a concrete boundary asks for
one of the roles below. Each role is a separate read-only run with its own model,
so its value is independence, not extra effort. A role that sees the implementer's
reasoning is not independent.

How a host runs a role is in [hosts.md](hosts.md). With the `pi-counterweight`
extension installed, the extension runs them; read its README, not this file,
for configuration.

| Role | Input | Returns | Never |
| --- | --- | --- | --- |
| explorer | one question | compact evidence; the format is in [subagents.md](subagents.md) | edits, design advice |
| review | the request and the diff | `WRONG` blocks for behavior errors and weakened real boundaries; `none` | missing tests, refactors, fixes |
| over_review | the request and the diff | `CUT` blocks for what did not earn its place; `none` | correctness, replacement designs |
| research | one question the main model could not settle | conclusion first; unread parts marked `未核实` | implementation, a roadmap |
| historian | the current history document and a stage report | the whole rewritten document | invented dates, ids, or causes |
| planner | the transcript so far and the edit about to happen | one four-part fix plan | tool use, reviewing earlier work |

## Shared rules

- **Read only.** Restrict the role to read and search tools. A prompt that says
  "do not edit" is not a restriction.
- **One shot.** The role keeps no memory. When it needs more, it replies with
  `ASK:` on the first line and its questions after it, and nothing else. Answer
  inside the request and run it again. Never ask it for a design choice.
- **Reports, never gates.** A role result does not decide whether the work is
  done. The end check, if any, decides that. Treat findings as input to verify,
  not as orders: a reviewer can be wrong, and the main model sees code the role
  was not given.
- **Size the timeout to the input.** Start at 300 seconds. If the input is
  plainly large (a long diff, many files), start higher. On a timeout, double it
  (300, 600, 1200, 1800) and run again. Cap at 1800: a role that still times out
  there needs a smaller input (split by file or commit), not more time.
- **Pick a model for the job.** Explorer and historian can be cheap. Review and
  over_review should differ from the implementer's model. Planner must be
  stronger than the implementer (see below).

## Review and over_review

Run only the ones the user or the project chose. They are independent roles,
not a pair: review alone, over_review alone, or both are all valid. Run them on
a coherent unit of finished work, not on every edit. Pass the request in the
user's words and the diff; the roles do not run `git diff` themselves. When both
are chosen, run them on the same diff in parallel.

When one earns its cost is the material-risk test in [workflow.md](workflow.md)
(Review). `none` ends a run; do not rerun on the same diff without new evidence.

## Historian

One document, `.cw/HISTORY.md` or the project's existing equivalent, rewritten
whole on each report. Report after a stage result lands: a commit, a decision,
a finished sub-agent task. State dates and commit ids yourself; the historian
leaves out any fact neither the report nor the repository confirms, and asks
with `ASK:` when only you can settle it.


## Planner (PAUSE)

Before the first edit to source in a user turn, stop the edit, give a model that
cannot see the workspace the whole investigation so far, and get one plan back:
cause, location, approach, reason. Then make the edit, following the plan or
saying why not. Once per turn. If the planner fails or times out, make the edit
anyway: a plan is advice, and the implementer sees code the planner does not.

Evidence is one paper: a weak executor (Qwen3-Coder-30B) with a strong planner
raised OpenHands on SWE-bench from 45.4% to 62.2%. With the same model as
planner and executor, only 5.4% of failed runs were rescued; self-reflection
rescued 5.8%. It was not tested on a strong executor, so:

- **The planner must be stronger than the implementer.** The same model gives
  nothing. Use it for a weak or cheap implementer, or when the cause is still
  unclear after investigation.
- **Fire once, after investigation.** Earlier gives the planner too little to
  read. Not before a trivial edit.

## Forcing a role

A prompt that says "always run review" is a default the model can skip, not a
force. Forcing needs something outside the model's own turn to trigger it: an
extension, a host hook, or a wrapper script (see [hosts.md](hosts.md)), and each
forced run costs a model call.
