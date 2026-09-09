---
name: counterweight
description: "Manage coding implementation from planning through execution, functional verification, and task-based commits. Use by default for coding changes; scale the workflow to the task and eliminate work without a concrete payoff."
---

# Counterweight

Manage work through executable plans, clear task boundaries, functional acceptance, and timely commits, with process proportional to the task. Reducing low-ROI work must not remove the coordination and execution discipline the chosen track requires.

Optimize for time to useful, runnable software. Implement the smallest working version of the requested behavior, run it, and make it easy for the user to try. Real usage and reported failures guide the next iteration. Do not delay that feedback loop to chase imagined completeness or 100% robustness. Preserve explicit requirements and real safety boundaries.

Track the current phase: `SHAPE`, `EXECUTE`, `FEEDBACK`, or `DONE`; Deep also records task status in its plan. During initial `SHAPE`, inspect enough code and project guidance to select exactly one least-sufficient track. Do not blend their default obligations:

- **Direct** — `SHAPE → EXECUTE → FEEDBACK → DONE`. Use when the correct local diff is apparent. No coordination step, plan, design, `$grill-me`, subagent, review, or new permanent test by default. `FEEDBACK` is the cheapest existing check that supports completion.
- **Managed** — `SHAPE (coordinate) → EXECUTE → FEEDBACK → DONE`. Use when several dependent edits could drift. Before editing, identify their order and integration points; write one light plan only when recording that coordination materially helps. Verify the affected integration points. Do not inherit Deep's design and authorization gate.
- **Deep** — `SHAPE (decisions + executable plan) → EXECUTE (task → run/check → commit) → FEEDBACK (working feature) → DONE`. Use when a system decision or high-risk boundary remains, such as a public interface, migration, security, concurrency, data consistency, or large refactor. Read [references/workflow.md](references/workflow.md) and [references/deep.md](references/deep.md). Resolve material decisions, specify independently verifiable tasks, and execute the plan when authorized. Deep earns concrete instructions and progress checkpoints, not a larger implementation or automatic review pipeline.

Change level in either direction when new evidence changes what is necessary. Prior work or an existing plan does not justify keeping a heavier workflow.

## Restraint

Four rules govern the work:

> Process must earn execution. Complexity must earn implementation. Tests must earn maintenance. Knowledge must earn persistence.

Before adding an abstraction, interface, dependency, config knob, fallback, retry, cache, compatibility layer, generalized utility, public API, persistent state, background worker, or extra documentation, identify the current requirement, reachable caller, observed failure, trust boundary, or platform constraint that needs it. Future possibility, elegance, generality, completeness, and unspecified robustness are not sufficient.

Distinguish an existing implementation from a compatibility commitment. Code just written in the current task, or unreleased code with no evidence of external use, should be changed directly along with its callers, interfaces, and data structures. Do not retain old interfaces, compatibility parameters, fallback branches, or migration layers merely because an earlier implementation exists.

Evaluate compatibility only when evidence identifies a published contract, independently deployed consumers, persistent data that must be preserved, or an explicit user requirement. Check task context and repository evidence first; local callers that can be updated together do not justify a compatibility layer. If concrete signs of a compatibility obligation remain unresolved and the answer would materially change the implementation, ask one specific question before choosing an approach. Otherwise proceed with the direct change; do not ask about compatibility routinely or add it "just in case". Unreleased status does not override known consumers or data-preservation requirements.

Prefer current repository capability, then standard library, platform-native behavior, installed dependencies, and only then the least new code. Do not simplify away real security, accessibility, data-loss, or trust-boundary requirements.

Use questions for decisions, not confidence. Discover facts from code, project files, Git, and relevant documentation. Ask only when an unresolved choice materially changes the result.

Verification defaults to a runnable-code check and simple functional confirmation of the requested behavior, combined in one check where possible. Deep strengthens planning and execution discipline, not test volume. Do not add tests for speculative, extremely unlikely failures; expand checks only for observed failures, explicit requirements, or concrete risks in the changed path.

Workflow level and authorization are independent. Deep selects how carefully to shape the work; it never expands the requested scope or grants permission to edit files. When applicable workflows differ, obey the stricter approval boundary.

## Tool economy

Choose available tools for low latency and low context cost while preserving the evidence needed for the task. This applies to all tracks, including Deep.

- Prefer `rtk` for shell commands when installed, for example `rtk git status` and `rtk git diff`. If filtering hides necessary details, use `rtk proxy` or raw output for that check. If unavailable, use existing tools directly; do not turn the task into tool installation or setup.
- Narrow searches by path, symbol, or pattern, then read the relevant slices. Use `rg` or a precise symbol query for local questions; use broader repository tooling only when the question needs it. Avoid whole-repository dumps, full logs, or repeated reads of unchanged content.
- Request only needed fields and bounded output from tools. Batch independent reads or searches when it saves round trips; keep dependent actions sequential. Reuse results already obtained unless the relevant state changed.
- Prefer a direct CLI or API over UI automation when it provides the same result with less overhead. Do not add tool discovery, delegation, or orchestration unless it reduces the actual work.

## References

- Read [references/workflow.md](references/workflow.md) for every confirmed Deep task; for Managed work, read it only when an artifact materially helps coordination, review may be justified, or completion is genuinely non-obvious.
- Read [references/feedback.md](references/feedback.md) when verification is non-obvious, a permanent test is being considered, or a failure needs diagnosis.
- Read [references/subagents.md](references/subagents.md) only when delegation has a concrete context-isolation or parallel-work benefit and the host permits it.

## Commits during execution

Direct, Managed, and Deep share one commit policy: group by task intent, dependencies, and review/rollback boundaries, using the grouping principles of `/co-commit`. Track selection does not determine commit count. Read [references/commits.md](references/commits.md) before the first implementation edit to identify useful commit boundaries; no separate planning artifact is needed for Direct.

Commit each coherent unit as soon as its simple functional or run check passes, including useful intermediate stages. Do not accumulate completed units until the entire request is finished. A task can produce several commits, while tightly coupled steps may need one commit. Respect explicit no-commit instructions and repository or host restrictions. Analysis, review, and plan-only requests do not authorize implementation commits. Local commits do not authorize push, PR creation, merge, or release.

## Finish

Stop when the requested behavior works, the necessary run/check succeeded, and the commit disposition is resolved. Perform Deep's planned functional acceptance; do not add an audit, adjacent refactor, documentation, edge-case set, dependency update, or roadmap without a current reason. Make the result easy to try with a short run command or usage example when useful. Do not wait indefinitely for user feedback or invent another iteration before it arrives.

Lead the final response with the result. Usually report only what changed, the evidence run, commit subjects or the concrete reason for not committing, and any real blocker or limitation. Do not copy commit hashes into plans or routine reports. Do not narrate phases or manufacture future work.

If the work revealed verified, durable, reusable, non-obvious project knowledge, invoke `$project-learning`; otherwise do nothing.
