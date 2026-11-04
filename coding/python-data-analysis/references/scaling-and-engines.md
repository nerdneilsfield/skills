# Scaling without changing meaning

## Diagnose the expansion before choosing an engine

Separate disk bytes, decompressed in-memory columns, temporary arrays, join cardinality, group state, materialized results and figure/browser payload. A compact Parquet file can expand substantially when decoded. A join explosion is a contract failure first; a plotting crash after a successful query may be serialization/rendering rather than query memory. Measure wall time and peak resident memory on representative input, inspect result shapes and query plans, then choose one intervention. General profiling and nested CPU/BLAS thread budgets are owned by `python-performance`.

| Evidence | First repair | Tradeoff and proof |
| --- | --- | --- |
| Wide table, few columns used | Project required columns at read/scan | Assert schema and identical final summary |
| Most rows filtered late | Push safe predicates toward the source | Confirm semantics and actual plan/bytes, not merely syntax |
| Python per-row callbacks dominate | Native column expressions or batched operation | Match null, dtype, order and overflow behavior |
| Many temporary conversions | Stay in one representation longer | Check copy/lifetime behavior; Arrow compatibility is not universal zero-copy |
| Join rows explode | Validate key relationship before execution | Do not hide duplicate records to make a benchmark pass |
| Aggregate fits but input does not | Chunk/stream scan with mergeable state | Bound number of groups and verify combined denominators |
| Plot freezes | Aggregate/bin/sample for the visual question | Disclose reduction; preserve rare signals when required |

## pandas remains appropriate when it fits

Load only needed columns; specify safe dtypes and use categories for genuinely repetitive labels when that reduces memory. Measure `memory_usage(deep=True)` as a dataframe estimate, not whole-process peak memory. Avoid repeated concatenation in a loop; collect a bounded number of parts and concatenate once, or write/process batches when collecting them would exceed the budget. Do not promise `inplace=True` saves memory; copy behavior and Copy-on-Write depend on version and operation.

`read_csv(..., chunksize=...)` can support counts, sums and bounded grouped state. For a mean, maintain total and count; for variance, use a numerically stable mergeable algorithm rather than subtracting two huge nearly equal moments. An exact median, arbitrary sort, distinct set or unbounded-cardinality group map is not made bounded merely by reading chunks. State a memory/disk budget and choose an external algorithm or documented approximation if needed. Keep numeric-method details in `python-numerics`.

## Polars: scan before materialization

Use a lazy source such as `scan_parquet` when filter/projection pushdown matters. Wrapping an already loaded pandas frame in a lazy plan cannot undo its initial load. Prefer expression APIs over Python callbacks so the optimizer can reason about the query. Inspect `explain()` and, when useful, the installed version's physical/streaming plan. A typical expression is:

```python
q = (pl.scan_parquet('events.parquet')
     .filter(pl.col('eligible'))
     .select('group', 'value')
     .group_by('group').agg(pl.col('value').sum().alias('total')))
result = q.collect(engine='streaming')  # Check installed API and actual plan.
```

Streaming can execute supported work in batches; fallback or blocking operators may still increase memory. `collect` still materializes the final result: use an appropriate sink when the output itself is large. Verify null handling, categorical/group ordering, numeric types and join behavior against the original analysis rather than treating syntactic translation as equivalence.

## DuckDB: relational work over files

For joins/aggregations over local Parquet or CSV, a SQL query can avoid creating full Python dataframes. Select columns and filter before fetching, inspect `EXPLAIN`/profiling when appropriate, and return only the final small summary. Calling `.df()` on the full result brings memory pressure back into Python. Parameterize values and validate/quote identifiers rather than formatting untrusted strings into SQL. Do not enable remote extensions or external access just to analyze a local file.

Large sorts, joins and aggregates can spill to disk, but not every operator combination is guaranteed to fit. `memory_limit` is not a strict whole-process RSS cap; some allocations occur outside the buffer manager. Budget threads, application memory, other processes, disk capacity and temporary-directory permissions together. Set the temporary location deliberately on approved storage; spilling may place sensitive data there. Test under the real deployment quota, not only a workstation with spare RAM. Concurrent jobs need coordinated budgets rather than each assuming it owns the machine.

## Arrow: schema and batches, not a universal speed switch

Arrow datasets let you specify a schema and scan selected columns with a filter into record batches. Partition/statistics pruning can avoid work when layout and predicates support it; confirm actual behavior. Consume batches incrementally rather than immediately calling `to_table()` and retaining every batch. Explicit schemas avoid divergent inference across files. Timestamp units/timezones, dictionary/category representation and nullable values need compatibility checks at boundaries.

A zero-copy interchange can retain the original allocation for longer than expected. Some dtype conversions, string conversions or chunk consolidation require copies. Compare both runtime and peak memory in the receiving library. Parquet partitioning can help common filters but excessive tiny files or high-cardinality partition trees add metadata and open overhead. Choose physical layout for observed queries, not a universal partition recipe.

## Fair comparisons and prevention

Keep the same dataset snapshot, ordering requirement, null semantics, type widths, result tolerance, thread budget and cache policy. Compare end-to-end read/transform/write or chart preparation, not just the fastest isolated kernel. Record cold and warm behavior separately if both matter. A lazy plan that has not been executed is not a finished benchmark. Reconcile aggregate counts/results before accepting performance. Regression checks should include peak-memory trends, malformed schemas and cardinality changes, not just elapsed time on a tiny happy-path fixture.
