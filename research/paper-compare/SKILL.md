---
name: paper-compare
description: "Use when the user asks to compare several papers or methods side by side, choose between them, or build a comparison table: extract each method's setting, separate the authors' claims from their measured evidence and from your own inference, and flag metrics or datasets that are not actually comparable. Not for finding the papers (paper-search) or reading one paper closely (qi-read-paper)."
license: MIT
compatibility: Uses pdftotext or rga to extract numbers from PDFs. Retrieval follows the paper-search route when more papers are needed.
metadata:
  author: DengQi
---

# Compare methods without comparing apples to oranges

The output is one table plus the reasoning that fills it. The hard part is not the table; it is refusing to put two numbers in the same column when they were not measured the same way.

## 1. Fix the comparison question

Write down what the comparison is for: choosing a method, positioning a new one, or finding a gap. The purpose decides the rows. A comparison built to justify a choice keeps only the methods that could actually be chosen; one built to find a gap keeps the near-misses too.

## 2. Extract per method, in one pass each

For each paper, record the same fields, in the same order, so a missing field is visible rather than silently absent:

| Field | What to record |
| --- | --- |
| Setting | Task, input, output, assumptions |
| Method | The mechanism, in one or two sentences |
| Datasets | Name, version, split, size |
| Metrics | Name and exact definition |
| Baselines | What it was compared against |
| Compute | Hardware, budget, runtime if reported |
| Code | Repository, license, whether it runs |

Extract with `pdftotext -layout` and read the tables yourself; do not trust an extracted table's alignment. When a number is only in a figure, mark it as read from a figure.

## 3. Separate claim, evidence, and inference

Every cell carries one of three tags, and they never merge:

- **Claim** — the authors assert it in text.
- **Evidence** — a number the authors measured and reported.
- **Inference** — you concluded it. Say what from.

A claim without a matching number stays a claim. Do not upgrade it because two papers agree, and do not average numbers across different protocols.

## 4. Flag what is not comparable

Before drawing any conclusion, check these, and mark the cell `not comparable` rather than picking a winner:

- The metric name is the same but the protocol differs (mean vs median, p50 vs p99, per-query vs per-dataset).
- The dataset name is the same but the split, version, or preprocessing differs.
- The number is per-configuration, per-seed, or best-of-N, while another is a single run.
- One reports on the full test set and another on a subset.
- Different hardware or batch size makes a runtime comparison meaningless.
- A missing number is not a zero, and "not reported" is not "worse".

## 5. Write the table and the caveats

Put the table first, then the caveats that change how to read it, then the conclusion. Keep the tags in the table so a reader can see which cells are the authors' and which are yours.

```markdown
| Method | Setting | Dataset | Metric (def) | Reported | Tag | Compute | Code |
| --- | --- | --- | --- | --- | --- | --- | --- |
```

## Gotchas

- Two papers using "the same" dataset usually differ in split and preprocessing. Confirm from each paper, not from the dataset's homepage.
- A p99 and a mean under the same metric name are not comparable. Read the definition, not the name.
- The best number in a paper is often the best over several configurations. A single-run baseline is then not a fair comparison.
- A method's own paper reports its favorable baseline. Look for a third-party comparison before calling it state of the art.
- A runtime comparison across different hardware says nothing about the algorithm.
- An abstract-level comparison is a hypothesis. Verify each cell against the paper body before concluding.
- Do not fill a missing cell with an estimate. Leave it empty and say it was not reported.

## Report

State the comparison question, the methods included and why, the cells that are not comparable, and which conclusions rest on your inference rather than on reported evidence.
