# Fixing cache, cache-line and synchronization bottlenecks

Use after evidence identifies a plausible locality, bandwidth, coherence or synchronization cost. [Cache lines and contention](cpu-cache-sharing-contention.md) explains collection and attribution; this reference supplies **what to change, what can break, how to verify it, and how to avoid recreating it**. No recipe is permission to rewrite unrelated code, change deployment settings, install tools or add a dependency. CPU only.

All snippets below are original **scoped C++ examples**, not standalone programs or claimed measurements. Surrounding types, input contracts, error handling and worker ownership must be supplied by the project. They illustrate a change to test, not a promise that it is faster. A normal mutex, simple container or compact layout remains preferable when no meaningful bottleneck exists.

## 1. Choose a remedy for the actual mechanism

| Supported mechanism | First changes worth testing | Changes that do not follow automatically |
| --- | --- | --- |
| Poor spatial locality / pointer chasing | Traverse contiguous data; compact hot fields; use stable indices or chunks when ownership permits | Rewrite every AoS into SoA or replace every container |
| Reused data exceeds useful cache working set | Tile the actual reuse loop; reduce simultaneously live intermediates | Pick tile size from advertised cache capacity alone |
| Memory bandwidth plateaus | Remove redundant passes/copies; fuse compatible work; reduce bytes touched and unnecessary materialization | Add more threads, force wider SIMD, estimate bandwidth from generic misses |
| TLB/page-walk pressure | Reduce scattered pages; contiguous/chunked allocation; reduce active working set | Enable huge pages or change host policy globally |
| Independent fields share a hot coherence line | Keep per-worker state local; batch publication; separate measured independent hot fields if still needed | Pad every object to an assumed 64 bytes |
| Many workers update one logical object | Privatize/reduce when semantics allow; shard ownership; batch or use a single owner | Put the same atomic on its own line and expect serialization to vanish |
| Long contended critical sections | Remove unrelated work from lock; extract a bounded batch; shorten ownership and simplify protected invariants | Replace the mutex with a spinlock or generic lock-free structure |
| Busy waiting without useful progress | Blocking predicate wait for potentially long waits; reduce notifications; repair owner scheduling | Assume spinning is always lower latency |

For every experiment retain the same workload identity, successful-work count, quality checks and production-like build. Compare time/latency **and** the evidence associated with the proposed cause. Cache misses, switches or lock acquisitions may decrease while useful work regresses; a counter improvement alone is not acceptance.

## 2. Repair traversal before replacing the representation

### Evidence and preconditions

The hot path walks a row-major image/matrix or point-field buffer with a large stride, or repeatedly follows pointers through scattered allocations. Confirm dimensions, stride/padding, ownership and actual element layout. A view/ROI can be non-contiguous; “row-major” does not imply `row_stride == columns`.

For a non-overlapping input/output, or exactly the same elementwise buffer, these scoped loops perform the same independent scaling. Require `cols <= stride`, buffers containing at least `rows * stride` elements, and representable dimensions/products/index arithmetic. Partial input/output overlap is outside the contract.

```cpp
// Before: a column walk through row-major storage.
for (std::size_t c = 0; c < cols; ++c)
  for (std::size_t r = 0; r < rows; ++r)
    output[r * stride + c] = scale * input[r * stride + c];

// Candidate: visit neighboring elements together.
for (std::size_t r = 0; r < rows; ++r) {
  const auto base = r * stride;
  for (std::size_t c = 0; c < cols; ++c)
    output[base + c] = scale * input[base + c];
}
```

**Why this can help:** sequential lines/pages are reused before eviction, hardware prefetch has a simpler pattern, and fewer unrelated pages are active simultaneously. No change in scalar precision or arithmetic operation is required. It may not matter for tiny data, already-vectorized library calls or an end-to-end path dominated by another stage.

**Correctness and side effects:** changing iteration order is not generally safe for recurrences, partial aliasing, in-place stencils, cross-element dependencies, external callbacks or order-sensitive reductions. Preserve required deterministic output ordering. Do not introduce `restrict`, `noalias()` or unchecked alignment assumptions merely to encourage vectorization.

