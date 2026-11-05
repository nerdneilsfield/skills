---
name: algorithm-design
description: "Use when designing a new method or algorithm from a problem statement: enumerate candidate approaches, analyze complexity and failure modes, start from the simplest baseline, and decide when to stop adding components. Not for running the comparison experiments (algorithm-experiment) or for writing the paper's related work (research-report)."
license: MIT
metadata:
  author: DengQi
---

# Design the simplest thing that could work

The output is a short list of candidates, one chosen baseline, and the reason the extra machinery is or is not justified. Most designs should end at the baseline.

## 1. State the problem before the method

Write the input, the output, the constraint that makes the problem hard, and what "solved" means. A method proposed before the constraint is named is usually solving a different problem.

## 2. Find the simplest baseline

The baseline is the smallest method that could plausibly work: the trivial algorithm, the standard method, or the current practice. Build and measure it before designing anything larger. Every added component must beat the baseline by more than the noise, or it is not earning its place.

If the baseline already meets the requirement, stop. That is a result.

## 3. Enumerate candidates

List three to five distinct approaches, each in one or two sentences, and for each:

- The core mechanism, and why it could work.
- The assumption it depends on, and what breaks if the assumption fails.
- The complexity in time and memory, with the variable that actually grows.
- The failure modes: degenerate inputs, scale, non-finite values, ties, empty input.
- The evidence that would distinguish it from the baseline.

Prefer candidates that differ in mechanism, not in tuning. Before building one, use `research-hypothesis` to write what it predicts that the baseline does not, so that the measurement can tell them apart.

## 4. Complexity and failure analysis

State complexity in terms of the quantity that grows with the problem, not a vague "it is fast". Check the constants that matter at the real scale: a method with a better asymptotic bound can lose at the sizes you actually run.

For each candidate, name the input that makes it fail, and say whether that input can occur. A method that fails only on inputs the problem forbids is fine; one that fails on a plausible input is not.

## 5. Decide when to stop adding components

Add a component only when the current version's measured failure justifies it. After each addition, re-measure against the same baseline and the same metric. Stop when:

- The requirement is met within tolerance.
- The next component's expected gain is smaller than the measurement noise.
- The added complexity brings a failure mode the problem cannot tolerate.

Prefer removing a component that does not move the metric over tuning the ones that remain.

## Gotchas

- A method with no baseline is uninterpretable. "It works" is not evidence until something simpler has been measured.
- Complexity is a claim about a variable. Say which variable, or the comparison is meaningless.
- A component that improves one metric and worsens another has not obviously helped. State the trade.
- Tuning the baseline to be worse is not a comparison. Give the baseline the same search budget as the proposal.
- The mechanism that helps at small scale often stops helping at large scale, and vice versa. Check the scale you will actually run.
- A design that needs a hyperparameter per dataset has moved the problem, not solved it.
- Elegance is not evidence. If a simpler candidate matches the complex one, choose the simpler one.
- Do not add a component for a future requirement that is not in the problem statement.

## Report

State the problem and constraint, the baseline and its measurement, the candidates considered with their complexity and failure modes, the chosen design, and the evidence that justifies each component beyond the baseline.
