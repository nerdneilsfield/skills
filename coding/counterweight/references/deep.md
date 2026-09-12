# Deep: plan and execute

Read this for every confirmed Deep task. Keep the implementation narrow; make its execution explicit. The harness is a concrete plan, runnable checkpoints, and recorded progress, not exhaustive testing or review ceremony. This contract is self-contained and does not require another workflow skill.

## Build a plan another session can execute

Inspect the relevant source, callers, repository instructions, run/check commands, and Git state before planning. Record only relevant pre-existing changes needed to distinguish task work from user work. Verify referenced paths and symbols; mark new paths as new. Do not invent repository facts or commands.

Use one plan with these required parts for implementation work:

1. **Outcome and scope:** observable success, exclusions, and the request or spec being implemented.
2. **Design and constraints:** the current behavior and proposed change, affected components and their responsibilities, and the chosen approach with rationale for consequential trade-offs. Specify shared interface/data contracts and invariants. Where they determine correctness, describe data flow, state transitions and triggers, resource ownership/lifetime, limits and overflow behavior, and failure/recovery paths. Include rollout, compatibility, and rollback only when relevant. Separate resolved decisions from blocking unknowns; requirements such as "bounded queues" or "recover after failure" need concrete mechanisms, not just restatement.
3. **Acceptance map:** assign each required behavior or invariant an ID; map it to an owning task, simple verification procedure, and expected observable result. Confirm the code runs and the requested function works. Include failure behavior only for a reported bug, explicit requirement, or concrete reachable risk; do not invent rare scenarios to populate the map.
4. **Ordered tasks:** every task identifies an independently verifiable deliverable, affected modules or known files, the intended behavioral change and approach, dependencies/shared contracts, acceptance procedure and expected result, and intended commit boundary. Identify exact symbols only when they are a necessary integration point. The next task must be actionable without another system-design phase; it need not prescribe local coding steps. A task title and a promise to design it later are insufficient.
5. **Execution and progress:** how to resume, task states, completed evidence, blockers, and final integration checks.

Split tasks where one deliverable could be accepted while its neighbor is rejected. Fold scaffolding, tests, and documentation into the behavior that needs them. Avoid whole layers such as "implement backend" and trivial tasks such as "create empty file". If a task cannot be verified or committed coherently without its successor, redraw the boundary or explicitly group them into one verification/commit unit.

Task boundaries guide commits but do not impose a one-task/one-commit rule. Apply `commits.md` throughout execution: commit independently useful, verified intermediate stages within a task as they become ready. Do not wait for the whole task or plan to finish, and do not duplicate Git history in the plan.

Order work toward the earliest useful runnable slice after establishing a coherent design for the requested scope. Resolve decisions that determine feasibility, task boundaries, or shared contracts before treating the implementation plan as ready; a runnable first slice does not justify postponing those decisions. Do not front-load a test framework, speculative hardening, or generalized infrastructure. Complete the user's requested scope, but do not append hypothetical follow-up work. Give the user a runnable entry point as soon as useful; continue already-authorized work without waiting unless their feedback is needed for a material decision.

Describe each task through its target, approach, and observable result. Specify shared data shapes, state transitions, or interface semantics where correctness or coordination depends on them; exact signatures are needed only when a fixed external or existing contract requires them. Leave helper functions, internal decomposition, local algorithms, and coding order to the implementer unless a consequential design decision requires otherwise. Do not include function bodies, implementation code, or line-by-line edit recipes by default. "Add error handling", "write tests", and "ensure compatibility" without concrete behavior and expected results are still insufficient.

Apply the main skill's shared maintainability standard. In a Deep plan, record consequential maintenance trade-offs and accepted costs alongside the relevant design decisions, using current repository evidence and requested behavior. Do not add a separate maintenance essay or checklist.