**A/B:** validate output and padding/sentinel regions on zero/one/odd dimensions, padded rows and representative large sizes. Include cold/warm policy explicitly; examine useful bytes/work and supported cache/TLB events. Account for any conversion or view construction. **Prevent:** make layout/stride contracts explicit in APIs, use meaningful row/column accessors, and avoid hiding repeated full transposes inside helpers.

### AoS, SoA and compact hot state

If a hot pass reads only XYZ from a large point record containing descriptors, strings and metadata, it may fetch much more than it uses. Candidate changes, from smallest to largest:

1. Avoid copying the full record when a reference or narrow view suffices.
2. Process a compact batch of needed fields, measuring gather/conversion cost.
3. Separate immutable/cold metadata from the hot numeric record while retaining stable IDs/lifetimes.
4. Use SoA or AoSoA only if the dominant passes benefit and the cross-field/producer APIs can be maintained simply.

SoA can hurt a pass that consumes all fields of one object; conversion and duplicated storage may outweigh kernel savings. PCL/OpenCV/Open3D representations must not be reinterpreted as packed arrays without their alignment/stride/lifetime contracts. Preserve labels, associations and frame identity when reordering points. **Prevent:** design hot kernels around the fields they actually require, but keep representation changes localized rather than build an all-purpose data-layout abstraction.

## 3. Tile reuse and reduce memory traffic

### Cache blocking

**Evidence:** the same matrix/image neighborhood is reused, but a full row/plane/iteration makes the live working set too large. **Change:** partition the loops into tiles that complete useful reuse before moving on. Keep the original boundary handling and dependency order. For a stencil, distinguish immutable input from output, preserve halo cells, and do not accidentally replace a Jacobi-style update with an in-place Gauss–Seidel update.

Select candidate tile sizes from the actual bytes simultaneously needed: input/output, halos, temporary arrays, multiple channels and concurrent workers sharing a cache. Sweep a small justified set on the target hardware. Cache associativity/conflicts, prefetch, vector width and shared cache occupancy mean “tile equals cache size” is not a formula.

**Correctness:** test edge tiles, dimensions not divisible by tile size, padded strides and degenerate dimensions. Floating-point reduction reordering can change rounding or convergence; use the numerical error budget, not just a byte comparison. **A/B:** include setup/copy time; compare cache-fitting and larger representative inputs plus per-work traffic/time. **Prevent:** keep the tile parameter near the kernel with a documented tested range, not an unexplained architecture-wide magic constant.

### Fuse passes only when the contracts match

A hot path may compute an intermediate array, write it, then read it once in a second pass. If neither stage needs the whole intermediate and no other consumer observes it, compute each intermediate value locally and consume it immediately. This can reduce allocation, reads and writes more than instruction-level tuning.

```cpp
// Before: scratch is produced solely for this immediate consumer.
for (std::size_t i = 0; i < n; ++i) scratch[i] = transform(input[i]);
for (std::size_t i = 0; i < n; ++i) output[i] = consume(scratch[i]);

// Candidate: transform/consume must be independent and safe in this order.
for (std::size_t i = 0; i < n; ++i) {
  const auto value = transform(input[i]);
  output[i] = consume(value);
}
```

**Preconditions:** no whole-array dependency, externally required scratch data, alias-dependent behavior, ordering-sensitive side effects or requirement that all transforms succeed before any output changes. Exceptions can leave a different partial-output state in the fused form; preserve the existing transaction/error contract. Fusion can increase register pressure, impede vectorization or duplicate work for multiple consumers.

**A/B:** count removed bytes and allocations, but measure actual end-to-end timing and output/error behavior. **Prevent:** make intermediates' ownership/consumers clear and avoid mandatory materialization at every API boundary. Do not ban intermediates that make the algorithm correct or maintainable.

### TLB pressure and page locality

