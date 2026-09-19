# Deep: plan and execute

Read this for every confirmed Deep task. Keep the implementation narrow; make
its execution explicit. The harness is a concrete plan, runnable checkpoints,
and recorded progress, not exhaustive testing or review ceremony. This
contract is self-contained. Authorization follows `SKILL.md`.

## Build a plan another session can execute

Inspect the relevant source, callers, repository instructions, run/check
commands, and Git state before planning. Record only relevant pre-existing
changes needed to distinguish task work from user work. Verify referenced
paths and symbols; mark new paths as new. Do not invent repository facts or
commands.

Use one plan with these required parts for implementation work:

1. **Outcome and scope:** observable success, exclusions, and the request or
   spec being implemented.
2. **Design and constraints:** the current behavior and proposed change,
   affected components and their responsibilities, and the chosen approach
   with rationale for consequential trade-offs. Specify shared
   interface/data contracts and invariants. Where they determine
   correctness, describe data flow, state transitions and triggers, resource
   ownership/lifetime, limits and overflow behavior, and failure/recovery
   paths. Include rollout, compatibility, and rollback only when relevant.
   Separate resolved decisions from blocking unknowns; requirements such as
   "bounded queues" or "recover after failure" need concrete mechanisms, not
   just restatement.
3. **Acceptance map:** assign each required behavior or invariant an ID; map
   it to an owning task, simple verification procedure, and expected
   observable result. Confirm the code runs and the requested function
   works. Include failure behavior only for a reported bug, explicit
   requirement, or concrete reachable risk; do not invent rare scenarios to
   populate the map.
4. **Ordered tasks:** every task identifies an independently verifiable
   deliverable, affected modules or known files, the intended behavioral
   change and approach, dependencies/shared contracts, acceptance procedure
   and expected result, and intended commit boundary. Identify exact symbols
   only when they are a necessary integration point. The next task must be
   actionable without another system-design phase; it need not prescribe
   local coding steps. A task title and a promise to design it later are
   insufficient.
5. **Execution and progress:** how to resume, task states, completed
   evidence, blockers, and final integration checks.

Split tasks where one deliverable could be accepted while its neighbor is
rejected. Fold scaffolding, earned permanent tests, and documentation into
the behavior that needs them. Avoid whole layers such as "implement backend"
and trivial tasks such as "create empty file". If a task cannot be verified
or committed coherently without its successor, redraw the boundary or
explicitly group them into one verification/commit unit.

Task boundaries guide commits but do not impose a one-task/one-commit rule.
Commit independently useful verified stages as they become ready. Do not
duplicate Git history in the plan.

Order work toward the earliest useful runnable slice after a coherent design
for the requested scope. Resolve decisions that determine feasibility, task
boundaries, or shared contracts before calling the plan ready. Do not
front-load a test framework or speculative hardening. Give the user a
runnable entry point as soon as useful.

Describe each task through its target, approach, and observable result.
Specify shared data shapes or interface semantics where correctness depends
on them. Leave helper functions, local algorithms, and coding order to the
implementer. Do not include function bodies by default. "Add error
handling" or "write tests" without expected results is insufficient.

Record consequential maintenance trade-offs beside the relevant design
decisions. Do not add a separate maintenance essay.

For each check, supply cwd, command or procedure, input, and expected
outcome — not merely "exit 0". Prefer an existing run command. Unknown
commands or unresolved contracts block readiness; do not invent shell.

## Plan template

Replace the fields below with repository evidence. Omit irrelevant optional
fields; do not leave implementation-critical placeholders in a ready plan.

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

Status and evidence fields are execution records, not missing design. Repeat
the task block for every implementation task. Local coding choices may remain
open. Do not defer architecture, shared contracts, or ownership decisions
that could invalidate earlier work.

During exploration, a bounded discovery task may record a question, entry
point, expected finding, and stopping condition. Mark the plan as an
exploration draft while foundational decisions remain open. Writing a
discovery task is not completion of planning. If progress requires
unavailable evidence or a user decision, report the blocker. Discovery
alone does not require a commit.

## Ready-plan sample

Fill only fields the work needs. `deep-runnable-first` CSV import: no
rollout, no function bodies, a three-row map, first task already end-to-end.