For each check, supply a working directory, command or precise manual procedure, necessary input/setup, and expected outcome. State what confirms the requested behavior, not merely "exit 0". Prefer an existing run command with a simple input/output example; reuse focused tests when useful, without requiring new test code. If an environment is unavailable, state what cannot yet be verified and how to obtain that evidence. Unknown commands or unresolved contracts block readiness for affected tasks; do not fill gaps with plausible-looking shell commands.

## Plan template

Replace the fields below with repository evidence. Omit irrelevant optional fields; do not leave implementation-critical placeholders in a ready plan.

```markdown
# <Topic> implementation plan

Plan readiness: <exploration draft / ready / blocked; concrete reason if not ready>.

## Outcome and scope

<Requested behavior, exclusions, spec link if one exists.>
Existing changes: <relevant paths and ownership, or none>.
Authorization: <implementation / plan-only; material approvals still needed>.

## Design and constraints

<Current behavior, proposed component responsibilities and interactions.>
<Resolved approach and rationale, shared contracts and invariants.>
<Relevant state transitions, ownership, limits and failure/recovery mechanisms.>
<Rollout and rollback procedure when relevant.>

## Acceptance map

| ID | Behavior or invariant | Task | Check and expected result |
| --- | --- | --- | --- |
| A1 | <observable requirement> | T1 | <procedure and oracle> |

## Execution

Read this plan and linked spec; use counterweight's references/deep.md
execution loop. Run ready tasks in dependency order, one implementation
task at a time. Run/check, inspect the diff, commit, and update this plan before taking
the next dependent task. Continue through all authorized tasks without
asking for approval at each checkpoint.

### T1: <independently verifiable deliverable>

Status: pending
Depends on: <task IDs or none>
Acceptance: <IDs>
Targets: <Affected modules or verified files; mark proposed new files; exact symbols only when needed>
Contracts: <inputs/outputs shared with other tasks, where relevant>

- [ ] <Behavioral change, chosen approach, and relevant integration boundary.>
- [ ] <Verification step: cwd, command/procedure, prerequisites, expected result.>
- [ ] Inspect the diff for scope, contract mistakes, and unnecessary code.
- [ ] Commit <intended coherent scope and proposed subject>.

Evidence: <fill during execution: run/check and observed result>

## Final acceptance

<Smallest run/smoke procedure with expected results confirming the assembled
feature works; reuse task evidence when it already proves this.>

## Progress and handoff

<Last completed task, next ready task, deviations/blockers, final evidence.>
```

Status and evidence fields are execution records, not missing design. Repeat the task block for every implementation task with substantive behavioral changes and checks. Local coding choices may remain open without being listed as blockers. For unresolved design questions that depend on earlier findings, name the required evidence or predecessor and affected task. Do not defer architecture, shared protocol/state contracts, or ownership decisions that could invalidate earlier work. Plan length follows the necessary design content, not a target for brevity or a requirement to reproduce future source code.

During exploration, a bounded discovery task may record a question, relevant module or entry point, expected finding, and stopping condition. Mark the plan as an exploration draft while foundational decisions remain open. Continue authorized investigation and incorporate its findings; writing a discovery task is not completion of planning. If progress requires unavailable evidence or a user decision, report the concrete blocker and affected tasks rather than inventing contracts or calling the draft ready. Discovery alone does not require a commit.

## Readiness gate

Before implementation, check the plan against the request and inspected repository:

- Every requirement has a task and falsifiable acceptance check; no task adds unsupported scope.
- The overall design explains how the requested behavior works across components, including relevant failure paths; shared decisions are resolved rather than assigned to future implementation.
- Every implementation task identifies targets, behavioral changes, relevant contracts, and acceptance; remaining design dependencies are explicit, while routine coding choices remain with the implementer.
- Consequential maintenance trade-offs are addressed in the design without speculative abstractions or a separate maintenance workstream.
- Known paths, shared signatures, data shapes, dependencies, and commands agree across tasks; unresolved downstream details are explicit.
- The next ready task is concrete enough for a fresh session to execute without redesigning the feature.
- Checks confirm runnable code and requested functionality without speculative rare-case coverage; rollout/rollback procedures exist where the requested change needs them.
- No unresolved decision blocks the next task; unresolved later decisions are labeled and block their dependents.

