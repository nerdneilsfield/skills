# Fixing thread and memory bottlenecks, then avoiding their return

Use this after the evidence identifies a plausible mechanism, not merely a large counter. The diagnostic companions are [scheduler/thread capacity](scheduler-thread-capacity.md), [memory pressure/NUMA](memory-pressure-numa.md), and the [read-only proc collector](proc-sampler-guide.md). This reference supplies the next implementation choices and acceptance tests offline. It does not authorize deployment quota, affinity, memory-policy or kernel-setting changes.

For every change keep five things together: the slow workload and quality target; the specific resource hypothesis; one reversible implementation change; correctness and resource side effects; comparable before/after evidence. A reduced switch/fault count alone is not success if throughput, tail latency, memory or numerical quality worsens. Test representative small/large, balanced/skewed and burst/steady inputs, not only the input that made the optimization attractive.

## 1. Runnable oversubscription: reduce competing work, not blindly all threads

**Precondition.** During the actual slow phase there is excessive runnable demand relative to allowed CPUs/visible quota, or a worker-count sweep shows increasing runnable delay/preemption/throttling while useful throughput plateaus or falls. Sleeping I/O threads do not by themselves establish this. Identify all pools, CPU masks, quota periods and shared cgroup users first.

**Concrete change and verification.** Apply the single [parallelism/BLAS policy](parallelism-and-blas.md): it owns the explicit orchestration budget, outer/inner experiment, backend-control scope, correctness/quality risks and acceptance/prevention rules. Use the capacity evidence above as its input. Continue to the following sections only if granularity, waiting, buffer ownership or memory behavior also needs changing; do not recreate a second thread policy here.

## 2. Too-small tasks and wakeups: batch only where latency permits

**Precondition.** Profiles show executor/queue/synchronization overhead dominating useful work, many tiny tasks, or workers repeatedly waking for negligible batches. A producer/consumer service-time trace is more useful than raw context-switch totals alone.

**Concrete change.** Keep the existing executor and group adjacent work into chunks. For a contiguous point/image range, each task can own a disjoint interval, reuse scratch and publish one completion rather than enqueue one task per point. The following is **integration pseudocode**, not a new executor implementation:

```text
Before:
  for each element i: submit(one_element(i))
After:
  for each disjoint [begin,end) chunk:
    submit(process_range(begin,end))
  collect the submitted chunk results outside an exhausted worker pool
```

Choose chunk size from workload and latency, not a magic constant. Static ranges suit predictable cost/locality; a small set of dynamic chunks can help skewed geometry or variable-cost residuals. Too-large chunks lose load balance and delay cancellation. For a streaming queue, a consumer can drain a bounded batch while preserving required order, but must release the queue lock before expensive processing.

**Correctness/side effects.** Specify ownership of input/output intervals and lifetime until all tasks finish. Avoid overlapping writes and retained views into growing vectors. Preserve ordering when outputs are order-sensitive; otherwise explicitly define the stable merge/index mapping. Keep error propagation, cancellation and shutdown observable. Do not await futures while holding a lock needed by workers.

**A/B verification.** Sweep a few chunk sizes and worker counts; include skewed inputs. Measure work per task, queue operations, CPU overhead, p95/p99 latency, cancellation response and output equivalence. A throughput gain that violates the real-time tracking deadline is not accepted.

**Prevent recurrence.** Centralize task granularity near the partitioning code; document why it is chosen and expose it only if tuning is genuinely necessary. Avoid logging/progress updates per element when a throttled batch update suffices.

## 3. Waiting and migration: fix ownership and scheduling before pinning

**Precondition.** Wait stacks or stage traces identify a serial producer, lock owner, barrier imbalance, pool starvation or repeated cross-worker handoff. For migration specifically, show degraded locality/latency alongside actual migration counts and data placement; a changed last-observed CPU is not an exact count.

**Concrete changes:**

