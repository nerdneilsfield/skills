# Changelog

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
