# Workflow

This reference expands workflow choices. Track selection and authorization
live in `SKILL.md`. The kernel's restraint remains binding.

The tracks are separate execution contracts, not labels for the same
behavior. Direct must not inherit Managed or Deep ceremony. Managed must
perform dependency coordination but must not inherit Deep's design gate.
Deep must not confuse analysis depth with permission to implement.

## Shape

Read only enough code and project guidance to locate the requested behavior,
the change point, and necessary consequences. Trace callers or broader data
flow only when the change can affect them or current evidence leaves scope
unclear. Shape asks only:

1. What outcome did the user request?
2. Which unresolved decision would change the implementation?
3. What is the least sufficient workflow now?

Fact questions belong to repository inspection. If a decision is blocking,
ask one to three related questions together and include a recommended default
with its reason.

## Direct

Use Direct for bounded work: text and config edits, imports, simple wiring,
established fields or flags, and local bugs whose cause and correct edit are
evident. Feedback is usually one cheap existing check.

Do not announce the classification, perform a coordination step, create a
task list, or invoke a grill or cut. Do not request confirmation merely to
increase confidence. Inspect, edit, verify, stop.

## Managed

Use Managed when dependent edits are numerous enough that execution could
drift. Identify their order, shared constraints, and integration points
before editing. This coordination is required; a persisted artifact is not.
If recording it materially helps execution, keep one light plan:

```markdown
# Goal

...

# Change

- ...

# Check

- ...
```

Omit empty sections. Do not add a proposal, separate design, task tree, risk
matrix, milestones, future work, or implementation report. Do not inherit
Deep's design gate. Execute after coordination when the request authorizes
implementation; feedback covers the changed integration points, not
unrelated suites.

## Deep

Use Deep only for a system-level decision or high-risk boundary. Initial
inspection may still downgrade the task when an existing facility removes
that boundary. Read [deep.md](deep.md) for the plan contract, readiness gate,
task execution loop, and integration acceptance.

Authorization follows `SKILL.md`. Deep determines analysis depth, not write
permission. Infer intent from the whole conversation. A mode selection or
pasted proposal alone does not authorize implementation. If it remains
unclear whether the user wants analysis or implementation, state the proposed
boundary and ask.

Keep design decisions, executable tasks, and progress in one Deep plan,
linking an existing spec rather than duplicating it. For implementation,
persist it in the existing planning location or
`docs/plans/YYYY-MM-DD-<topic>.md` when no convention exists. For plan-only
work, honor the requested output location; without authorization to write a
plan file, deliver it in the response. An analysis or design-only deliverable
need not invent implementation tasks. If later evidence removes the Deep
boundary, downgrade and record why; do not delete existing artifacts merely
to reduce ceremony.

If `$grill-me` is installed and the user asks to be grilled or to
pressure-test the plan, complete the Deep design first, then run it before
requesting implementation approval. Do not begin implementation until that
grill is resolved. If it is not installed, ask the material questions
directly using the same restraint.

## Review

Before committing, inspect the changed diff for scope and obvious mistakes.
A separate review pass or reviewer is not a default gate in any track,
including Deep. Add one only for a concrete difficult boundary, an observed
concern, or an explicit request where independent judgment has material
value and the host permits it. Do not turn routine diff inspection into a
multi-stage review pipeline, or call it independent review.

Ask a reviewer to find only material issues:

1. The requested task is incomplete.
2. The change creates a real correctness, security, or data risk.
3. The implementation adds complexity unsupported by current need.

Suggestions about future elegance, optional hardening, or more tests are not
findings. No material finding means report none; do not repeat review without
new evidence.

## Completion

Choose evidence that can actually support the claim. Re-read the request and
changed diff, then use fresh verification proportionate to risk. A passing
narrow check does not imply unrelated properties.

Finish when requested behavior, necessary consequences, and real safety
constraints are satisfied. Stop extra searching, testing, and review when
they no longer discriminate between plausible outcomes.

Resolve local commits using [commits.md](commits.md) when grouping is
non-obvious, the index is dirty, or a hook fails; otherwise the four bullets
in `SKILL.md` are enough. For Deep, retain only functional evidence and real
limitations that help resumption. Record separate review results only if a
review was actually needed.
