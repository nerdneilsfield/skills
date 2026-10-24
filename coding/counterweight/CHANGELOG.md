# Changelog

## 0.6.0 — 2026-10-24

- Deep closeout sorts the plan's text once by what earns keeping; a finished
  plan is a record, not a living spec.
- New `references/roles.md`: optional read-only roles and when each earns its
  cost.
- New `references/hosts.md`: running the roles on codex, opencode, kimi code,
  grok build, and pi without the extension, with verified and unverified facts
  kept apart.
- `counterweight-setup` gains an optional, user-chosen roles section.
- Unchanged: Direct, Managed, track selection, and zero subagents and zero
  automatic reviewers by default.

## 0.5.0 — 2026-09-20

- Kernel: one-glance self-check before commit; no extra review round.
- Optional `$counterweight-cut` exit after Deep work that added an
  abstraction, dependency, test file, or compatibility layer. Ask once;
  never start unasked. Direct and small Managed do not mention it.
- Companion `counterweight-cut`: short, report-only cut list. Not part of
  setup's default workflow.

## 0.4.0 — 2026-09-20

Pin this version for eval A/B. Changes:

- Frontmatter `version` and a trigger-rich description with a negative boundary.
- Single source-of-truth table in this package README.
- Implementation ladder, track/authorization/report tables, and calibration
  examples in the kernel. Check-choice list lifted into `SKILL.md`.
- Direct no longer reads `commits.md` unconditionally; local commits remain
  the default. Host Git wrappers are generic; this package no longer names a
  sibling commit skill.
- Companions are optional. Setup writes five executable rules instead of a
  sole-workflow claim. README files no longer inline the setup block.
- Deep gains a ready-plan sample; authorization restatements point at
  `SKILL.md`.
- Evals split into `core.jsonl` / `suite.jsonl` with fixtures and a YAGNI
  baseline protocol. Round 1 measured instruction overhead and a policy
  oracle; live model trials are still pending.
