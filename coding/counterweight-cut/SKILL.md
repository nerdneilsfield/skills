---
name: counterweight-cut
description: >
  After implementation, list what in this diff did not earn the cost of
  staying: unused abstractions, extra dependencies, config knobs,
  compatibility layers, unearned tests, and process artifacts. Use when the
  user asks what can be deleted, whether the diff got fat, or to simplify
  this change. Default is a cut list, not a new diff. Not for implementing
  features, correctness review, product decisions, or whole-repo cleanup.
---

# Counterweight Cut

Ask whether already-written work earned the right to stay. This is not a
correctness review and not a second implementation pass.

Default: report only. Do not edit unless the user says to apply the list.
Analysis is not implementation.

## Scope

Look only at this session's diff, or the paths the user named. Do not scan
the repository. Whole-repo cleanup is a different product.

Do not take the implementer's chat rationale as evidence. Use callers, test
oracles, commit boundaries, and the user's original request. "Might need it
later" is not a reason to keep something.

## Freeze

Do not propose cutting:

- trust-boundary checks
- accessibility behavior
- data-loss protection
- published contracts
- CI-required checks
- tests or compatibility layers the user explicitly asked to keep

## Reverse the four earn rules

For each addition in scope:

- Process: is this plan, extra doc, or session-only test now in the tree?
- Complexity: is there a current caller or platform constraint?
- Tests: is there an independent oracle, and will this earn future maintenance?
- Knowledge: is this already in the code or existing docs?

## Output

One executable cut per line. No essay. If nothing qualifies, write `none`.

```text
CUT <path>:<symbol or hunk>
remove: <what>
keep: <what remains>
why: <which earn rule failed>
```

Forbidden: "consider refactoring", hypothetical cleanups, new lint rules,
checklists, or a convention document to prevent future fat.

## Apply

Edit only after an explicit "cut per this list" or equivalent. Apply only
listed, unfrozen items. Re-run the smallest check that still supports the
requested behavior. Do not start a new implementation round.