When supported page-walk/TLB events plus a scattered-access/size sweep implicate translation overhead, first reduce the number of active pages and improve locality: chunk related nodes, use a contiguous stable-index representation where lifetime permits, reuse bounded scratch storage, or process a compact working set per phase. Check whether pointer-heavy traversal is actually waiting for data rather than translation before crediting TLB changes.

Larger pages are a **separate, authorized** experiment, not the default remedy. They can increase fragmentation, pinned/resident footprint, allocation latency and NUMA-placement sensitivity; kernel/allocator behavior and transparent huge-page policy vary. A reserved address region is not proof that huge pages back it. Record actual mapping/page behavior and tail latency. Do not enable THP, call privileged controls, lock memory or change system policy merely because a TLB counter rose. **Prevent:** avoid unnecessary per-element allocations and unbounded simultaneous arenas; retain simple ownership rather than invent a custom allocator without evidence.

## 4. Reduce sharing before padding it

### True sharing: global counter versus local reduction

**Evidence:** every worker repeatedly modifies the same atomic statistic, and that update is materially hot. If the requirement is only the final total, make the hot accumulation private and combine after workers finish.

```cpp
// Before, inside every worker's item loop:
completed.fetch_add(1, std::memory_order_relaxed);

// Candidate, inside one worker: count locally, publish once when finished.
std::uint64_t local_completed = 0;
for (const auto& item : assigned_items) {
  process(item);
  ++local_completed;
}
completed.fetch_add(local_completed, std::memory_order_relaxed);
```

The final count must fit `uint64_t`; define what “completed” means when processing fails or is cancelled. This is not equivalent if a controller requires per-item live progress, enforces a strict global budget, or uses this count to publish other memory. `relaxed` is suitable only for the counting semantics already established; it does not publish `process` results. Join workers or use the existing separate synchronization before reading their outputs. For live progress, bounded batching can reduce updates but deliberately changes staleness; preserve the actual responsiveness/cancellation contract.

An alternative is one ordinary counter per worker, written only by that worker and read after join, then reduced. Allocate stable slots before launch, do not resize the container concurrently, and do not use `vector<bool>` as independent writable flags. Even better, accumulate in a local variable and write the slot once: this often removes the hot sharing without any padding.

**A/B:** preserve exact task accounting, cancellation/error paths and required observation points. Compare update frequency, relevant ownership traffic, throughput and p99 responsiveness. Include the reduction/publication cost. **Prevent:** separate high-frequency private telemetry from control/synchronization data; avoid making every hot operation update one global statistic.

### False sharing: isolate only independent hot owners

**Evidence:** mapped addresses/offsets show independent fields with a writer on the same coherence line, and a controlled ownership/layout experiment supports the hypothesis. **Change:** first keep updates private or batch them; if concurrent independent fields genuinely must be published frequently, place them in separately aligned/strided worker slots or split read-mostly metadata from hot write state.

The following is a layout sketch, **not** a universal 64-byte prescription:

```cpp
// Before: adjacent frequently updated atomics may share a line.
struct PackedCounters {
  std::atomic<std::uint64_t> first{0};
  std::atomic<std::uint64_t> second{0};
};

// Candidate: target_alignment must be a supported compile-time alignment,
// chosen/validated for this deployment and uniform across ABI boundaries.
struct alignas(target_alignment) WorkerCounter {
  std::atomic<std::uint64_t> value{0};
};
```

Inspect actual `alignof`, `sizeof`, element stride and addresses; alignment of a struct start does not separate its members. An array of over-aligned elements must use an allocation path that respects that alignment. C++17+ ordinary aligned allocation helps supported paths, but foreign buffers/placement new/custom allocators need their own contract. `std::hardware_destructive_interference_size`, when available, is an implementation hint, not a runtime probe; changing it across translation units or public layouts can create ABI problems.

**Side effects:** padding increases memory/TLB footprint and can make scans, cache capacity and initialization worse. Separating fields that are consumed together can harm constructive locality. True-sharing words remain serialized even if isolated. **A/B:** compare required thread counts, memory footprint, representative small/large working sets and traffic/time. **Prevent:** give hot mutable fields clear owners, separate unnecessary shared telemetry, and reserve padding for specific measured boundaries rather than a blanket style rule.

