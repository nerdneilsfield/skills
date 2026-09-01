# Subagents

Default to zero subagents and zero automatic reviewers. Delegate only when expected context or time saved exceeds coordination cost and the host permits it.

## Context isolation

Use one read-only explorer for high-noise work such as repository inventory, caller discovery, Git history, large documentation lookup, or initial log sorting. Give it one question, bounded scope, no implementation, no architecture ownership, no further delegation, and no unrelated research.

If the host makes model choice simple, use a cheaper model that is sufficient for retrieval. Do not build or hard-code a provider router.

Return compact evidence rather than copied source:

```yaml
relevant:
  - path: ...
    symbol: ...
    reason: ...
flow: ...
constraint: ...
unknown: ...
```

The useful transformation is large noisy context in, small actionable evidence out.

## Independent work

Parallel work earns delegation only when tasks are genuinely independent, mutable scope does not overlap, and integration cost is low. Do not create a default Planner/Implementer/Tester/Reviewer pipeline. Small tasks, work requiring shared evolving context, or delegation that merely repeats the parent's reading remain local.

Review delegation follows the material-risk criteria in [workflow.md](workflow.md), not task completion alone.
