# Repeated-run JSON comparison, entirely offline

Use the local tool when timing/memory samples already exist and need a transparent descriptive comparison. It does **not** run the program, create a benchmark, establish experimental validity or infer statistical significance. It uses Python 3.9+ standard library only; there are no network calls or subprocesses.

Use an already installed Python 3.9+ interpreter: commands below use `python3`; on Windows use `py -3` (or the explicit Python 3 executable). Do not assume `python` is an alias.

From this skill's directory:

```sh
python3 scripts/compare_benchmarks.py --help
python3 scripts/compare_benchmarks.py assets/benchmarks/before.json assets/benchmarks/after-noisy.json
```

The bundled JSON files are synthetic interpretation fixtures, not measurements of user code. Expected noisy result: median 100→98 ms, descriptive relative improvement 2%, observed ranges overlap, `statistical_significance_established: false`. Exit 0 means only that declared metadata/checks permit a descriptive comparison; it does not mean a speedup was accepted.

## Input contract

```json
{
  "metric": "latency",
  "unit": "ms",
  "direction": "lower",
  "samples": [95, 100, 105],
  "correctness_passed": true,
  "metadata": {
    "input": "exact-dataset-id-or-content-hash",
    "compiler": "compiler-and-version",
    "build": "Release-with-specific-options",
    "cpu": "machine-cpu-identity",
    "threads": 1,
    "warmup": "same-policy"
  }
}
```

- `metric` and `unit` are nonempty strings; direction is `lower` or `higher`. Use one metric per file. Throughput generally uses higher; latency/memory generally lower. Never compare milliseconds to seconds and assume automatic conversion.
- Samples are at least three finite, nonnegative numeric repeats. This input floor is not a sampling-size recommendation. Use [measurement and report](measurement-and-report.md) to design the experiment and retain raw run order separately when paired analysis/drift matters.
- `correctness_passed` is a JSON boolean, not a string. `false` blocks comparability. It is the caller's assertion; the script does not run numerical or functional tests. Use false until actual quality checks pass.
- Metadata is a nonempty object. Include all conditions that could change interpretation: workload identity, compiler/options, CPU/environment, dependency/backend versions, thread settings, cache/warmup, affinity/power when relevant. The tool cannot detect omitted confounders or validate hashes. A minimal fake metadata object can pass structural validation and still describe a bad experiment.
- Metadata comparisons preserve JSON types recursively: `true`, `1` and `1.0` are not interchangeable. Keep recording formats consistent.
- Each input is limited to 1 MiB with a bounded read. Negative samples, NaN/infinity, booleans as samples and values outside finite numeric range are rejected rather than silently coerced.

## Output interpretation

`before`/`after` summarize count, median, min/max and median absolute deviation. `median_delta` is after minus before in the declared unit. `relative_improvement_percent` uses the declared preferred direction; positive values mean the observed median moved in the preferred direction, not that the change is statistically or practically established.

Zero baselines make a relative percentage undefined; extremely small baselines can make the percentage unrepresentable. In either case the percentage is null with an `unavailable` explanation; absolute medians remain inspectable. The tool avoids overflow in the median of large finite even-sized samples.

`overlapping_ranges` is a conservative warning, not a hypothesis test. `separated_ranges` also does **not** prove significance, unbiased sampling or causality. No confidence interval, paired-run model or multiple-comparison correction is supplied. Report the actual experiment, uncertainty and quality acceptance alongside these descriptive numbers.

## Deliberately changed metadata

Default behavior rejects every metadata difference. A compiler comparison intentionally changes compiler version; if that is the sole experimental variable and other conditions are controlled, explicitly allow that key:

```sh
python3 scripts/compare_benchmarks.py assets/benchmarks/before.json assets/benchmarks/after-compiler.json
# Expected exit 1, incomparable: compiler differs.
python3 scripts/compare_benchmarks.py assets/benchmarks/before.json assets/benchmarks/after-compiler.json \
  --allow-metadata-difference compiler
# Expected exit 0, records compiler in allowed_metadata_differences.
```

Repeat the option only for intentional variables and explain the experimental policy in the report. It is not a switch to silence inconvenient dataset/precision/hardware differences. Approval here cannot override failed correctness, unit/metric/direction mismatch, malformed input or other unapproved metadata differences. A deliberate backend/precision comparison still needs the same task-level quality budget.

## Local fixtures and exit codes

| Pair, always against `before.json` | Expected interpretation |
| --- | --- |
| `after-noisy.json` | 2% descriptive median change, overlapping ranges; no accepted speedup |
| `after-separated.json` | 20% descriptive median change, separated observed ranges; still no significance claim |
| `after-compiler.json` | Incomparable until deliberate compiler variable is explicitly allowed |
| `after-failed.json` | Incomparable regardless of speed because correctness did not pass |

Exit 0: comparable descriptive output. Exit 1: incomparable with reasons. Exit 2: invalid/unreadable input or CLI usage. Output JSON goes to stdout; diagnostics to stderr. Redirection such as `> comparison.json` is an explicit shell write chosen by the caller, not an implicit script mutation.

The separately distributed development-validation suite covers these decisions plus zero baseline, type-sensitive metadata and bounded input reads. It is not required to use this runtime tool; the local synthetic JSON fixtures and commands above are included here.