## 5. Shorten lock ownership without breaking the invariant

### Move slow unrelated work outside the lock

**Evidence:** a specific critical section has substantial hold time or wait tails and contains logging, I/O, callbacks, allocation or computation not required to protect shared state. **Change:** copy/move a stable snapshot or extract a small batch under the lock, release it, then do independent work. Preserve what must be atomic.

```cpp
// Before: the mutex serializes queue access AND arbitrary work.
{
  std::lock_guard lock(queue_mutex);
  if (!queue.empty()) {
    process(queue.front());
    queue.pop_front();
  }
}

// Candidate: Item has suitable move/error behavior; process is independent.
std::optional<Item> item;
{
  std::lock_guard lock(queue_mutex);
  if (!queue.empty()) {
    item.emplace(std::move(queue.front()));
    queue.pop_front();
  }
}
if (item) process(*item);
```

This is a **semantic change to review**, not a drop-in general rewrite. It changes failure handling: the candidate removes the job before processing, so an exception needs an explicit retry/failure policy if the original retained it. Concurrent consumers can finish out of FIFO order. `Item` movement can throw, and moving from a queue element before the move fails may change its state. Choose a suitable no-throw transferable handle or preserve the established exception contract. Do not keep a reference to an element that another worker can erase after unlock.

For bounded batching, transfer at most a workload-appropriate amount under the lock and process outside. Larger batches reduce acquisitions but can increase hold time, starvation, memory and tail latency. Use existing cancellation/backpressure contracts. **A/B:** test exactly-once/at-most-once/retry semantics as required, result ordering, shutdown, exceptions and concurrent producers. Measure wait/hold distributions and useful throughput rather than just lock acquisition count. **Prevent:** keep lock scope adjacent to protected invariants; never invoke unknown callbacks or block on I/O under a hot mutex without a reason.

### Snapshot/recheck for expensive preparation

If a change depends on shared mutable configuration, one pattern is: read a stable snapshot plus version under lock; prepare outside; reacquire lock, validate the version/preconditions, then commit or retry. This is appropriate only when preparation has no irreversible externally visible effects and retry cost/starvation is bounded. Without the recheck, the optimization can introduce a time-of-check/time-of-use race. If this adds more complexity than the measured benefit justifies, retain the lock.

### Shard by real ownership, not by arbitrary hashes alone

For independent key/object updates, shard the protected state by a stable key or give a partition to one worker. Check skew: one hot key still serializes. Cross-shard operations need a documented order/transaction model; acquiring multiple shard mutexes casually can create deadlocks. Avoid copying large state to every shard if memory pressure is already the problem. **A/B:** include skewed keys and cross-partition operations, not only uniform synthetic distribution. **Prevent:** make ownership and aggregation boundaries explicit early; keep multi-object invariants together when that is the simpler correct design.

## 6. Replace unproductive spinning with the right wait

If workers spin while an owner is descheduled or while I/O/long work completes, a spinlock/atomic poll loop can waste capacity and worsen oversubscription. `yield()` is not a guarantee that the owner runs next and is not a portable backoff policy. Do not insert arbitrary sleeps into production synchronization to make a profile look quieter.

For potentially long waits, an existing mutex/condition-variable predicate is often the simpler candidate:

```cpp
// Consumer sketch: ready/stop are protected by the same mutex.
std::unique_lock lock(mutex);
condition.wait(lock, [&] { return stop || !queue.empty(); });
if (stop && queue.empty()) return;  // This example drains queued work on stop.
auto item = std::move(queue.front());
queue.pop_front();
lock.unlock();
process(item);
```

Producers change the predicate under the mutex and notify according to actual demand; a notification alone is not stored work. Recheck the predicate to tolerate spurious wakeups. Shutdown must wake waiters and follow the chosen drain/cancel semantics. Apply the same item-move/exception caveats as above. `notify_one` can avoid a thundering herd for one available item, while broadcast is necessary for some shutdown/state changes; blanket replacement of `notify_all` is not correct.