- Move expensive processing, I/O, allocations and user callbacks outside the critical section when ownership permits. Copy/move the small required work item under the lock, release it, then process. Preserve a coherent snapshot rather than read shared state unsynchronized.
- Replace busy polling for ordinary work availability with the existing event/future/condition variable. A condition-variable wait needs a predicate guarded by the same mutex and a shutdown condition; notification without a state predicate can lose wakeups.
- Investigate the *last* barrier arrival: rebalance partitions or move independent work across the stage boundary before replacing the barrier primitive.
- Reduce unnecessary cross-worker ownership handoffs; keep a shard's mutable state with a stable worker when that matches the workload. Preserve enough work balancing to avoid idle capacity.
- For repeated migrations with demonstrated locality loss, first compare coarser tasks and stable partitioning. A process-local affinity experiment is a separate explicit choice, checked against allowed masks, heterogeneous cores, quotas and neighboring workloads. Do not pin every worker by default.

A condition-variable excerpt illustrating the predicate/lifetime contract, not a complete queue API:

```cpp
// All queue and closed changes use mutex. Producer notifies after changing state.
std::unique_lock lock(mutex);
ready.wait(lock, [&] { return closed || !queue.empty(); });
if (queue.empty()) {             // closed and drained
    return;
}
Work item = std::move(queue.front());
queue.pop_front();
lock.unlock();
process(item);                   // error policy belongs to the worker boundary
```

The queue must outlive workers. Shutdown must set `closed` under the mutex and notify all relevant waiters; determine whether to drain or cancel queued work before joining. Do not hold a queue lock across joining workers. C++ `jthread` stop requests do not automatically wake a plain `condition_variable`; connect cancellation to the actual wait predicate/notification or use an appropriately supported stop-aware primitive.

**Correctness/side effects.** Releasing a lock earlier can invalidate borrowed state unless ownership/snapshot semantics are explicit. Batching notifications can delay response. Stable partitions/affinity can worsen imbalance, restrict available CPUs or move work away from data. Different NUMA placement can increase memory footprints if replication is introduced.

**A/B verification.** Check progress, shutdown, cancellation and error paths, then measure blocked/runnable time, barrier arrival spread, queue latency, migrations and throughput. Use bounded waits in tests instead of sleeps guessed to be “long enough.” If no wait stacks are available, label the lock/I/O explanation provisional.

**Prevent recurrence.** Define worker-state ownership and shutdown contracts. Keep lock scope visible and avoid callbacks under internal locks. Retain a skewed-input test and a shutdown-under-load test when those behaviors changed; do not create a generic concurrency framework for them.

## 4. Allocation and first-touch: reuse bounded storage with correct lifetimes

**Precondition.** Allocation/copy stacks, allocator counters or repeated minor-fault bursts dominate a phase. Distinguish one-time startup from repeated per-frame work, and live allocations from allocator-retained pages. RSS staying high after `free` is not by itself a leak.

**Concrete change.** Reuse a worker-owned buffer across sequential jobs when data need not escape that worker. Reserve based on a justified upper bound or observed batch size; resize before writing through indices. Example excerpts for a synchronous `transform_into` operation:

```cpp
// Before: a new allocation path is possible on every job.
for (const auto& frame : frames) {
    std::vector<float> scratch(frame.size());
    transform_into(frame, scratch);
    consume_now(scratch);
}

// After: one owner, reused capacity; resize still establishes valid elements.
std::vector<float> scratch;
for (const auto& frame : frames) {
    scratch.resize(frame.size());
    transform_into(frame, scratch);
    consume_now(scratch);
}
```

`transform_into`/`consume_now` are illustrative application operations, not library functions. This excerpt assumes `consume_now` does not retain a span/pointer after returning. `reserve(n)` alone does not create `n` elements; writing `scratch[i]` after only reserve is invalid. Resizing/reallocation can invalidate stored views. If processing is asynchronous, transfer ownership or use an explicitly bounded buffer pool whose reuse waits for completion.

Reuse is not synonymous with permanent retention. One huge frame can leave every worker holding a huge capacity. Choose a documented retention budget and release/recreate exceptional buffers at a quiescent batch boundary when needed; do not call `shrink_to_fit` every frame. That call is non-binding and may allocate/copy, and allocator release does not guarantee immediate RSS reduction.

