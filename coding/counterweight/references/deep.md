# Deep: plan and execute

Read this for every confirmed Deep task. Keep the implementation narrow; make its execution explicit. The harness is a concrete plan, runnable checkpoints, and recorded progress, not exhaustive testing or review ceremony. This contract is self-contained and does not require another workflow skill.

## Build a plan another session can execute

Inspect the relevant source, callers, repository instructions, run/check commands, and Git state before planning. Record only relevant pre-existing changes needed to distinguish task work from user work. Verify referenced paths and symbols; mark new paths as new. Do not invent repository facts or commands.

Use one plan with these required parts for implementation work:

1. **Outcome and scope:** observable success, exclusions, and the request or spec being implemented.
2. **Decisions and constraints:** the chosen approach, rationale for consequential trade-offs, exact interface/data contracts, and invariants. Include rollout, compatibility, and rollback only when relevant. Separate resolved decisions from blocking unknowns.
3. **Acceptance map:** assign each required behavior or invariant an ID; map it to an owning task, simple verification procedure, and expected observable result. Confirm the code runs and the requested function works. Include failure behavior only for a reported bug, explicit requirement, or concrete reachable risk; do not invent rare scenarios to populate the map.
4. **Ordered tasks:** one independently verifiable deliverable per task, dependencies, and intended commit boundary. Fully detail exact files/symbols, implementation steps, and checks for the next ready task; refine later tasks before executing them.
5. **Execution and progress:** how to resume, task states, completed evidence, blockers, and final integration checks.

Split tasks where one deliverable could be accepted while its neighbor is rejected. Fold scaffolding, tests, and documentation into the behavior that needs them. Avoid whole layers such as "implement backend" and trivial tasks such as "create empty file". If a task cannot be verified or committed coherently without its successor, redraw the boundary or explicitly group them into one verification/commit unit.

Task boundaries guide commits but do not impose a one-task/one-commit rule. Apply `commits.md` throughout execution: commit independently useful, verified intermediate stages within a task as they become ready. Do not wait for the whole task or plan to finish, and do not duplicate Git history in the plan.

Order work toward the earliest useful runnable slice. Prefer one thin end-to-end path before optional refinements; do not front-load a test framework, speculative hardening, or generalized infrastructure. Complete the user's requested scope, but do not append hypothetical follow-up work. Give the user a runnable entry point as soon as useful; continue already-authorized work without waiting unless their feedback is needed for a material decision.

Each step must identify an action, target, and result. Specify exact signatures, data shapes, algorithms, or pseudocode where they determine correctness or task coordination; do not copy entire future source files just to lengthen the plan. "Add error handling", "write tests", and "ensure compatibility" without concrete cases and expected behavior are not executable steps.

For each check, supply a working directory, command or precise manual procedure, necessary input/setup, and expected outcome. State what confirms the requested behavior, not merely "exit 0". Prefer an existing run command with a simple input/output example; reuse focused tests when useful, without requiring new test code. If an environment is unavailable, state what cannot yet be verified and how to obtain that evidence. Unknown commands or unresolved contracts block readiness for affected tasks; do not fill gaps with plausible-looking shell commands.

## Plan template

Replace the fields below with repository evidence. Omit irrelevant optional fields; do not leave implementation-critical placeholders in a ready plan.

```markdown
# <Topic> implementation plan

## Outcome and scope

<Requested behavior, exclusions, spec link if one exists.>
Existing changes: <relevant paths and ownership, or none>.
Authorization: <implementation / plan-only; material approvals still needed>.

## Decisions and constraints

<Resolved approach, boundary contracts, invariants, consequential trade-offs.>
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
Files: <Create/Modify/Test: exact paths and relevant symbols>
Contracts: <inputs/outputs shared with other tasks, where relevant>

- [ ] <Concrete implementation step with target and expected behavior.>
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

Status and evidence fields are execution records, not missing design. Fully specify the next ready task's targets, contracts, and acceptance procedure. Later tasks must have an outcome, dependencies, and acceptance intent; mark details that depend on earlier results and resolve them before those tasks start. Do not investigate every downstream detail before delivering the first runnable slice.

When an unknown prevents a later task from becoming ready, allow a bounded discovery task: name the question, relevant module or entry point, expected finding, and stopping condition. Its deliverable is enough evidence to specify the dependent task, not a repository-wide survey. Discovery alone does not require a commit.

## Readiness gate

Before implementation, check the plan against the request and inspected repository:

- Every requirement has a task and falsifiable acceptance check; no task adds unsupported scope.
- Known paths, shared signatures, data shapes, dependencies, and commands agree across tasks; unresolved downstream details are explicit.
- The next ready task is concrete enough for a fresh session to execute without redesigning the feature.
- Checks confirm runnable code and requested functionality without speculative rare-case coverage; rollout/rollback procedures exist where the requested change needs them.
- No unresolved decision blocks the next task; unresolved later decisions are labeled and block their dependents.

Fix execution-blocking deficiencies before execution. This is a short self-check, not another planning/review phase; sufficient means the next task can be implemented and its result checked without guessing material requirements. Do not polish the plan for its own sake or request permission already given. Plan-only requests end with the plan and any genuine open decisions.

## Execute and resume

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
