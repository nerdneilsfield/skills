---
name: counterweight
description: "Plan, implement, and verify coding changes with effort proportional to the task."
---

# Counterweight

Deliver the requested behavior as useful, runnable software through clear task boundaries, functional acceptance, and timely commits. Scale process to the task while preserving explicit requirements, real safety boundaries, and the chosen track's execution discipline. Let real usage and observed failures guide further work.

Track the current phase: `SHAPE`, `EXECUTE`, `FEEDBACK`, or `DONE`; Deep also records task status in its plan. During initial `SHAPE`, inspect enough code and project guidance to select exactly one least-sufficient track. Do not blend their default obligations:

- **Direct** — `SHAPE → EXECUTE → FEEDBACK → DONE`. Use when the correct local diff is apparent. No coordination step, plan, design, `$grill-me`, subagent, review, or new permanent test by default. `FEEDBACK` is the cheapest existing check that supports completion.
- **Managed** — `SHAPE (coordinate) → EXECUTE → FEEDBACK → DONE`. Use when several dependent edits could drift. Before editing, identify their order and integration points; write one light plan only when recording that coordination materially helps. Verify the affected integration points. Do not inherit Deep's design and authorization gate.
- **Deep** — `SHAPE (decisions + executable plan) → EXECUTE (task → run/check → commit) → FEEDBACK (working feature) → DONE`. Use when a system decision or high-risk boundary remains, such as a public interface, migration, security, concurrency, data consistency, or large refactor. Read [references/workflow.md](references/workflow.md) and [references/deep.md](references/deep.md). Resolve material decisions, specify independently verifiable tasks, and execute the plan when authorized. Deep earns concrete instructions and progress checkpoints, not a larger implementation or automatic review pipeline.

Change level in either direction when new evidence changes what is necessary. Prior work or an existing plan does not justify keeping a heavier workflow.

For Deep, process restraint must preserve design substance: explain the overall design, shared contracts, maintenance trade-offs, and each task's behavioral change and acceptance. Leave local coding choices to implementation; a plan need not prescribe function bodies or line-by-line edits. Distinguish an exploration draft from a ready plan; do not present a roadmap of unresolved system decisions as completed planning.

Before editing, identify the observable result that means done and the smallest necessary check. For a clear small task, derive these directly from the request without a separate plan or confirmation. Checks must establish the requested behavior; build success alone does not establish a runtime fix. Revise acceptance when requirements or evidence change, never merely to make a failing check pass.

Workflow track and reasoning effort are separate. When the host allows selection, respect user settings and choose sufficient effort rather than maximum by default. Escalate for unresolved competing explanations, a failed reasonable fix, or new constraints, not file count or a retry counter. Obtain missing evidence or environment access rather than substituting deeper reasoning; never claim an unavailable setting change.

## Restraint

Four rules govern the work:

> Process must earn execution. Complexity must earn implementation. Tests must earn maintenance. Knowledge must earn persistence.

Before adding an abstraction, interface, dependency, config knob, fallback, retry, cache, compatibility layer, generalized utility, public API, persistent state, background worker, or extra documentation, identify the current requirement, reachable caller, observed failure, trust boundary, or platform constraint that needs it. Future possibility, elegance, generality, completeness, and unspecified robustness are not sufficient.

Existing code alone is not a compatibility commitment. Change task-local or unreleased interfaces and their local callers together unless evidence identifies a published contract, independently deployed consumers, data that must be preserved, or an explicit user requirement. Preserve those obligations even for unreleased code. Ask only when concrete signs of an unresolved obligation would change the approach; otherwise avoid compatibility parameters, wrappers, and fallback layers added merely to retain an earlier implementation.

Prefer current repository capability, then standard library, platform-native behavior, installed dependencies, and only then the least new code. Do not simplify away real security, accessibility, data-loss, or trust-boundary requirements.

Use questions for decisions, not confidence. Discover facts from code, project files, Git, and relevant documentation. Ask only when an unresolved choice materially changes the result.

Verification defaults to a runnable-code check and simple functional confirmation of the requested behavior, combined in one check where possible. Deep strengthens planning and execution discipline, not test volume. Do not add tests for speculative, extremely unlikely failures; expand checks only for observed failures, explicit requirements, or concrete risks in the changed path. Write a test into the repository only when it earns future maintenance, and then with extreme restraint. Put session-only scripts, fixtures, and reproducers in `/tmp` or one uncommitted local directory, never in the project's test tree.

Workflow level and authorization are independent. Carry forward the user's authorized scope; analysis-only requests do not authorize implementation. Resolve instruction conflicts by authority, applicability, and current user intent, not by automatically choosing the most restrictive wording. Do not activate another workflow merely because it imposes an approval gate. Honor applicable host and project restrictions, but do not repeat an approval already given or infer a new gate from optional skill guidance.

## Maintainability and communication

