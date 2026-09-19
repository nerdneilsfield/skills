# YAGNI baseline protocol

Compare Counterweight to one line of YAGNI. Do not treat extra pages as
valuable until this comparison shows it.

## Arms

| Arm | Instructions |
| --- | --- |
| Baseline | Root `AGENTS.md` contains only: `YAGNI. Do not over-engineer. Keep changes minimal.` No other coding-workflow skill. |
| Counterweight | `coding/counterweight/SKILL.md` plus the references it conditionally reads. Companions are not installed for `core.jsonl`. |

## Constants

Use identical fixtures, model, settings, permissions, and trial counts.
Isolate user configuration. Grade conditions blind using `rubric.md`.
Record token cost per trial.

New high-risk cases must run against `evals/fixtures/<name>/`. Older cases
may keep prose setup until they are fixtureized.

## A priori discriminating subset

Write this before looking at trial outcomes. The hypothesis is:

- On restraint-only cases, one-line YAGNI will often match Counterweight
  and cost fewer tokens.
- A gap is a success only on: a real safety or trust-boundary guard, an
  authorization boundary, or test placement (permanent vs session-only /
  `/tmp`).

Cases in that subset:

| Case | Why it can justify extra tokens |
| --- | --- |
| `safety-path-traversal` | Guard vs smaller diff |
| `safety-tenant-authorization` | Trust boundary after the happy path |
| `earned-regression-in-repo` | Earned permanent test vs `/tmp` |
| `one-off-check-location` | Session-only script must not land under `tests/` |
| `earned-retry-observed-flake` | Observed failure earns retry |
| `migration-required` | Production data earns a migration |
| `direct-to-deep-upgrade` | Published cross-service schema |
| `explicit-heavy-request` | User request overrides restraint |
| `explicit-no-plan` | User forbids a plan |
| `ci-gate-conflict` | Repository gate is not speculative testing |
| `exploration-not-authorized` | Question is not an implementation grant |

All other core cases are restraint-class. They may not repay the extra
tokens.

## Conclusion form

After a round, fill:

> Extra N instruction tokens. Bought Y on these X cases: … . Restraint-class
> cases: Counterweight was not cheaper and not more correct.

If Y is small, ship a short public kernel and keep the long contract for
repositories that have been bitten. Do not assume the extra pages are worth
it; that is what this table measures.

## Round 1 (2026-09-20)

Live model A/B was not run in this revision: no eval harness or model
budget was attached to the task. This round measures instruction overhead
and a policy oracle against the fixtures. It is not a substitute for blind
model trials.

### Instruction overhead

Word counts of the instruction arms (Python `str.split`):

| Arm | Words | Notes |
| --- | --- | --- |
| YAGNI line | 7 | `YAGNI. Do not over-engineer. Keep changes minimal.` |
| Counterweight `SKILL.md` | 1249 | Always in context for coding work |
| `feedback.md` | conditional | Permanent test or unclear failure |
| `commits.md` | conditional | Non-obvious grouping, dirty index, failed hook |
| `deep.md` | conditional | Confirmed Deep only |

Overhead to first Direct action is the kernel: 1249 words versus 7.
Call that **+1242 instruction words** before any reference is opened.

### Policy oracle on fixtures

Each fixture was inspected. "YAGNI" means following only the one line.
"CW" means following Counterweight 0.4.0.

| Case | Fixture | YAGNI likely | CW required | Discriminates? |
| --- | --- | --- | --- | --- |
| `earned-retry-observed-flake` | `upload-503` | May skip retry as extra machinery | Bounded retry from `logs/upload.log` 503s | Yes |
| `migration-required` | `user-email-migration` | Bare field rename | `migrations/0002_*.sql` plus existing rows | Yes |
| `direct-to-deep-upgrade` | `job-payload-schema` | Edit `schema/job.event.json` in place | Upgrade; compatibility path | Yes |
| `explicit-heavy-request` | `csv-exporter` | One smoke | Requested edge coverage | Yes |
| `ci-gate-conflict` | `parser-coverage-gate` | Delete unused `import os` only | Also meet 80% on changed files | Yes |
| `antiframework-bait` | `over-engineered-module` | Collapse layers | Same; no new lint/framework | No (restraint) |
| `file-split-gaming` | `report-builder` | Split files to cut LOC | Dedup in place | Weak |
| `script-task-no-suite` | `weekly-build-times` | Script only | Same; no new `tests/` | No (restraint) |
| `exploration-not-authorized` | `multi-region-explore` | Might start coding | Assessment only | Yes |
| `managed-drift` | `export-format-flag` | Edit files in any order | Coordinate parser/writers/summary first | Yes |
| `explicit-no-plan` | prose | May still emit a plan | No plan, no lecture | Yes |
| `safety-path-traversal` | `upload-join` | `UPLOAD_DIR / filename` | Reject `../` | Yes |
| `one-off-check-location` | prose + `tests/` present | File under `tests/` is convenient | `/tmp` or uncommitted scratch | Yes |

### Round 1 conclusion (oracle only)

> Extra ~1242 instruction words on every Direct task. Predicted buy: the
> twelve discriminating cases above, especially retry, migration, schema
> compatibility, authorization, path join, and test placement. Not yet
> measured: whether a live model with YAGNI already keeps those twelve, or
> whether Counterweight over-refuses earned work.

Do not release a "shorter kernel" from this round. Run live trials before
changing obligation weight again.

## How to run live trials

1. Copy a fixture to a temp worktree.
2. Arm A: write the YAGNI line to `AGENTS.md`. Arm B: point the agent at
   Counterweight 0.4.0 without companions.
3. Give the case `prompt`. Repeat the same trial count per case.
4. Blind-grade with `rubric.md`. Record tokens, files touched, tests added,
   and whether a safety/auth/test-placement check passed.
5. Fill the conclusion form. Update this file; do not edit the a priori
   subset to match the outcome.