C++20 atomic wait/notify can fit a carefully designed single-word state protocol, but a value change alone does not replace required notification or a full queue/lifetime design. Do not mix atomic and non-atomic access to the same state. **A/B:** examine CPU used while idle, wake latency/tail, throughput under short and long waits, cancellation and missed-wakeup tests. **Prevent:** match waits to the resource contract; prefer bounded queues/backpressure to unbounded busy polling, and avoid waking every worker for every tiny item.

## 7. Atomics and lock-free are not a free performance tier

A hot contended atomic RMW is still coherence serialization. First reduce communication frequency, partition ownership, or change work granularity. If independent values only need final aggregation, local state can outperform both a mutex and a contended atomic without a complex memory model.

Weakening `seq_cst` to acquire/release/relaxed requires a written synchronization argument: which writes become visible to which reader, through which atomic or lock, and what establishes object lifetime. “It is just a flag” is insufficient. Relaxed operations can count independent events but cannot by themselves publish an initialized object. `volatile` is not thread synchronization. Do not insert fences until a failing protocol seems to work.

A lock-free queue/list introduces reclamation, ABA, lifetime, boundedness, fairness and platform lock-freedom questions. Verify whether the chosen atomic type is actually lock-free on supported targets; lock-free progress is not wait-free latency, fairness or automatic throughput. Prefer an existing proven project facility over a new home-grown algorithm, and keep the user's vendoring policy if a new library is genuinely needed.

**A/B:** preserve linearization/ordering semantics, test stress and shutdown/reclamation paths, and use targeted TSan where supported (a clean run is not proof of correctness). Compare throughput, p99 latency, CPU utilization and memory under contention and low contention. **Prevent:** document ownership and the synchronization edge at the boundary; do not expose mutable shared state simply because atomic fields make compilation easy.

## 8. Acceptance and prevention checklist for a focused patch

Record one row per actual change, not a performance rewrite wish list:

```text
Evidence / competing hypothesis:
Required observable semantics and lifetime/ordering contract:
Concrete code/layout/ownership change:
Correctness tests, failure/shutdown paths and numerical tolerance:
Before/after representative latency/throughput, spread and useful-work count:
Mechanism evidence (available counters, hold/wait, traffic, allocation):
Footprint, conversion/setup, fairness and tail-latency trade-offs:
Deployment/compiler/ISA restrictions and unmeasured regimes:
Small preventive rule kept near the affected API/code:
```

Good preventive rules describe a discovered boundary: “worker statistics stay private until batch publication,” “this image view carries row stride,” or “no callbacks while queue_mutex is held.” Bad preventive rules are global prohibitions such as “all counters padded,” “all mutexes forbidden,” “always use SoA,” or “every numerical loop hand-vectorized.” Keep the smallest design that meets the real budget.

## Local context and source pointers

- [Cache evidence and c2c/lock attribution](cpu-cache-sharing-contention.md).
- [Scheduler/usable CPU capacity](scheduler-thread-capacity.md) before interpreting spinning or active-worker demand.
- [Memory pressure and NUMA](memory-pressure-numa.md) before trading compactness for padding/replication/large pages.
- [Measurement and report](measurement-and-report.md) and [local repeated-run comparison](local-benchmark-tool.md).
- For matrix aliasing, precision, solver convergence and data interfaces, use `cpp-numerics` and its locally installed references; this document does not redefine those contracts.

Original remedies and examples synthesized for this bundle. The collection reference links kernel false-sharing documentation, upstream perf manuals and target-specific sources; they establish terminology and measurement caveats, not universal optimization prescriptions. External links are not required to use the workflows above.

## Local runnable correctness companion

The [original C++20 remediation examples](../assets/remediation-examples/README.md) provide complete compilable local-aggregation, row-major traversal, close-and-drain bounded-queue and buffer-reuse examples. Their Debug/Release checks validate results/lifecycle, not speed. The scoped snippets in this reference remain integration examples; library/runtime-specific changes still need the actual project and an A/B measurement.