**Other grounded changes.** Reserve output vectors when their size bound is known; remove unnecessary intermediate copies; use contiguous batches for uniform data; avoid per-element heap ownership when object lifetime naturally matches a container. Start with standard containers/RAII. Introduce arenas or custom allocators only if allocator overhead remains measured and bulk lifetime/exception/destructor semantics are explicit.

**Correctness/side effects.** A shared scratch vector used simultaneously by multiple workers introduces races. `thread_local` buffers can multiply retained memory across many long-lived threads and complicate service lifecycle; explicit bounded worker contexts make ownership/cost visible. Reuse must reset all logical state, not just vector length, and avoid exposing previous job's sensitive contents.

**A/B verification.** Measure allocation counts/bytes, copy volume, initialization time, first-touch faults, steady-state throughput and peak RSS/PSS. Exercise small→large→small inputs and many concurrent workers; check contents, empty inputs and asynchronous lifetime boundaries. Report whether startup work merely moved out of the benchmark window.

**Prevent recurrence.** State scratch ownership and retention budgets near worker configuration. Add bounded-capacity/reuse only where evidence earns it; do not preallocate the maximum theoretical dataset everywhere.

## 5. Capacity, reclaim and swap: reduce simultaneous live work

**Precondition.** Comparable windows show working-set growth with reclaim/refault/PSI or swapping and worse latency, or an actual process/cgroup memory budget is exceeded. Major faults can be file-backed reads; zero swap does not exclude pressure. Establish the applicable cgroup/host limit and other workloads first.

**Concrete changes:**

1. Bound in-flight jobs and queued payload bytes, not just the number of queue entries. Three giant point clouds can cost more than a hundred small commands. Include scratch, outputs, decoded buffers and replicas in the estimate.
2. Stream/tile data when the algorithm permits, retaining only the required working window. Keep halo/overlap data for neighborhood operations; do not assume each chunk is independent in reconstruction or graph optimization.
3. Release references to completed frames and obsolete caches at clear lifecycle boundaries. Audit hidden shared ownership, retained futures/callbacks and caches that grow by input identity.
4. If independent jobs compete for the same memory budget, reduce concurrency before requesting a larger system limit. If data are repeatedly materialized by neighboring stages, share immutable owned storage or fuse a justified conversion while keeping ownership explicit.
5. For file-backed major faults, compare sequential/chunked access and reuse that fit the actual workload. Prefetch can add traffic and hurt cache; make it a measured optional experiment, not a default API call.

Admission/backpressure is part of behavior: choose whether producers wait, reject new work or drop replaceable frames. Dropping/sliding-window approximation is permissible only when the application's correctness/quality contract allows it. Do not silently discard calibration samples or map observations to improve latency. Blocking a critical producer can deadlock if it must perform work needed to drain the queue; trace the dependency graph.

A useful budget calculation is `in-flight payloads + worker scratch + outputs + caches + safety headroom`, with measured sizes and uncertainty rather than multiplying only input bytes. Queue depth should be observable, so a memory cap does not hide indefinitely accumulating latency upstream.

**Correctness/side effects.** Streaming can change accumulation order, numerical error, global-neighborhood availability and persistence semantics. Releasing a shared buffer can invalidate spans still used by another stage. Cache limits need eviction/lifetime contracts; smaller caches can increase I/O. Lower precision/compression is a separate accuracy-budget decision, not a free memory fix.

**A/B verification.** Repeat a representative long run and burst, including input-size transitions. Check peak and retained RSS/PSS, queue bytes/depth, target faults, system/cgroup reclaim/pressure/swap and completed useful work. Verify no unbounded upstream queue, dropped required results or quality regression. Report end-to-end latency rather than only the stage that now waits less.

**Prevent recurrence.** Put bounds on concurrency, queues and caches at ownership boundaries; expose overload behavior. Test worst supported inputs within the documented resource envelope. Do not “fix” pressure by disabling swap, clearing caches, changing swappiness or raising limits without separate authorization and a deployment-level justification.

## 6. NUMA and TLB: place and partition deliberately, not automatically

