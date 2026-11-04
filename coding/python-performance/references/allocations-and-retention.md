# Separate allocation activity from retained state

## Three different questions

1. **Churn:** how much is allocated/freed while completing useful work? Temporary strings,
   lists and arrays can consume time and peak memory without leaking.
2. **Retention:** which objects remain after equivalent work cycles? Unbounded caches,
   pending futures, queues, callbacks and references to large base arrays can retain data.
3. **Resident/system pressure:** what pages actually occupy memory and compete with other
   processes? RSS includes native allocations and mappings, not only traced Python objects.

A single growing RSS observation does not distinguish these. Collect a sequence of equal
work cycles, include cleanup/drain and compare steady-state plateaus. Document input growth;
a larger live dataset is not necessarily a leak. A cumulative allocation counter never
shrinks even when every object is freed.

## Python allocation experiment

Start tracemalloc before the relevant allocations (`-X tracemalloc=10` at startup or an
explicit `tracemalloc.start(10)` in the owned test harness). Snapshot after warmup, execute a
fixed number of work units, then snapshot after equivalent cleanup. Compare by traceback
or line and inspect positive size/count differences. Repeat cycles: a persistent increasing
retained set is stronger evidence than a single transient difference. More traceback frames
cost memory and CPU; do not maximize depth by default.

Only observed allocations are represented. A late start misses earlier allocations, and
tracemalloc is not a complete measurement of all native or device memory. If traced state is
stable while RSS grows, investigate native libraries, mappings and allocator behavior rather
than declaring Python objects clean enough to rule out all memory problems.

## Native and whole-process evidence

Memray can attribute allocations through native extensions. Choose native stacks when that
layer matters and symbols are available; choose Python-allocator tracing when individual
Python allocations matter. Modes change data volume and observer overhead. The retained/high-
water/temporary allocation views answer different questions; label which you used. Native
allocator tracking does not make CPU-memory tooling a GPU allocator profiler.

Track RSS/PSS, page faults and system reclaim/swap if memory pressure causes stalls. Minor
faults need not imply disk access; major faults need not all be swap (file-backed pages can
need reads). Correlate rates with I/O, reclaim and working set. Unsupported OS counters are
unknown, not zero. On Unix `resource` offers process counters, but field availability and
units are platform-dependent; don't silently compare raw maximum-RSS numbers across OSes.

## Fix the supported mechanism

| Evidence | Small remedy | Risk / verification / prevention |
| --- | --- | --- |
| Many temporary objects, stable retained set | Batch operations, reuse an owned buffer, avoid repeated conversion | Aliasing and stale contents; check results and peak allocations; define buffer owner/lifetime |
| Unbounded keys or pending work grow each cycle | Bound cache/queue, evict by policy, drain results | Hit-rate/latency or loss of required work; test sustained load and shutdown; explicit capacity contract |
| A small view keeps a huge base array alive | Copy only the needed slice when lifetime saving pays | Adds copy CPU/peak bytes; measure both; document view ownership |
| Excess parallel workers duplicate dataset | Reduce worker count, stream/chunk, consider explicit shared storage | Serialization/coordination; verify aggregate memory and throughput, not parent RSS only |
| RSS plateau remains after objects freed | Investigate allocator reuse/fragmentation before intervention | `del`/`gc.collect()` do not guarantee OS return; do not add collection to every request |

Do not use forced GC as a generic performance fix. It can diagnose a hypothesis in an
isolated test but changes timing and cannot free reachable objects. Stop when memory is
bounded under the required workload, not when RSS happens to return to its initial value.

## Provenance

- Python tracing: https://docs.python.org/3.14/library/tracemalloc.html
- Native allocations: https://bloomberg.github.io/memray/overview.html
- Allocator granularity: https://bloomberg.github.io/memray/python_allocators.html
- Resource counters: https://docs.python.org/3.14/library/resource.html
