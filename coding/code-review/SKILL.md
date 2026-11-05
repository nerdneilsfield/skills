---
name: code-review
description: "Use when reviewing a change against a fixed baseline: check it along two separate lines, the repository's own standards and the spec or request it implements, and report only problems where you can state a concrete failing scenario. Not for reviewing your own just-written diff, or for a design-level critique of a module (codebase-design)."
license: MIT
compatibility: Uses git and gh; the diff must exist locally or be fetchable from the host.
metadata:
  author: DengQi
---

# Review the change, on two lines

The output is two lists of findings plus the baseline they were computed against. A finding you cannot turn into a failing scenario is an opinion, and does not belong.

## 1. Pin the baseline first

Ask for the baseline commit, branch, or tag if it was not given. Then capture the diff once, against the merge base:

```sh
git rev-parse <baseline>
git diff <baseline>...HEAD
git log <baseline>..HEAD --oneline
```

A bad ref or an empty diff fails here, before any reading. For a hosted review, `gh pr diff <n>` gives the same content.

## 2. Line 1: does it follow this repository's standards?

Read the repository's own documents first: `CONTRIBUTING.md`, `AGENTS.md`, style guides, and the linter and formatter configuration. The linter already enforces what it enforces; do not report what it would have caught.

Report a standards finding only when you can cite the standard and quote the code. Where the repository is silent, a convention shared by the surrounding code is the standard.

## 3. Line 2: does it do what was asked?

Find the source of truth for the request: the issue, the spec, the message. Then check three things:

- **Missing** — the request asked for something the diff does not implement.
- **Extra** — the diff does something the request did not ask for.
- **Wrong** — the diff looks implemented but the behavior is not what the request describes.

Quote the request line for each finding.

## 4. Report only falsifiable problems

For each finding, state the input or the sequence that makes it fail, and what happens instead. If you cannot construct that, drop the finding or move it to a separate "questions" list.

Rank by consequence: data loss, security, correctness, then everything else. A test or grader weakened to make the diff pass is a finding on its own.

## 5. Keep the two lines separate

Present the standards findings and the spec findings under their own headings, and do not pick a single winner across them. A change can follow every standard and implement the wrong thing, or do exactly what was asked and break the repository's conventions.

## Gotchas

- Without a baseline, the review has no boundary. Ask for it rather than reviewing `HEAD`.
- A finding with no failing scenario is a style preference. Say so, or leave it out.
- The linter's own findings are not review findings. Read the config before repeating them.
- Do not rewrite the diff while reviewing it; report the problem and let the author fix it.
- A passing test suite does not mean the request was implemented. Check the request separately.
- A test weakened, skipped, or made tolerant to get a green run is a finding, not a detail.
- Do not rerank across the two lines. The separation exists so one line cannot hide the other.
- A large diff is reviewed by sampling: the entry points, the risky paths, and the tests, then the rest.

## Report

State the baseline and the diff command, the standards sources read, the findings per line with their failing scenario and severity, and any request requirement you could not verify.
