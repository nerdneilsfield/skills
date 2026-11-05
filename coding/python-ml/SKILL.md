---
name: python-ml
description: "Use when the user asks to build, evaluate, debug, or speed up a classical ML or deep-learning training or inference pipeline: leakage, misleading splits, unstable training, slow data loading, GPU out-of-memory, or untrusted checkpoints. Defer shared contracts to python. Not for generic profiling outside a training loop (python-performance), array kernels with no model (python-numerics), packaging (python-environments), or descriptive tables and charts (python-data-analysis)."
---

# Machine learning: trustworthy evidence before faster training

Run this skill for classical ML or deep-learning training, evaluation, checkpoints, and performance inside that loop. Treat the model as one stage of a reproducible decision pipeline: **prediction contract → data separation → fitted transformation → training → independent evaluation → deployment evidence**. A faster epoch with duplicated samples, changed precision or weaker validation is not an equivalent improvement. Defer shared data contracts to `python`. Defer generic profiling outside a training or inference loop to `python-performance`, array kernels with no model to `python-numerics`, packaging and CUDA/ABI repair to `python-environments`, and descriptive tables or charts to `python-data-analysis`.

Preserve the project's framework and model family unless the task calls for changing them. Classical ML and deep learning share data/evaluation contracts but need different implementation references. The examples use scikit-learn and PyTorch to make those contracts executable; neither is mandatory for every project.

## Choose the relevant depth

| Task or symptom | Read first |
| --- | --- |
| Suspicious validation, model selection, group/time splits, imbalance, calibration | [Classical modeling and evaluation](references/classical-ml.md) |
| Loss/gradient bugs, train/eval mismatch, AMP, batching, distributed training | [Deep-learning lifecycle](references/deep-learning.md) |
| Slow training/inference, worker explosion, device gaps, OOM or misleading timing | [Training and inference performance](references/training-performance.md) |
| Resume mismatch, export, model provenance, reproducibility or checkpoint safety | [Reproducibility and artifacts](references/reproducibility-artifacts.md) |
| Bundled script inputs, commands and coverage | [Executable examples](references/executable-examples.md) |
| Maintenance or tracing a version-sensitive claim | [Research sources](references/sources.md) |

Read the matching reference first. Read a second reference in this skill after the first one names a different stage (for example a split bug that is also a checkpoint mismatch). Each reference explains decisions offline. URLs are attribution, not missing instructions.

Defer interpreter, package source, lock, and CUDA ABI changes to `python-environments`. Defer generic Python or native CPU, wait, and system profiling outside this loop to `python-performance`. Defer array layout, kernels, dtype or reduction correctness, and JIT boundaries with no model to `python-numerics`. Defer descriptive joins and charts to `python-data-analysis`. Defer shared contracts to `python`. If a needed named skill is missing, ask to install that exact skill from this bundle; do not globally search, fetch a replacement or invent its contents. Independent data and model checks can continue.

## Establish what must remain true

Record prediction unit and horizon, target availability, repeated entities, split policy, feature availability at inference, metrics and costs, quality/latency/memory budgets, installed framework versions and device. Separate development decisions from the untouched evaluation set. A random seed is not evidence that separation or numerical behavior is correct.

For an optimization, capture a baseline with the same data IDs, preprocessing, shapes, batch size or stated changed batch semantics, precision, device, quality gate and measurement boundary. Fix correctness first, then change one bottleneck. Report cold start separately from steady state and include end-to-end latency/throughput rather than only operator time.

## Required handoff

Deliver the actual split/feature contract; observed failure or bottleneck; a minimal change with rationale and tradeoffs; before/after quality and resource evidence; and remaining untested configurations. State whether a result is a CPU smoke test, actual GPU measurement or distributed execution. Never convert an absent optional dependency into a passing framework test. Do not install packages, download datasets/models or load untrusted serialized objects as a side effect of diagnosis.
