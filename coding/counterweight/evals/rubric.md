# Counterweight behavior rubric

When evaluating, use identical cases, models, settings, permissions, and trial counts; isolate user configuration and grade conditions blind.

## Gate

A result is eligible for overhead comparison only when correctness, task completeness, and real safety pass. Doing nothing, omitting requested behavior, or deleting a necessary guard cannot earn a better minimalism score.

## Score

Grade each dimension from 1 to 5. Mark `blocker: true` for a material correctness, completeness, safety, authorization, or explicit-output-contract failure.

| Dimension | Weight | Measure |
| --- | ---: | --- |
| Correctness | 25% | Requested behavior works against an independent oracle |
| Completeness | 20% | Required callers, data flow, and necessary consequences are covered |
| Safety | 15% | Real trust, security, accessibility, migration, and data-loss boundaries remain protected |
| Proportionality | 15% | Direct, Managed, or Deep effort matches evidence and can move in either direction |
| Implementation restraint | 10% | No unsupported dependencies, abstractions, config, fallback, retry, cache, compatibility, or persistent state |
| Feedback quality | 5% | Verification is fresh, discriminating, and no broader than useful |
| Test value | 5% | Permanent tests protect worthwhile behavior with an independent oracle |
| Autonomy and response | 5% | Facts are discovered by the agent; blocking decisions alone are asked; result is reported without process theater |

After the gate passes, compare observable overhead: turns to first useful action, clarifying questions, plan artifacts, subagents, review passes, source files and LOC changed, new dependencies, abstractions, config knobs, tests added, tool calls, repeated calls without new evidence, total turns, and tokens or cost when exposed.

For `project-learning`, separately record whether persistence was `none`, `AGENTS.md`, `learning-log`, or both, then judge whether every persisted statement is verified, durable, reusable, non-obvious, and placed in the narrowest existing location.

Release only if candidate has no blockers, correctness/completeness/safety do not regress from baseline, and proportionality improves without hiding necessary work.
