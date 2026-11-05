# Define what the experiment can prove

## Measure the user's outcome first

A batch pipeline can be slow in input construction, parsing, computation, serialization,
queueing or delivery. Time the whole useful operation first. A microbenchmark excluding
input creation answers a narrower question and must say so. Record input identity, shape,
size, seed, work count, expected output and the correctness/precision acceptance check.
For a service record offered load, completed work and error rate: rejecting work can make
successful requests look faster without improving the service.

Use `time.perf_counter()` for elapsed wall time and `time.process_time()` for current-process
CPU. Wall includes waiting; process CPU excludes sleeping.
Across native threads process CPU can exceed wall. Their ratio is a clue, not a lock/GIL
classifier. Include worker-group accounting before claiming parallel efficiency.

Define units and scope before collection: seconds per batch differs from seconds per item;
throughput increases are not latency decreases. Preserve raw repeats. Separate first import,
JIT/compilation, cold cache, warm execution and teardown according to the real workload.
Do not silently discard slow samples. Report median plus spread; tail quantiles need enough
representative observations, not five loop timings dressed up as p99.

## Comparable baseline

Record Python executable/version and GIL/build mode, source revision, dependency lock,
OS/CPU, usable affinity/quota, thread-pool controls and meaningful input/configuration.
Avoid including secrets, full environment dumps or command arguments with credentials.
Hold these fixed or explain the changed variable. Alternate before/after ordering where
practical and repeat in independent processes when allocator/JIT state matters.

Profiler run: identify a suspect. Unprofiled run: evaluate the change. Tracking function
calls disproportionately affects call-heavy Python; allocation tracing changes memory and
CPU; high sampling rates also have cost. Compare capture-on and capture-off overhead on the
same workload if operational impact matters. Never treat an advertised overhead as a budget.

For small snippets `timeit` is available offline.
`pyperf` is an optional stronger repeated-run harness; missing installation is not a reason
to fetch it or tune host settings. Do not run `pyperf system tune` automatically.

## Acceptance and causal claims

1. Compare outputs, including edge sizes and failures; numeric work uses the project's tolerance.
2. Compare unprofiled observations with identical useful work and units.
3. Check the sacrificed resource: cache size, peak allocation, queue capacity, worker count.
4. Check a representative production-scale case; a tiny example cannot establish scalability.
5. Separate measured improvement from inferred explanation. If noise is comparable to the
   difference, report inconclusive and choose a larger/cleaner experiment rather than claim victory.

The bundled comparison helper summarizes existing samples; it is not a statistical test,
profiler, benchmark runner or correctness oracle. Its input must record the actual workload
and correctness result, not invented labels to make incompatible runs compare.

## Provenance

- CPython profiler guidance: https://docs.python.org/3.14/library/profile.html
- Timing API and GC behavior: https://docs.python.org/3.14/library/timeit.html
- Repeated processes/warmups: https://pyperf.readthedocs.io/en/latest/run_benchmark.html
