---
name: eval-plan
description: "Run when the user explicitly asks to plan a model-backed eval: preregister bars, arms, decoys, and stop rules, dry-run at zero cost, price a small pilot, and get approval before the full run, with results beside a no-skill arm. Not for deterministic tests, which run without a model."
license: MIT
compatibility: Works with whatever runs the eval; in this repository the harnesses under evals/. Needs a way to read each call's real cost or to declare it unknown.
metadata:
  author: DengQi
disable-model-invocation: true
---

# Preregister a paid eval, then earn the full run

Four gates stand before the first full-run call, in order: a frozen preregistration, a dry run that spends nothing, a priced pilot, and a person's approval. Each writes a file in the eval's output directory, so a later reader can see what was decided before the numbers existed.

## Boundaries

- Spend nothing before the pilot, and in the pilot only what the cap admits. Do not split calls or retry to fit under the cap.
- A bar, arm, decoy, or stop rule changed after the first priced call is a new eval with a new preregistration. Say so; do not edit the old one.
- Held-out sets are never read, pasted into a prompt, or summarized during planning. The dry run uses development rows only.
- An agent never approves its own full run. Unattended, write the approval request to a file and stop.

## 1. Preregister

Write `prereg.md`. Every section is required, and a template comment does not count as content.

| Section | Holds |
| --- | --- |
| Decision | What this eval decides, and what each outcome will make you do |
| Bars | Per metric: name, pass bar, direction, what a miss means |
| Arms | Per arm: model, skill revision or loadout, settings, estimated cost per item |
| No-skill arm | Same model, same rows, same tools, task text only, no skills installed |
| Decoys | Inputs the scorer must reject or score low: how many, how made, what a decoy pass proves |
| Scoring | Scorer or judge, its own bar on decoys, trial count per item |
| Stop rules | Spend cap, a bar missed in the pilot, a scorer below its bar, the first quota or rate-limit error on a metered seat |
| Held-out exposure | Each held-out set touched, and which earlier runs have already seen it |

Commit or otherwise date the file before any priced call, so "decided first" can be checked.

**Blinding.** A candidate that can tell it is being graded behaves differently, and a judge that knows the arm grades the label. Nothing the candidate sees says eval, test, judge, benchmark, or arm, unless the task itself is about a project's tests. Make the fixture look like a project, not `case-7/`. Show the judge neutral labels and the files the transcript shows were opened, never the candidate's own account of what it read.

## 2. Dry-run at zero cost

Run the real pipeline on the real development rows with a stub in place of the model. If the harness has no stub mode, add the smallest one, or run with a fake `claude` first on `PATH` that returns a canned reply in the expected format. Pass only when:

- Every row has the required fields, and the row count matches the plan.
- Every arm has a current price, read from the provider's page today, or is declared seat-metered.
- The output budget leaves room for the answer after any reasoning.
- The exact text sent on a retry is written down. A retry with no new text repeats the failure at the same price.
- The largest single call fits under the cap.
- The scorer passes its own check on decoys and on a known-good answer, using the stub output.

Write `dry-run.md` with those results. A failed dry run blocks the pilot; fix the rows or pipeline, not the bars.

## 3. Priced pilot

Run about three items per arm, chosen before seeing results. Settle every call in `spend.md` with the provider's actual cost, or `unknown` when a seat or CLI hides it:

```markdown
| Attempt | Arm | Item | Reserved | Actual | Result |
```

Admit a call only when `spent + reserved + unknown charges + estimate <= cap`. Then compute per arm the mean cost per item, its spread, and a projection to the full item count with a band. Three items give a rough band, so state it as one. Stop and report, without asking for approval, when a bar failed, the projection exceeds the cap, or a stop rule fired.

## 4. Ask for approval

Show, in this order and nothing before it: the projection, the spend table, pilot results per bar, and the stop rules. Then ask one question:

- A) Run the full set at the projected cost (recommended only when within the cap).
- B) Cut arms or items, and recompute first.
- C) Stop here and keep the pilot as the record.

An approval covers that item count, those arms, and that cap, and nothing wider. The full run keeps settling in `spend.md` and stops at the cap.

## 5. Report beside the no-skill arm

Write `results.md` with one row per arm, each no-skill row beside its skill rows, and the bars as the header. Report the difference from no-skill, the spread across trials, decoy results, and spend. A row with no no-skill comparison does not leave the run. An arm that read a skill file it should not have is contaminated and gets no credit; read the transcript to check.

## Gotchas

- Tuning descriptions against every query you later report leaves no holdout. Name the exposure each time.
- Pilot cost understates cost when items vary in size. Choose pilot items across the size range.
- A CLI's reported cost can be an estimate, and cache writes or tool fees may be excluded. Reconcile against usage when the number decides anything.
- Models and prices change. Read them on the day; do not copy a table from an old report.
- A decoy the scorer passes means the scorer is broken, and every other number with it.
- Two arms differing in prompt text as well as the skill are not measuring the skill.
- Changing transport mid-run, such as a proxy to direct, changes the arm. Record it, and do not pool across it.

## Report

State the preregistration path and date, dry-run result, pilot spend and projection, who approved what, the results table with the no-skill rows, and anything unverified or contaminated.