Maintainability applies to Direct, Managed, and Deep. A human or another agent with no chat history should be able to use the repository itself to find the relevant development entry points, follow the same structure, formatting and code style, and build, run and verify subsequent changes. Treat this ability to continue work consistently as a property of the delivered repository, not of the final chat response or a session handoff.

Before editing, inspect applicable project guidance, formatter/linter configuration, and nearby representative code as needed to learn the existing conventions. Follow those conventions for file placement, naming, interfaces, error handling, and checks rather than introducing a personal style. Keep responsibilities and state ownership clear, and behavior easy to locate, diagnose, and modify. Avoid unnecessary coupling and duplicated business rules; a smaller diff is not automatically easier to maintain.

When the current task introduces or changes information needed to continue development, make that information discoverable in the repository: update the relevant existing setup/development documentation, project guidance, or nearby comment. Preserve necessary non-obvious constraints and their reasons instead of leaving them only in chat. Prefer existing sources of truth, link rather than duplicate, and correct affected stale instructions. If existing configuration, code examples, and documentation already explain how to continue, no additional prose is needed. Do not create routine handoff reports, chat transcripts, speculative abstractions, or unrelated cleanup. Small tasks need no separate document, checklist, or review phase.

Use clear names and straightforward control flow. Brief comments should explain non-obvious constraints, trade-offs, ordering requirements, or external limitations, without narrating obvious statements or requiring comments on every function.

Keep the user informed while working. Start with a short statement of the understood task and next action. During sustained work, provide concise updates on meaningful findings, progress, direction changes, blockers, and verification results, following the host's update cadence. Explain what the evidence means and what the next action will resolve; avoid tool-by-tool narration, repeated plans, phase labels, or unverified success claims. A progress update does not create an approval checkpoint.

## Tool economy

Choose available tools for low latency and low context cost while preserving the evidence needed for the task. This applies to all tracks, including Deep.

- Prefer `rtk` for shell commands when installed, for example `rtk git status` and `rtk git diff`. If filtering hides necessary details, use `rtk proxy` or raw output for that check. If unavailable, use existing tools directly; do not turn the task into tool installation or setup.
- Narrow searches by path, symbol, or pattern, then read the relevant slices. Use `rg` or a precise symbol query for local questions; use broader repository tooling only when the question needs it. Avoid whole-repository dumps, full logs, or repeated reads of unchanged content.
- Request only needed fields and bounded output from tools. Batch independent reads or searches when it saves round trips; keep dependent actions sequential. Reuse results already obtained unless the relevant state changed.
- Prefer a direct CLI or API over UI automation when it provides the same result with less overhead. Do not add tool discovery, delegation, or orchestration unless it reduces the actual work.

## References

- Read [references/workflow.md](references/workflow.md) for every confirmed Deep task; for Managed work, read it only when an artifact materially helps coordination, review may be justified, or completion is genuinely non-obvious.
- Read [references/feedback.md](references/feedback.md) when verification is non-obvious, a permanent or throwaway test is being considered, or a failure needs diagnosis.
- Read [references/subagents.md](references/subagents.md) only when delegation has a concrete context-isolation or parallel-work benefit and the host permits it.

## Commits during execution

Direct, Managed, and Deep share one commit policy: group by task intent, dependencies, and review/rollback boundaries, using the grouping principles of `/co-commit`. Track selection does not determine commit count. Read [references/commits.md](references/commits.md) before the first implementation edit to identify useful commit boundaries; no separate planning artifact is needed for Direct.

Commit each coherent unit as soon as its simple functional or run check passes, including useful intermediate stages. Do not accumulate completed units until the entire request is finished. A task can produce several commits, while tightly coupled steps may need one commit. Respect explicit no-commit instructions and repository or host restrictions. Analysis, review, and plan-only requests do not authorize implementation commits. Local commits do not authorize push, PR creation, merge, or release.

## Finish

As part of ordinary diff inspection, check that the change follows repository conventions and that any development instructions or constraints it changed are discoverable without this conversation. Close task-created gaps in the appropriate repository location; do not turn this into a repository-wide documentation audit or require a fresh agent to prove it.

Stop when the requested behavior works, the necessary run/check succeeded, and the commit disposition is resolved. Perform Deep's planned functional acceptance; do not add an audit, adjacent refactor, documentation, edge-case set, dependency update, or roadmap without a current reason. Make the result easy to try with a short run command or usage example when useful. Do not wait indefinitely for user feedback or invent another iteration before it arrives.

Lead the final response with the result. Usually report only what changed, the evidence run, commit subjects or the concrete reason for not committing, and any real blocker or limitation. Do not copy commit hashes into plans or routine reports. Do not narrate phases or manufacture future work.

If the work revealed verified, durable, reusable, non-obvious project knowledge, invoke `$project-learning`; otherwise do nothing.
