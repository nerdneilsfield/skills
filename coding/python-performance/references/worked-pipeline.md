# A complete parse/filter/reduce example

A generic job receives JSON records, selects enabled records and reduces integer values.
A real pipeline may also read files, call native kernels and publish results. Measure these
separate stages; the fixture's bottleneck is not a diagnosis of your application.

From this skill directory, standard-library Python only:

```sh
python assets/batch_pipeline.py --rows 10000 --repeat 3
python -m cProfile -s cumulative assets/batch_pipeline.py --rows 10000 --repeat 1
```

The fixture generates fixed data locally, bounds rows/repeats and loads no arbitrary target.
`baseline` parses each record twice; `batched` parses once in the row's lifetime. The latter
means doing the record's operations together, not materializing a new full-dataset array.
Both return the same integer reduction and a parse-call counter. Timing excludes input
creation; process CPU covers only this process. The cProfile command includes both variants,
setup and output: its scope is not the first command's timing scope or a speedup benchmark.

Correctness: empty, singleton and representative datasets must yield equal totals. Mechanism:
two parses per row become one. Performance: unprofiled observations evaluate actual benefit;
tests intentionally do not assert a speed ratio. Small cases may be dominated by noise.
This fixture does not validate native kernels, service p95, scheduling or paging.

## Choose the remedy that matches the cause

The problem is redundancy within a record. A process pool would add IPC; caching every JSON
string would retain unlimited distinct input. A local parsed record removes duplication
without a cross-request lifetime. If real cross-batch reuse justifies a cache, specify its
capacity, invalidation and memory budget, then measure hit rate under sustained input.

Thus evidence leads to a lifetime-preserving local change; an output check establishes
correctness, a counter checks the mechanism, and unprofiled timing evaluates performance.
The lesson is not a universal “parse once gives X percent”.

## Follow the evidence when cost moves

If a native stage becomes dominant, investigate that layer instead of more Python tweaks.
If outer workers multiply native thread teams, test one parallel layer at fixed work and
measure whole-group CPU/memory. If queues grow because delivery cannot keep up, bound them
and use backpressure; a faster producer can otherwise worsen latency and memory. If traced
allocations plateau but RSS remains high, examine native allocations/allocator reuse before
forcing GC. These are conditional experiments, not mandatory changes to the fixture.

## Final report

Record workload/size and included stages, useful completed work, environment, evidence and
uncertainty, concrete change, correctness, unprofiled before/after spread, sacrificed resource,
and relevant capacity/lifetime regression check. If the target is unmet, name the next
experiment; if noise obscures a difference, say inconclusive. Do not claim unavailable tools
or platforms were tested.
