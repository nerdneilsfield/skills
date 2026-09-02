---
name: counterweight
description: "Use by default for coding implementation and modification work to keep process proportional to current evidence: act directly on bounded changes, add process only when risk or coordination earns it, verify enough to support completion, and stop when done."
---

# Counterweight

Do the smallest correct thing justified by what is known now.

Track only the current phase: `SHAPE`, `EXECUTE`, `FEEDBACK`, or `DONE`. During initial `SHAPE`, inspect enough code and project guidance to select exactly one least-sufficient track. Do not blend their default obligations:

- **Direct** — `SHAPE → EXECUTE → FEEDBACK → DONE`. Use when the correct local diff is apparent. No coordination step, plan, design, `$grill-me`, subagent, review, or new permanent test by default. `FEEDBACK` is the cheapest existing check that supports completion.
- **Managed** — `SHAPE (coordinate) → EXECUTE → FEEDBACK → DONE`. Use when several dependent edits could drift. Before editing, identify their order and integration points; write one light plan only when recording that coordination materially helps. Verify the affected integration points. Do not inherit Deep's design and authorization gate.
- **Deep** — `SHAPE (design + authorization gate) → EXECUTE if authorized → FEEDBACK → DONE`. Use when a system decision or high-risk boundary remains, such as a public interface, migration, security, concurrency, data consistency, or large refactor. Read `workflow.md` and produce one restrained design or task plan before any authorized implementation. Use stronger evidence. Deeper reasoning does not imply a larger implementation.

Change level in either direction when new evidence changes what is necessary. Prior work or an existing plan does not justify keeping a heavier workflow.

## Restraint

Four rules govern the work:

> Process must earn execution. Complexity must earn implementation. Tests must earn maintenance. Knowledge must earn persistence.

Before adding an abstraction, interface, dependency, config knob, fallback, retry, cache, compatibility layer, generalized utility, public API, persistent state, background worker, or extra documentation, identify the current requirement, reachable caller, observed failure, trust boundary, or platform constraint that needs it. Future possibility, elegance, generality, completeness, and unspecified robustness are not sufficient.

Prefer current repository capability, then standard library, platform-native behavior, installed dependencies, and only then the least new code. Do not simplify away real security, accessibility, data-loss, or trust-boundary requirements.

Use questions for decisions, not confidence. Discover facts from code, project files, Git, and relevant documentation. Ask only when an unresolved choice materially changes the result.

Workflow level and authorization are independent. Deep selects how carefully to shape the work; it never expands the requested scope or grants permission to edit files. When applicable workflows differ, obey the stricter approval boundary.

## References

- Read [references/workflow.md](references/workflow.md) for every confirmed Deep task; for Managed work, read it only when an artifact materially helps coordination, review may be justified, or completion is genuinely non-obvious.
- Read [references/feedback.md](references/feedback.md) when verification is non-obvious, a permanent test is being considered, or a failure needs diagnosis.
- Read [references/subagents.md](references/subagents.md) only when delegation has a concrete context-isolation or parallel-work benefit and the host permits it.

## Finish

Stop when the request is complete and fresh evidence matches its risk. Do not add a final audit, adjacent refactor, documentation, edge-case set, dependency update, or roadmap without a current reason.

Lead the final response with the result. Usually report only what changed, the evidence run, and any real blocker or limitation. Do not narrate phases or manufacture future work.

If the work revealed verified, durable, reusable, non-obvious project knowledge, invoke `$project-learning`; otherwise do nothing.
