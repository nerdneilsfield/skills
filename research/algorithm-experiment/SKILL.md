---
name: algorithm-experiment
description: "Use when running experiments to test an algorithmic idea: fix the hypothesis and baseline first, change one thing per ablation, pick the metric and seeds before looking, decide whether the evidence is statistically sufficient, and log every run so leakage and tuning bias are visible. Not for designing the method itself (algorithm-design) or for reproducing a published number (paper-reproduce)."
license: MIT
compatibility: Uses uv or the project's environment to run; hyperfine for timing; jq to aggregate run logs. A GPU run needs a fixed precision mode to be comparable across runs.
metadata:
  author: DengQi
---

# Experiments that can be believed

The output is a run log plus a verdict on whether the evidence supports the hypothesis. The verdict is often "not enough evidence".

## 1. Fix the hypothesis and the baseline

Write the hypothesis as a falsifiable statement with a direction, and name the baseline it is compared against. A hypothesis without a baseline cannot be tested. Run the baseline on the same data, metric, and budget as the treatment.

If no baseline exists, build the simplest one that works and say so. A comparison against nothing is not an experiment.

When the hypothesis came from a surprising result, or several explanations are live, write the rivals and the predictions that separate them with `research-hypothesis` before the first run. An experiment on which every explanation predicts the same result decides nothing.

## 2. Decide the metric and the split before running

Choose the metric definition, the evaluation split, and the number of seeds first, and write them down. Changing any of them after seeing results turns the experiment into a search over metrics.

## 3. Change one thing per ablation

Each ablation removes or replaces exactly one component, holding everything else fixed. An ablation that changes two things cannot attribute the difference.

Order the ablations by the component you believe matters most, and stop when an ablation shows no effect: that component is not earning its cost.

## 4. Log every run

One row per run, appended as it finishes:

```markdown
| Run | Commit | Config | Seed | Metric | Value | Wall | Notes |
```

Keep the raw output next to the row. A run that was not logged did not happen, even if you remember the number.

## 5. Decide whether the evidence is enough

Report the spread across seeds, not one run. For a comparison between two methods, use several seeds and check whether the difference is larger than the seed-to-seed spread; a difference smaller than the noise is not a result. When the effect is small, state that the experiment is underpowered rather than reporting the best seed.

## 6. Guard against the two biases

- **Leakage** — any information from the evaluation split that reached training or model selection. Tuning on the test set, normalizing with test statistics, or selecting the best checkpoint by test score are all leakage. Hold out a validation split and use it for every decision.
- **Tuning bias** — reporting the best configuration found after many trials as if it were the result of one. Count the trials and report the selection procedure.

## Gotchas

- A single seed is an anecdote. Report the spread, and never compare two methods on one seed each.
- Best-of-N selection inflates the winner. If you tried N configurations, N belongs in the report.
- Touching the test set during development is leakage even if you do not train on it. Every use of it is a decision.
- An ablation that removes a component also changes the parameter count and the runtime. Attribute the metric change to the component only if the budget is held comparable, or say it is not.
- A metric with a different definition in two runs is not the same metric. Fix the definition once, in code, and reuse it.
- A speedup measured with a cold cache or a single repeat is noise. Use several repeats and a warmup.
- Non-determinism from GPU kernels, threads, or hash order changes the last digits. Fix the seed and the precision mode, and still report the spread.
- A failed run is data. Keep it in the log; deleting it biases the average.
- "It converges" is not a metric. Report the value, the split, and the seed.

## Report

State the hypothesis, the baseline, the metric and split, the seeds, the per-run results with their spread, the ablation table, and whether the evidence supports the hypothesis, is underpowered, or is confounded.