Fix these deficiencies before claiming planning is complete or starting implementation. A fresh executor should be able to implement the next task and understand how later tasks integrate without redesigning the system or guessing material requirements. This is a content check, not a separate review pipeline or prose-polishing stage. Do not request permission already given. Plan-only requests end with a ready plan, or an explicitly incomplete draft and genuine blockers when further authorized investigation cannot resolve them; honor an explicit request for an outline or exploratory draft.

## Execute and resume

When a session handoff or context recovery is needed, keep a compact continuation record in the existing plan rather than creating another artifact. Retain the confirmed goal and authorization boundaries, relevant changed paths and diff references, checks and observed results, consequential hypotheses already ruled out with their reasons, blockers, and the next concrete action or acceptance check. Note later changes that may invalidate earlier evidence. Link to source or logs instead of copying full diffs, logs, or conversation history. Keep only information that changes how work resumes; ordinary uninterrupted tasks do not need a separate handoff exercise.

1. **Load and reconcile.** Read the plan, linked spec, applicable project instructions, current Git status/diff, and relevant Git history. Compare current code with completed task states. Reuse a valid existing plan. If it has drifted, repair the affected portion before acting; do not overwrite user work or blindly repeat completed tasks.
2. **Select one ready task.** Dependencies must be complete. Mark it `in_progress`. Execute sequentially in the main session by default. If delegation is authorized and useful, give a worker the task, constraints, exact owned files, dependencies, and acceptance checks; the main agent retains plan and integration ownership. Never run concurrent implementation tasks under this contract.
3. **Implement and verify.** Follow the concrete steps. Run the task's simple functional/runnability checks and record actual outcomes. When an intermediate coherent unit passes its check, inspect and commit it using steps 4–5 before continuing the remaining task steps; keep the task `in_progress`. Use a reproducer for a reported bug; a permanent regression test must separately earn its cost under `feedback.md`. Deep does not mandate TDD, new tests, or broader suites. Passing syntax alone cannot satisfy a behavioral requirement.
4. **Inspect the task diff.** Check scope, shared contracts, and obvious mistakes before committing. Fix concrete issues and rerun only affected checks. Do not dispatch a reviewer or perform a second audit by default; follow `workflow.md` when a separate review has a specific reason.
5. **Commit and continue.** Follow `commits.md`. Mark `done` only when task acceptance passes, known blocking issues are resolved, and the change is committed or an allowed no-commit exception applies. A failing or unavailable required check means `blocked`, not `done`. Keep task status current when it helps resumption. Do not create, amend, or delay a commit solely to update plan bookkeeping.
6. **Continue.** Take the next ready task without routine user confirmation. Repeat until the authorized scope is complete or no useful in-scope work remains.

On failure, use the diagnosis loop in `feedback.md`. A task can be `pending`, `in_progress`, `blocked`, or `done`; record the concrete blocker and next action. Do not proceed into dependent tasks on failed assumptions. Independent ready work may continue sequentially while a blocker is unresolved.

When evidence invalidates the design, update the affected decisions, tasks, and acceptance map first. Resolve routine implementation details from repository evidence. Ask only for a material scope/behavior decision or authority not already granted. Do not weaken acceptance to make a failing check pass.

## Integration acceptance and closeout

After task checks pass, confirm the assembled feature runs and meets the requested behavior with the planned minimal functional check. Reuse task evidence when it already proves that result; a separate integration suite or final audit is not required. Rerun checks only where later changes invalidate earlier evidence. Fix known issues and verify affected paths without adding speculative edge-case tests.

Close a persistent plan with observed results and any remaining limitation only when that record helps later work. Required acceptance still blocked means the work is incomplete, even if implementation commits exist. Do not make a closeout commit solely for plan bookkeeping. Report the result and a useful run/try command. Real user feedback can start the next iteration; do not preempt it with imagined scenarios. Do not claim review, test execution, or completion that did not occur.