```markdown
# Resumable CSV import

Plan readiness: ready.

## Outcome and scope

`import.csv` starts a job, writes rows, and resumes after interrupt from the
last durable checkpoint. Out of scope: concurrent writers, corruption
repair, a new test framework.

Existing changes: none.
Authorization: implementation.

## Design and constraints

Today the command writes every row in one process with no checkpoint.
Change: a job record plus `{job_id, source_path, row_offset}` written after
each successful batch commit. Resume opens the same file, skips to
`row_offset`, and continues. A crash between commit and checkpoint may
re-import one batch; duplicates are out of scope.

## Acceptance map

| ID | Behavior | Task | Check and expected result |
| --- | --- | --- | --- |
| A1 | Fresh import writes all fixture rows | T1 | `import.csv fixtures/small.csv` creates a job and 3 rows |
| A2 | Interrupt then resume continues | T1 | kill after row 1; resume writes remaining rows once |
| A3 | Completed job refuses a second resume | T2 | resume exits non-zero; data unchanged |

## Execution

### T1: End-to-end import and resume

Status: pending
Depends on: none
Acceptance: A1, A2
Targets: existing import command; job-state store (new checkpoint fields)
Contracts: checkpoint shape above

- [ ] Persist a checkpoint after each committed batch; resume skips to it.
- [ ] Verify at repo root: import the small fixture, interrupt, resume;
      expect 3 rows and no extras.
- [ ] Inspect the diff for scope.
- [ ] Commit the runnable import/resume slice.

### T2: Completed-job guard

Status: pending
Depends on: T1
Acceptance: A3
Targets: resume entry point
Contracts: completed jobs are immutable

- [ ] Resume of a completed job fails closed.
- [ ] Verify with the same fixture after a successful run.
- [ ] Commit the guard.

## Final acceptance

Import the small fixture, interrupt, resume, then confirm a second resume
is rejected. Reuse T1/T2 evidence.

## Progress and handoff

None yet.
```

## Readiness gate

Before implementation, check the plan against the request and inspected
repository:

- Every requirement has a task and falsifiable acceptance check; no task
  adds unsupported scope.
- The overall design explains how the requested behavior works across
  components, including relevant failure paths; shared decisions are
  resolved rather than assigned to future implementation.
- Every implementation task identifies targets, behavioral changes, relevant
  contracts, and acceptance; remaining design dependencies are explicit,
  while routine coding choices remain with the implementer.
- Consequential maintenance trade-offs are addressed in the design without
  speculative abstractions or a separate maintenance workstream.
- Known paths, shared signatures, data shapes, dependencies, and commands
  agree across tasks; unresolved downstream details are explicit.
- The next ready task is concrete enough for a fresh session to execute
  without redesigning the feature.
- Checks confirm runnable code and requested functionality without
  speculative rare-case coverage; rollout/rollback procedures exist where
  the requested change needs them.
- No unresolved decision blocks the next task; unresolved later decisions
  are labeled and block their dependents.

Fix these before claiming the plan is ready. A fresh executor should
implement the next task without redesigning the system. This is a content
check, not a review pipeline.

## Execute and resume

When a handoff is needed, keep a compact continuation in the existing plan:
goal, authorization, changed paths, checks, ruled-out hypotheses, blockers,
next action. Ordinary uninterrupted tasks do not need this.

1. **Load and reconcile.** Read the plan, spec, project instructions, and
   Git state. Repair drift; do not overwrite user work or repeat completed
   tasks.
2. **Select one ready task.** Dependencies complete. Mark `in_progress`.
   Execute sequentially. Never run concurrent implementation tasks.
3. **Implement and verify.** Run the task's functional checks and record
   outcomes. When an intermediate unit passes, inspect and commit it; keep
   the task `in_progress`. Keep a disposable reproducer in `/tmp` or an
   uncommitted local directory. A permanent regression test must earn its
   cost under `feedback.md` and then live with the project's existing tests.
   Passing syntax cannot satisfy a behavioral requirement.
4. **Inspect the task diff.** Check scope and contracts. Do not dispatch a
   reviewer by default.
5. **Commit and continue.** Follow `commits.md`. Mark `done` only when
   acceptance passes and the change is committed or an allowed no-commit
   exception applies. A failing required check means `blocked`.
6. **Continue.** Take the next ready task without routine confirmation.

On failure, use `feedback.md`. Do not proceed into dependents on failed
assumptions. When evidence invalidates the design, update decisions, tasks,
and acceptance first. Do not weaken acceptance to make a failing check pass.

## Integration acceptance and closeout

After task checks pass, confirm the assembled feature with the planned
minimal functional check. Reuse task evidence when it already proves that.
Required acceptance still blocked means the work is incomplete. Report the
result and a try command. Do not claim checks that did not occur.
