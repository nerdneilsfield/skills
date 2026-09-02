# Workflow

This reference expands workflow choices. The kernel's restraint remains binding.

The tracks are separate execution contracts, not labels for the same behavior. Direct must not inherit Managed or Deep ceremony. Managed must perform dependency coordination but must not inherit Deep's design and authorization gate. Deep must not confuse analysis depth with permission to implement.

## Shape

Read only enough code and project guidance to locate the requested behavior, the change point, and necessary consequences. Trace callers or broader data flow only when the change can affect them or current evidence leaves scope unclear. Shape asks only:

1. What outcome did the user request?
2. Which unresolved decision would change the implementation?
3. What is the least sufficient workflow now?

Fact questions belong to repository inspection. If a decision is blocking, ask one to three related questions together and include a recommended default with its reason.

## Direct

Use `SHAPE → EXECUTE → FEEDBACK → DONE` for bounded work: text and config edits, imports, simple wiring, established fields or flags, and local bugs whose cause and correct edit are evident. For Direct work, `FEEDBACK` is usually one cheap existing check.

Do not announce the classification, perform a coordination step, invoke `$grill-me`, or create a task list. Do not request confirmation merely to increase confidence. Inspect, edit, verify, stop.

## Managed

Use `SHAPE (coordinate) → EXECUTE → FEEDBACK → DONE` when dependent edits are numerous enough that execution could drift. During `SHAPE`, identify their order, shared constraints, and integration points. This coordination is required; a persisted artifact is not. If recording it materially helps execution, keep one light plan:

```markdown
# Goal

...

# Change

- ...

# Check

- ...
```

Omit empty sections. Do not add a proposal, separate design, task tree, risk matrix, milestones, future work, or implementation report. Do not inherit Deep's design and authorization gate. Execute after coordination when the request authorizes implementation; `FEEDBACK` covers the changed integration points, not unrelated suites.

## Deep

Use `SHAPE (design + authorization gate) → EXECUTE if authorized → FEEDBACK → DONE` only for a system-level decision or high-risk boundary. Initial `SHAPE` may still downgrade the task when inspection finds an existing facility that removes that boundary.

Deep determines analysis depth, not write authorization.

Before modifying source code, configuration, tests, or persistent documents, classify the user's requested deliverable explicitly:

- **Analysis, design, or review request**: inspect and produce the Deep artifact or response only. Do not implement.
- **Explicit implementation request**: implementation may proceed after unresolved material decisions are settled and the restrained task plan is written.
- **Ambiguous wording** such as "do this," "use Deep," "work on this," or a pasted proposal: do not treat it as write authorization. State the proposed implementation boundary and ask for approval.

If another applicable workflow requires an approval checkpoint, follow the stricter workflow. Creation of a plan is never permission to execute it.

Keep one restrained Deep artifact. If repository writes are not authorized, deliver it in the response only. Otherwise use the repository's existing planning or decision location; if none exists and a persistent artifact is warranted, use `docs/<topic>.md`. Select only necessary sections:

```markdown
# Goal

# Decisions

# Change

# Constraints

# Check
```

Add migration or rollback sections only when those operations exist. `FEEDBACK` must cover the actual system boundary and risks that justified Deep. If later evidence removes that boundary, downgrade and remove any artifact that no longer serves execution.

When the user requests plan stress-testing or invokes `$grill-me`, complete the Deep design first, then run `$grill-me` before requesting implementation approval. Do not begin implementation until the grill is resolved.

## Review

Review is not a completion ritual. Use independent judgment only when it has material expected value: high risk, security, migration, public API, large diff, substantial unresolved uncertainty, or an explicit user request.

Ask a reviewer to find only material issues:

1. The requested task is incomplete.
2. The change creates a real correctness, security, or data risk.
3. The implementation adds complexity unsupported by current need.

Suggestions about future elegance, optional hardening, or more tests are not findings. No material finding means report none; do not repeat review without new evidence.

## Completion

Choose evidence that can actually support the claim. Re-read the request and changed diff, then use fresh verification proportionate to risk. A passing narrow check does not imply unrelated properties.

Finish when requested behavior, necessary consequences, and real safety constraints are satisfied. Stop extra searching, testing, and review when they no longer discriminate between plausible outcomes.
