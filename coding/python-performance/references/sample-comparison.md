# Compare existing samples without running arbitrary workloads

From this skill directory:

```sh
python scripts/compare_samples.py assets/sample-before.json assets/sample-after.json
```

These fixture JSON files contain **synthetic** numbers for exercising the helper; they are
not measured speedup evidence. Each file has exact required fields: `schema_version: 1`,
`workload`, `metric`, `unit`, `direction` (`lower` or `higher`), `scope`, at least three finite
nonnegative `samples`, boolean `correctness`, and a `metadata` object. Samples represent the
same metric per comparable useful-work unit. Do not feed pyperf or profiler JSON directly.

The helper checks comparability, prints median/MAD/range and descriptive change. It does not
assert statistical significance or independently verify the supplied correctness boolean.
Metadata differences reject comparison unless an explicit top-level key is allowed with
`--allow-metadata-difference KEY`; use only for the intentional change (such as revision),
not to erase incompatible hardware/input/thread budgets. The key must exist on both sides.

Each input is bounded to 1 MiB and 100000 samples. Invalid input exits 2, incompatible runs
exit 1, and a described comparison exits 0. Zero/overflow-denominator percentages are null,
not invented infinity or a speedup. These exits do not certify performance acceptance.
Record raw sample provenance separately and keep comparison scope honest.
