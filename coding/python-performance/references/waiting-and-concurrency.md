# Waiting, scheduling and capacity

## Low CPU is not automatically inefficient Python

A batch/service operation can wait on storage, remote services, locks, bounded queues or
worker startup. First compare wall and whole-workload CPU and sample stacks during the slow
interval. Correlate request phases, queue depth and throughput. A stack blocked in a read
suggests where time is waiting; it does not establish whether the disk, network or upstream
producer is the root cause. Use available I/O latency and utilization evidence to distinguish.

For repeated tiny I/O, batch within response/cancellation bounds and reuse existing
connections. For downstream overload, bound submissions and apply backpressure rather than
spawn unlimited tasks. Verification includes errors, queue length and p95 at the same offered
load; prevention is an explicit capacity policy. Increasing timeout only hides the symptom.

## Async does not remove synchronous work

An event loop executes tasks cooperatively. A long synchronous callback or CPU loop prevents
other tasks on that loop from advancing. Enable local asyncio debug logging when appropriate
and set `loop.slow_callback_duration` to a workload-relevant diagnostic threshold. Debug mode
is not the production timing baseline. Inspect lag and task backlog, not only function totals.

Move blocking I/O to an existing bounded executor or use a compatible async API. Pure Python
CPU work may need a process/native implementation. Preserve cancellation, exception propagation and
shutdown behavior.

With Pyinstrument async-aware modes, waiting is attributed to the awaiting context. That
wall time is not CPU consumed by the coroutine. Cross-context work requires careful mode
selection; capture a representative whole operation if request-local views are misleading.

## Threads, GIL and nested teams

Record both build capability and actual GIL state after relevant application imports.
Normal GIL builds can still execute native routines concurrently when those release the GIL.
Do not infer either behavior from the Python version number alone. Shared-state operations
still need logical synchronization: changing interpreter mode does not make compound updates
atomic or algorithms thread-safe.

Budget usable CPUs from affinity/container quota, not just host core count. A Python worker
pool invoking multithreaded BLAS can multiply runnable threads. Compare worker counts and
native team sizes at fixed total work; prefer one deliberate parallel layer, then validate
latency and throughput. Configure supported native limits before library initialization, or
use its documented local control; do not globally alter unrelated workloads. `python-numerics`
provides the library-specific thread policy.

More threads than cores is evidence to investigate, not a verdict: waiting-heavy tasks can
benefit. Excess runnable threads plus context switches, CPU throttling and worsening useful
throughput support an oversubscription hypothesis. Reduce teams/queue depth and repeat. High
context switches alone do not distinguish lock waits, I/O or preemption.

## Processes and synchronization

Processes add startup, serialization, IPC and duplicated/retained memory. Batch enough work
to amortize them; bound submitted futures and result buffering. Record the actual start method
and avoid assuming inherited globals/fork on every Python/OS version. Main-guard process
entrypoints and picklable callables are needed for spawn-style starts. Never force fork into
a threaded/native runtime as a quick performance fix. Shared memory needs explicit ownership,
cleanup and synchronization, not just a zero-copy claim.

For locks, first measure wait/hold duration and identify the invariant. Move independent
parsing/I/O outside a critical section only if snapshot/publication semantics remain valid.
Shard state only when access patterns justify it. Native false sharing needs cache-line and
access evidence before padding; padding costs footprint and may worsen locality. Prevent
regressions with bounded workers, documented ownership and cancellation/drain tests.

## Provenance

- Async behavior/debugging: https://docs.python.org/3.14/library/asyncio-dev.html
- Async attribution: https://github.com/joerick/pyinstrument/blob/main/docs/how-it-works.md
- GIL build and runtime distinctions: https://docs.python.org/3.14/howto/free-threading-python.html
- Process lifecycle/start methods: https://docs.python.org/3.14/library/multiprocessing.html