**Precondition.** A multi-node workload exhibits node placement/access imbalance plus measured remote-access/locality or throughput evidence. `numa_maps` residency on another node alone does not prove remote accesses caused the slowdown. For TLB work, establish relevant miss/page-walk evidence with architecture-supported events and actual working-set/page sizes.

**Concrete changes:**

- Partition a large mutable working set with the worker group that consumes it; reduce cross-node ownership transfers and shared writes. Allocate/initialize worker-owned data in the intended worker context in an explicitly controlled placement experiment.
- Beware “first-touch” claims: constructing/resizing a zero-initialized vector on the main thread may already fault in its pages before workers fill it. Moving only the later fill loop is not evidence that first touch changed. Conversely allocator reuse, automatic NUMA balancing and existing mappings can defeat a simplistic new-allocation assumption.
- Separate allocation from steady-state measurement only if that matches the real application. If startup/first frame matters, report it too. Verify actual placement after initialization and over time; do not assume scheduler affinity implies memory placement.
- Prefer smaller live working sets, contiguous access and fewer pointer-chasing structures before huge-page experiments for TLB pressure. Huge pages can increase allocation/compaction costs, internal fragmentation and retained memory; a benefit on one traversal can hurt another phase.
- Read-mostly replication per node can reduce remote reads when repeated access and memory headroom justify it. It duplicates memory and introduces update/invalidation costs; never replicate mutable state without a consistency design.

Illustrative ownership arrangement: create lightweight worker contexts centrally, but have the owning worker allocate/initialize its scratch before processing its stable shard. A main-thread `vector<float>(large_size)` followed by worker fills is not equivalent. These are application-local design choices; NUMA policy APIs, binding and huge-page settings require a separately authorized, platform-specific experiment using installed facilities.

**Correctness/side effects.** Partition boundaries, halo exchanges, global reductions and load balance still matter. Binding may fight the scheduler, quotas or heterogeneous cores. Per-node replicas can exhaust the memory budget and create stale results. Large-page alignment/allocation APIs differ across operating systems; preserve matching release functions and error handling.

**A/B verification.** Compare the same input and useful work under equivalent load, recording allocation/startup, residency by node, available supported remote/local event evidence, migrations, bandwidth, latency and memory. Include skewed shards and a fallback when placement requests fail. Treat physical placement and hardware-event support as observations, not assumptions.

**Prevent recurrence.** Make large-buffer ownership and consumption locality understandable in the design. Prefer stable data partitioning with explicit cross-partition operations to scattered ad-hoc affinity calls. Keep topology-sensitive choices optional and documented, not a requirement for ordinary correctness.

## Decision and acceptance record

Use the existing benchmark/report mechanism; a concise entry can be:

```text
Evidence and competing explanations:
Resource envelope (input sizes, CPU constraints, memory budget):
Change and why it targets that evidence:
Correctness/lifetime/ordering/numerical constraints preserved:
Before/after useful throughput + latency + quality:
Before/after relevant counters + peak/retained memory:
Stress/edge cases and failure/shutdown behavior checked:
Trade-offs, rollback and remaining unknowns:
Preventive ownership/budget rule retained in the project:
```

A successful fix can leave a counter high: a better algorithm might do more work per switch, or a correct startup might still fault pages once. Keep only preventive rules supported by the project's failure mode; avoid turning a measured local optimization into a universal prohibition or a new framework.

## Reading pointers and scope

The linked local diagnostics include the primary kernel/proc/cgroup/PSI/NUMA and platform source references and exact collection commands. C++ snippets here are original, scoped excerpts; application identifiers and executor APIs are deliberately not presented as runnable library APIs. Validate complete integrations with the project's actual concurrency, error and numerical contracts. No system setting, new package, remote document or CUDA facility is required to understand these choices.

## Local runnable correctness companion

The [original C++20 remediation examples](../assets/remediation-examples/README.md) provide complete compilable local-aggregation, row-major traversal, close-and-drain bounded-queue and buffer-reuse examples. Their Debug/Release checks validate results/lifecycle, not speed. The scoped snippets in this reference remain integration examples; library/runtime-specific changes still need the actual project and an A/B measurement.
