---
name: python-ml
description: Use when building, evaluating, debugging or optimizing Python machine-learning models and deep-learning training or inference, including data leakage, misleading validation, unstable training, slow data loading, GPU out-of-memory and unreliable checkpoints.
---

# Machine learning: trustworthy evidence before faster training

Treat the model as one stage of a reproducible decision pipeline: **prediction contract → data separation → fitted transformation → training → independent evaluation → deployment evidence**. A faster epoch with duplicated samples, changed precision or weaker validation is not an equivalent improvement.

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

Read only the matching reference initially; cross to another when the evidence crosses its boundary. Each reference explains decisions offline. URLs are attribution, not missing instructions.

Use `python-environments` for interpreter/package source/lock/CUDA ABI changes; `python-performance` for generic Python/native CPU/wait/system profiling; `python-numerics` for array layout, kernels, dtype/reduction correctness and JIT boundaries. If a needed named skill is missing, ask to install that exact skill from this bundle; do not globally search, fetch a replacement or invent its contents. Independent data/model checks can continue.

## Establish what must remain true

Record prediction unit and horizon, target availability, repeated entities, split policy, feature availability at inference, metrics and costs, quality/latency/memory budgets, installed framework versions and device. Separate development decisions from the untouched evaluation set. A random seed is not evidence that separation or numerical behavior is correct.

For an optimization, capture a baseline with the same data IDs, preprocessing, shapes, batch size or stated changed batch semantics, precision, device, quality gate and measurement boundary. Fix correctness first, then change one bottleneck. Report cold start separately from steady state and include end-to-end latency/throughput rather than only operator time.

## Required handoff

Deliver the actual split/feature contract; observed failure or bottleneck; a minimal change with rationale and tradeoffs; before/after quality and resource evidence; and remaining untested configurations. State whether a result is a CPU smoke test, actual GPU measurement or distributed execution. Never convert an absent optional dependency into a passing framework test. Do not install packages, download datasets/models or load untrusted serialized objects as a side effect of diagnosis.
