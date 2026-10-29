# Comparable measurements and an honest report

Load before collecting or interpreting an optimization result. This file is self-contained offline guidance; links at the end provide provenance, not prerequisites. Use already available build/timing tools, and disclose unavailable measurements instead of downloading a profiler automatically.

## Define one experiment

Write these fields before editing the hot path:

```text
Question: Does reusing the correspondence scratch buffer reduce frame latency?
Required metric: end-to-end frame latency in milliseconds (lower is better)
Quality gate: same accepted correspondences and pose within project tolerance
Input identity: local dataset revision/hash + frame range + seed
Machine: CPU/OS, relevant affinity/power constraints, background load
Build: revision, compiler/version, optimization flags, dependency versions
Execution: warmup policy, repetitions, outer/inner threads, cache policy
Changed variable: scratch-buffer ownership/reuse only
```

These are example fields, not claims about a particular project. If the user has no accuracy/latency budget, establish a provisional comparison criterion and label it; do not invent an acceptable pose error on the user's behalf.

The input must represent the task. For SLAM, separate cold initialization, steady tracking, relocalization and optimization if their costs differ. A kernel win does not guarantee a frame-level win. For peak memory, include temporary conversions and factorization workspace, not merely steady resident model size.

## Collect repeated samples without hiding context

1. Build both revisions/configurations with comparable optimized settings. Preserve symbols for profile attribution. A sanitizer Debug baseline cannot support a production speedup claim.
2. Verify outputs before timing. Remove or separately account for validation/instrumentation overhead consistently.
3. Decide whether the requirement is cold start or warmed steady state. Do not discard first runs just because they look slow if cold start is the product requirement.
4. Use a monotonic elapsed-time measurement around the intended boundary. State whether setup, disk I/O, allocation and result consumption are included.
5. Repeat the complete experiment enough to see variation. Alternate baseline/candidate order when thermal or background-load drift matters. Retain samples rather than only the fastest run.
6. Record failures, timeouts and excluded runs with reasons. Do not quietly remove outliers that represent real tail behavior.

For a trusted runnable target, an existing benchmark harness is preferable to a new generic subprocess wrapper. If only a shell timer is available, time the complete known command repeatedly and record limitations: shell timers and their formatting differ across platforms, and a short task may be dominated by startup/timer resolution. Do not compare tool outputs with different units or timing boundaries.

## Comparing distributions

For a lower-is-better metric, median reduction can be described as:

```text
reduction_percent = 100 * (baseline_median - candidate_median) / baseline_median
speedup_ratio = baseline_median / candidate_median
```

Positive reduction denotes less latency, not more throughput. For higher-is-better throughput, define the direction explicitly instead of reusing the latency formula. A zero/nonpositive denominator needs a different measurement or explicit handling; never emit an infinite speedup as evidence.

Report sample count, median and spread (for example min/max and interquartile range). The spread is descriptive, not a confidence interval. If a 2% median difference sits inside approximately 5% run-to-run variation, say the result is inconclusive and improve the experiment. Do not automatically convert overlapping ranges into a statistical hypothesis test either: independence, pairing, sample size and noise model matter.

Tail latency needs sufficient observations at the relevant granularity. Five whole-program runs do not estimate frame p99 reliably. State the percentile definition and sampling unit; preserve dropped frames and failures in the interpretation.

Metadata mismatch is a reason to stop a direct comparison. Different data, threads, compiler flags, CPU, backend or output quality can change the causal question. Changing revision is expected; silently changing unrelated execution settings is not. If multiple factors intentionally change, call it a system comparison rather than attribute the result to one code edit.

## Worked offline interpretation fixtures

| Fixture | Samples / facts | Appropriate conclusion |
| --- | --- | --- |
| Clear timing shift | baseline ms: 100,101,99,100,100; candidate: 80,81,79,80,80; same metadata and quality | Median falls 100→80 ms, observed 20% reduction / 1.25× ratio; causal explanation still needs evidence |
| Small/noisy | baseline ms: 95,100,105,99,101; candidate: 94,98,103,97,100 | Observed medians 100→98 ms; overlap/variation warrants an inconclusive claim, not guaranteed 2% gain |
| Incomparable | same samples, but candidate uses half the image resolution | Do not attribute timing to the implementation; compare matching input or explicitly evaluate quality trade-off |
| Incorrect output | candidate faster but registration fails on two frames | Reject performance-only acceptance; report failures and investigate correctness |
| Single sample | 100 ms versus 90 ms once | Observation, not a reliable distribution or general speedup |

These fixtures need no network, third-party dependency or code execution. They support reviewing the intended reasoning, not certifying a statistical method.

## Minimal delivery report

```text
Outcome: accepted / regressed / inconclusive / incomparable
Workload and correctness: identity, boundary, checks and quality results
Environment: CPU/OS, build/configuration, backend, effective thread counts
Measurements: raw sample location, n, units, direction, median and spread
Change: one concrete intervention; profile evidence or unverified hypothesis
Trade-offs: memory, tail latency, numerical tolerance, cold/warm behavior
Limitations: unsupported platforms/counters, noisy conditions, untested inputs
Next step: smallest useful experiment if the outcome is not established
```

A profile can explain a measured shift, but a missing profile does not erase a well-controlled timing observation. Conversely, a hot function disappearing from a profile is not proof that total latency improved. Keep measurement and explanation distinct.

## Provenance and local alternatives

- [Google Benchmark user guide](https://google.github.io/benchmark/user_guide.html) discusses repetitions, statistics and timing concerns; use it only if already part of the project, not as a mandatory new dependency.
- [Intel performance patterns](https://github.com/intel/intel-performance-skills/blob/main/skills/performance-patterns/SKILL.md) and [Linux perf tutorial](https://perfwiki.github.io/main/tutorial/) inform evidence-driven profiling. Their CPU-specific examples are not universal acceptance thresholds.

When offline, the record, equations and fixtures above are sufficient to design and review a basic experiment. Installed-tool help can resolve syntax; unavailable tools limit evidence rather than block all reasoning.

## Local sample comparison tool

When repeated measurements are already recorded, use [the local benchmark tool guide](local-benchmark-tool.md) for the complete JSON schema, interpreter commands, exit codes and synthetic fixtures. This stdlib-only tool does not execute workloads or make a statistical significance claim.
