---
name: counterweight
version: 0.6.0
description: "Run when the user asks to implement, fix, refactor, wire configuration, add a feature, or debug code, including when that request would otherwise grow a plan, framework, compatibility layer, retry, cache, fallback, or unearned test suite. Pick the lightest sufficient process and keep the change proportional to current evidence and risk. Not for questions about existing code, standalone review, prose, root AGENTS.md setup (counterweight-setup), or a post-implementation cut list (counterweight-cut)."
---

# Counterweight

Deliver the requested behavior as useful, runnable software. This is the implementation workflow. Writing or repairing the root `AGENTS.md` is `counterweight-setup`. A cut list after the diff exists is `counterweight-cut`. Questions about existing code, standalone review, and prose stay outside this skill.

Workflow track, reasoning effort, authorization, and review are separate.

## Restraint

> Process must earn execution. Complexity must earn implementation. Tests must
> earn maintenance. Knowledge must earn persistence.

Do not simplify away real security, accessibility, data-loss, or trust-boundary
requirements.

Existing code is not by itself a compatibility commitment. Change task-local or
unreleased interfaces with their local callers unless evidence identifies a
published contract, independently deployed consumers, data that must be
preserved, or an explicit user requirement. Preserve those obligations even for
unreleased code.

Ask only when an unresolved choice materially changes the result. Discover facts
from code, project files, Git, and relevant documentation.

## Implementation ladder

Before writing new code, walk this in order and stop at the first level that
satisfies the current requirement:

1. Does this need to exist at all? — name the requirement, reachable caller,
   observed failure, trust boundary, or platform constraint that demands it.
2. Existing repository capability.
3. Standard library.
4. Platform or framework native behavior.
5. An already-installed dependency.
6. The smallest new code that works.

Future possibility, elegance, generality, completeness, and unspecified
robustness do not move you down a level.

## Calibration

- "Add caching to compute()" + compute is pure → `functools.lru_cache` or the
  repository's equivalent. Not a CacheManager, provider interface, or config knob.
- "Parse the generated metadata file" + generator and consumer share one current
  schema → implement that schema path only. No checksum, fallback parser, or
  future-version layer.
- "Pass region to the SDK constructor" + the repository already validates config
  parsing and has a smoke path → use them. No field-exists or mock-call-count test.
- "Add retry to this call" + logs show it really fails several times a day →
  the retry is earned. Restraint is not a reason to skip it.

## Track selection

| Signal | Track |
| --- | --- |
| You can name the files and the correct edit before reading further | Direct |
| Edits are clear but dependent; wrong order drops one | Managed |
| An unresolved system decision remains: public interface, migration, concurrency, data consistency, security boundary, large refactor | Deep |

When two tracks both seem to fit, take the lighter one and escalate on new
evidence. Prior work or an existing plan never justifies keeping the heavier
track.

Obligations:

- **Direct** — No coordination step, plan, design, subagent, review, or new
  permanent test by default. Feedback is the cheapest existing check that
  supports completion.
- **Managed** — Identify order and integration points before editing; write
  one light plan only when recording that coordination materially helps.
  Verify the affected integration points. Do not inherit Deep's design gate.
- **Deep** — Read [references/workflow.md](references/workflow.md) and
  [references/deep.md](references/deep.md). Resolve material decisions and
  execute when authorized. The plan must explain design, contracts, and
  acceptance; not function bodies.

Before editing, name the observable result that means done and the smallest
check that can establish it. Build success alone does not prove a runtime fix.

## Authorization

| Situation | Rule |
| --- | --- |
| Analysis, review, or plan-only request | Inspect and report; do not modify files |
| Authorization already given in this conversation | Carry it forward; do not ask again |
| A plan now exists | Not a new gate, and not a cancellation of existing authorization |
| Local commit authorized | Never implies push, PR, merge, or release |

An explicit user instruction about process weight overrides track defaults. If
the user asks for a plan, TDD, full test coverage, an ADR, or a review, provide
it. Restraint never overrides an explicit request.

Do not infer a new gate from optional skill guidance.

## Verification

Start with the smallest check that can support the claim:

- Feature: run a representative input through the changed path, inspect the result.
- Bug: run the reported reproducer, confirm the symptom is gone.
- Build/import: compile, typecheck, or load the affected entry point.
- Text/config: inspect the diff or run the relevant parser/config check.

Add a second check only for a separate explicit requirement, a real safety
boundary, or a mandatory repository gate. Fresh evidence must match the claim:
a parser check cannot prove runtime behavior.

Write a test into the repository only when it earns future maintenance, and then
with extreme restraint. Put session-only scripts, fixtures, and reproducers in
`/tmp` or one uncommitted local directory, never under `tests/`.

Read [references/feedback.md](references/feedback.md) when considering a
permanent test, or when diagnosing a failure whose cause is unclear.

## Commits

For authorized implementation in a Git repository, all tracks share one policy:

- Group by task intent, dependency, and review/rollback boundary — not by track,
  file type, or Conventional Commit type.
- Stage named paths or hunks only. Never `git add .`, `git add -A`, or
  `git commit -am`. Preserve unrelated user changes.
- Commit each coherent unit as soon as its check passes, including useful
  intermediate stages. Do not accumulate until the request is finished.
- Local commits only. Push, PR, merge, and release each need separate authorization.

Before committing, drop new abstractions, dependencies, config, permanent tests,
or docs that lack a current caller, observed failure, or explicit request. Do
not open a review round.

Read [references/commits.md](references/commits.md) when grouping is non-obvious,
unrelated changes are already staged, or a hook or commit fails.

## Scope

When the repository has `.cw/goal.md`, treat it as the bound on this task: do
the work inside it and do not widen it. It is the user's words, not a spec to
elaborate. Do not edit the file. A goal that is absent changes nothing.

## Maintainability

A later reader with no chat history should find entry points, follow existing
style, and verify further changes from the repository. Update existing
guidance when the task changes how to continue.

Prefer low-latency tools. Prefer a host Git wrapper for status and diffs.
Read [references/subagents.md](references/subagents.md) only when delegation
has a concrete isolation or parallel-work benefit. Read
[references/roles.md](references/roles.md) and
[references/hosts.md](references/hosts.md) only when the user or the project
config asks for a review, over-review, historian, or planner run.

## What the user sees

| Report | Do not report |
| --- | --- |
| What changed | Phase or track names |
| The check that was run and its actual result | Tool-by-tool narration |
| Commit subjects, or the concrete reason nothing was committed | Repeated plans |
| Real blockers and limits | Invented follow-up work |
| A non-obvious omission and its one-clause reason | Unverified success claims |

## Finish

Stop when the requested behavior works, the necessary check passed, and the
commit disposition is resolved. Perform Deep's planned functional acceptance.
Do not add an audit, adjacent refactor, or roadmap without a current reason.

If the task proved a durable, reusable, non-obvious project fact, add one or
two lines to the narrowest existing `AGENTS.md`. Record current truth, not a
task recap. The usual result is no change.

Stay in this skill for the implementation. Hand off when the user or a finding
calls for it: `grill-me` to grill the plan, `counterweight-cut` to delete or
simplify this diff, and `project-learning` to record a project fact beyond the
one or two `AGENTS.md` lines above. After Deep work that added an abstraction, dependency, test file, or
compatibility layer, ask once whether to run `counterweight-cut`. Do not start
it unasked. Direct and small Managed work do not mention cut. If the named
skill is not installed, name it and continue this skill.
