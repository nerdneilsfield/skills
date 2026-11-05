---
name: paper-reproduce
description: "Use when reproducing a paper's reported results or checking whether a claimed number holds: fix the target numbers and tolerances before running, run the authors' code or a baseline first, then attribute a mismatch to the method, the environment, or the setup rather than declaring the paper wrong. Not for implementing the method from scratch (paper-to-code) or for designing new experiments (algorithm-experiment)."
license: MIT
compatibility: Uses uv or the project's environment to build, hyperfine for timing, valgrind when the authors' code is C++. A GPU result is only comparable on the same precision mode.
metadata:
  author: DengQi
---

# Reproduce the claim, not the vibe

The output is a per-claim verdict with the number that was targeted, the number obtained, and the tolerance that decided it.

## 1. Write the targets before running anything

For each claim, extract the reported value, the exact metric definition, the dataset and split, and the configuration it was measured under. Fix the tolerance from the metric's own noise, not from how close you hope to get.

```markdown
| Claim | Metric (def) | Dataset/split | Reported | Tolerance | Verdict |
```

A claim with no reported number is not reproducible; record it as unquantified and move on.

## 2. Run the authors' code first

If code exists, run it unchanged on the reported configuration. A faithful run of the released code is the strongest available evidence about the environment, and it separates "the method is hard to reproduce" from "my reimplementation is wrong".

Record the exact commit, the environment, and the seed. Then run the baseline the paper compared against.

## 3. Measure speed claims under the paper's conditions

A speed or memory claim is a claim like any other, with its conditions as part of the target. Before running, record what the paper states, marking the rest `not reported`:

```markdown
| Claim | Value | Hardware | Input shape, batch | Precision | Threads | Scope | Warmup |
```

`Scope` says what the timer covers, such as inference only or the whole pipeline with loading and decoding. Then measure the same scope on the same shapes, batch, and precision, and record your own CPU and GPU models, library versions, and thread counts next to the result. Use `lscpu` for the CPU; repeat in fresh processes with `hyperfine --warmup 3 --runs 10 --export-json time.json '<cmd>'`, and report the median and spread.

On GPU code, wait for the device to finish inside the timed region, because a CPU timer otherwise measures submission (`torch.cuda.synchronize()` for PyTorch, and see `python-numerics` for others). Keep first-call compile and warmup apart from steady state.

On different hardware the absolute number cannot confirm or refute the claim. Run the paper's baseline on your machine, and compare the speedup ratio and how time grows with input size. Label the verdict `not comparable` when even that is unavailable. A speed claim also needs its accuracy: a faster run on a smaller input or at lower precision has not reproduced anything.

## 4. Attribute the mismatch

When a number does not match, classify before concluding:

| Symptom | Likely cause | Check |
| --- | --- | --- |
| Same code, same config, different number | Environment: BLAS, GPU, precision mode, library version | Pin versions, disable TF32/autotuning, rerun |
| Author code matches, your code does not | Your reimplementation | Diff against the deviation record from `paper-to-code` |
| Both off by a similar factor | Metric definition or split differs | Re-read the definition; check the data pipeline |
| Only one seed differs | Variance, not a bug | Rerun with several seeds |
| Crashes or diverges | Numerical instability or a missing guard | Reduce the step size, check for a zero denominator |

Do not report "the paper is wrong" until the environment and the metric definition have been ruled out.

## 5. Report per claim

State each claim separately. A method can reproduce one claim and fail another, and the failure is the useful part.

Never tune parameters until the number matches. That is fitting to the target, and it destroys the evidence. If a parameter must be swept, sweep it for the authors' code and your code alike, and report the sweep.

## Gotchas

- Fix the tolerance before running. A tolerance chosen after seeing the result is not a tolerance.
- The released code is often not the code that produced the paper's table. Check the commit date against the paper and say which you used.
- Floating-point differences from BLAS, GPU kernels, or reduced precision change the last digits. Compare at the reported precision, not bit-exactly.
- A single run of a stochastic method is not a reproduction. Run several seeds and report the spread.
- Reimplementation success does not validate the paper's claim; it validates your mapping. Keep the two verdicts separate.
- An unreleased dataset or a missing split makes a claim unreproducible, not false. Say which.
- A "failed" reproduction that traces to your environment is not a result about the paper. Report it as an environment gap.
- Timing and memory claims depend on hardware. Without comparable hardware, compare ratios to a baseline on one machine, and say so.
- "Real-time" and FPS claims often time one stage at one resolution with batching. Find what was timed before matching the number.

## Report

State the commit and environment used, each claim with its target, obtained value, and tolerance, the classification of every mismatch, and which claims remain unverified or unquantified.
