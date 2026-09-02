# Workflow

This reference expands workflow choices. The kernel's restraint remains binding.

## Shape

Read only enough code and project guidance to locate the requested behavior, the change point, and necessary consequences. Trace callers or broader data flow only when the change can affect them or current evidence leaves scope unclear. Shape asks only:

1. What outcome did the user request?
2. Which unresolved decision would change the implementation?
3. What is the least sufficient workflow now?

Fact questions belong to repository inspection. If a decision is blocking, ask one to three related questions together and include a recommended default with its reason.

## Direct

Use `SHAPE → EXECUTE → FEEDBACK → DONE` for bounded work: text and config edits, imports, simple wiring, established fields or flags, and local bugs whose cause and correct edit are evident. For Direct work, `FEEDBACK` is usually one cheap existing check.

Do not announce the classification or create a task list. Do not request confirmation merely to increase confidence. Inspect, edit, verify, stop.

## Managed

Use Managed only when dependent edits are numerous enough that execution could drift. If an artifact is useful, keep one task document:

```markdown
# Goal

...

# Change

- ...

# Check

- ...
```

Omit empty sections. Do not add a proposal, separate design, task tree, risk matrix, milestones, future work, or implementation report. Execute after writing it; approval is required only when the user requested planning only or a real unresolved decision remains.

## Deep

Use Deep only for a system-level decision or high-risk boundary. Keep one restrained document and select only necessary sections:

```markdown
# Goal

# Decisions

# Change

# Constraints

# Check
```

Add migration or rollback sections only when those operations exist. Investigation may show that an existing facility solves the problem; then downgrade and remove any artifact that no longer serves execution.

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
