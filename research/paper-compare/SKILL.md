---
name: paper-compare
description: "Use when the user asks to compare several or many papers or methods side by side, choose between them, or build a comparison table: extract each paper into its own file first, record evidence before judging it, keep not reported apart from not done, separate the authors' claims from your inference, and flag overlapping datasets and metrics that are not actually comparable. Not for finding the papers (paper-search) or reading one paper closely (qi-read-paper)."
license: MIT
compatibility: Uses pdftotext or rga to extract numbers from PDFs. Retrieval follows the paper-search route when more papers are needed.
metadata:
  author: DengQi
---

# Compare methods without comparing apples to oranges

The output is one extraction file per paper, then one table plus the reasoning that fills it. The hard part is not the table; it is refusing to put two numbers in the same column when they were not measured the same way.

## 1. Fix the comparison question

Write down what the comparison is for: choosing a method, positioning a new one, or finding a gap. The purpose decides the rows. A comparison built to justify a choice keeps only the methods that could actually be chosen; one built to find a gap keeps the near-misses too. Fix the fields and the outcome you care about before opening the papers, so that the extraction does not bend toward the first paper read.

## 2. Extract each paper into its own file, before any synthesis

One file per paper, `compare/<key>.md`, same fields in the same order, and nothing about the other papers. Do this for two papers as well as for thirty. Finish every file before writing a single comparative sentence. With many papers, give each one a separate pass or agent (brief through `agent-brief`), find local files through `paper-library`, and resume from the files after any interruption.

| Field | What to record |
| --- | --- |
| Identity | Title, version read (preprint or journal), errata, authors' group |
| Setting | Task, input, output, assumptions |
| Method | The mechanism, in one or two sentences |
| Datasets | Name, version, split, size, preprocessing |
| Metrics | Name and exact definition |
| Results | The number, its uncertainty, seeds or runs, and how it was selected |
| Baselines | What it was compared against, and who ran them |
| Compute | Hardware, input shapes, batch, precision, runtime |
| Code | Repository, license, whether it runs |

Every value carries a locator (`p.6 Table 2`) and one status:

| Status | Meaning |
| --- | --- |
| `reported` | The paper states it; give the value |
| `not reported` | Searched the paper and supplement, and found nothing. Says nothing about what was done |
| `not done` | The paper says it was omitted, or its procedure excludes it |
| `not available` | You could not access the source, such as a missing supplement. Name it |
| `n/a` | The field does not apply |

Silence is `not reported`, never `not done`. If the text and code disagree, record both.

Extract with `pdftotext` to a file and read tables with `-layout`; do not trust an extracted table's alignment, and check key numbers against the rendered page. When a number is only in a figure, mark it as read from a figure.

The extraction holds what the paper says, not what you think of it. Put judgments in a separate `## Concerns` section of the same file, written last, each with the locator, what you saw, and what it means for which result. Judge results, not papers: one paper can have a sound accuracy result and an unsound runtime result.

## 3. Audit the extraction

Before synthesis, recheck a sample of cells against the source: all headline numbers, and a few others per file. An extraction agent's errors look exactly like its correct cells, so accept the files through `agent-verify`.

## 4. Separate claim, evidence, and inference

Tag every statement that goes into the comparison:

- **Claim** — the authors say it. Quote or paraphrase, and say where.
- **Evidence** — a number the authors measured and reported.
- **Inference** — you concluded it. Say what from.

A claim without a matching number stays a claim. Do not upgrade it because two papers agree, and do not average numbers across different protocols.

## 5. Flag what is not comparable or not independent

Before drawing any conclusion, check these, and mark the cell `not comparable` rather than picking a winner:

- The metric name is the same but the protocol differs (mean vs median, p50 vs p99, per-query vs per-dataset).
- The dataset name is the same but the split, version, or preprocessing differs.
- The number is per-configuration, per-seed, or best-of-N, while another is a single run.
- One reports on the full test set and another on a subset.
- Different hardware or batch size makes a runtime comparison meaningless.
- A missing number is not a zero, and "not reported" is not "worse".

Then map overlap. Agreement counts as replication only when the data, code, and authors are independent:

- Preprint, journal, and extended versions are one study with several reports. Count one, and say which report gives which number.
- Papers sharing a dataset or test split are not independent evidence. A benchmark reused by a whole field has been selected on repeatedly, so its best scores run high.
- Papers sharing a codebase, a pretrained backbone, or a group can share a bug.

## 6. Write the table and the caveats

Synthesize only from the extraction files, and go back to a file rather than to memory. Organize the reasoning by question or outcome, not paper by paper. Put the table first, then the caveats that change how to read it, then the conclusion. Keep the tags and locators in the table so a reader can see which cells are the authors' and which are yours.

```markdown
| Method | Setting | Dataset | Metric (def) | Reported | Status | Tag | Where | Compute | Code |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
```

Do not total checklist items into a quality score. A paper that reports everything may still be wrong, and a terse one may be sound: reporting completeness, risk of bias, and how far the evidence supports a claim are different questions. Give the reasons per concern instead of a number.

## Gotchas

- Two papers using "the same" dataset usually differ in split and preprocessing. Confirm from each paper, not from the dataset's homepage.
- A p99 and a mean under the same metric name are not comparable. Read the definition, not the name.
- The best number in a paper is often the best over several configurations. A single-run baseline is then not a fair comparison.
- A method's own paper reports its favorable baseline. Look for a third-party comparison before calling it state of the art.
- A baseline number copied from an earlier paper was not run under the new paper's conditions, even inside one table.
- A runtime comparison across different hardware says nothing about the algorithm.
- An abstract-level comparison is a hypothesis. Verify each cell against the paper body before concluding.
- Do not fill a missing cell with an estimate. Leave it `not reported`.
- A DOI that resolves is not support for a claim. Check the paper says it, and look for an erratum or retraction before leaning on it.
- Reading the favorite paper first sets its fields as the template. Fix the fields in step 1.

## Report

State the comparison question, the methods included and why, where the extraction files are and how they were audited, the cells that are not comparable, the overlap among datasets and reports, and which conclusions rest on your inference rather than on reported evidence.
