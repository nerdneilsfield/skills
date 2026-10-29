# CPU caches, cache-line sharing and contention

Use when CPU time scales badly, memory access dominates, or thread counts rise without useful throughput. These are offline procedures for an authorized local workload. Install nothing, change no security settings, and use no GPU/CUDA tooling. Keep the baseline from `measurement-and-report.md`; sampling is evidence collection, not a speedup claim.

## Separate four different hypotheses

| Hypothesis | Expected supporting evidence | A discriminating experiment |
| --- | --- | --- |
| Capacity/locality misses | Hot working set or traversal outruns useful cache locality; memory-load stalls in the relevant region | Same work with blocked/compact access or a size sweep across working-set regimes |
| Bandwidth saturation | Throughput stops scaling while measured relevant memory traffic approaches a stable plateau | Fewer workers or fewer bytes per useful operation; include conversion/initialization cost |
| Cache-line ownership traffic | Multiple CPUs access a hot line with a writer; cache-to-cache samples point to that line/code | Establish object/offset ownership, then separate independent fields or reduce updates |
| Lock serialization | Waiters or spinning callers converge on a shared critical section; useful parallel work collapses | Measure wait/hold distributions and reduce/shared-state work rather than blindly pad |

These can coexist. A high generic cache-miss count does not identify which one applies. First identify the time-consuming stage and normalize counters by completed useful work (frames, points, residuals), not just process lifetime.

## 1. Inventory topology and supported measurements

On an installed Linux toolchain:

```sh
lscpu -e=CPU,CORE,SOCKET,NODE,ONLINE
lscpu --caches
perf --version
perf list
```

Older `lscpu` may lack columns or `--caches`; use its local `--help` and readable sysfs instead. For an actual CPU in the target affinity mask, inspect `/sys/devices/system/cpu/cpuN/cache/index*/` files `level`, `type`, `size`, `coherency_line_size` and `shared_cpu_list`. This reports hardware topology, not the target's resident working set. Do not assume every CPU has the same cache layout, that a cache-size total is per core, or that all SMT siblings provide independent execution/cache capacity. Virtualized topology can differ from the physical host. [lscpu manual](https://man7.org/linux/man-pages/man1/lscpu.1.html)

Generic aliases are a starting vocabulary, not a cross-CPU event specification. `cache-references`/`cache-misses` need the platform's definition; they do not universally mean L1 data references/misses. Hybrid CPUs can expose separate PMUs. Retain event names, privilege modifiers, enabled/running time and tool/kernel/CPU identities with results.

## 2. Small process-scoped counter passes

For a **known finite, trusted** invocation; choose a new output path if redirecting results:

```sh
perf stat -r 5 -e task-clock,context-switches,cpu-migrations,page-faults -- ./app representative-input
perf stat -r 5 -e cycles,instructions,cache-references,cache-misses -- ./app representative-input
```

Run small event groups separately when necessary. Check unsupported/not-counted events and multiplexing: a scaled value is not a full-duration simultaneous observation. Changing the workload between counter passes invalidates straightforward ratios. If supported, follow with locally listed L1/LLC/TLB/load-stall events relevant to the hypothesis; do not copy raw event encodings from another CPU generation. Avoid unschedulable large event groups. `:u` limits to userspace, which can deliberately exclude relevant kernel time. [perf stat manual](https://man7.org/linux/man-pages/man1/perf-stat.1.html)

Useful derived quantities, only with compatible event meanings and sampling windows:

- instructions per cycle = instructions / cycles; not a universal efficiency grade;
- misses per thousand instructions = misses / instructions × 1000; still not bytes or latency;
- misses per frame = misses / successful frames; catches changes in work amount;
- measured bytes/s and bytes/frame from supported memory-controller events, if legitimately available.

Do **not** multiply generic cache misses by a guessed 64-byte line and call it DRAM bandwidth. Prefetch, writeback, cache-to-cache transfer, merge behavior and event definitions break that inference. Uncore memory-controller counters commonly describe a socket/domain, not a process; competing workloads can dominate them. Use them only with authorized collection and scope attribution explicitly stated.

For a matrix/point-cloud workload, compare representative fixed problem sizes before sweeping size. Keep allocation/first-touch and cold-vs-warm policy consistent. A cache-fitting synthetic kernel cannot establish end-to-end speedup when input conversion or solver setup dominates.

## 3. Cache-line ownership: true sharing versus false sharing

**True sharing:** workers modify or depend on the same logical datum, e.g. one queue tail, global atomic counter or lock state. Moving that datum to a private cache line does not remove its serialization.

**False sharing:** independent logical fields occupy the same coherence line, and at least one is written while another CPU accesses the line. A read-mostly field beside a frequently modified counter can participate; two writers are not required. Read-only sharing alone is not a cache-line invalidation problem. [Kernel false-sharing guide](https://docs.kernel.org/kernel-hacking/false-sharing.html)

Before blaming false sharing:

1. Identify the hot data address/line and the accessing instructions/TIDs, not just a hot struct name.
2. Map offsets to fields and their real access/ownership pattern. Use matching binary debug info, source layout, `offsetof`/`sizeof` for suitable types, or an already installed `pahole` for supported debug types. Do not guess layout from declaration order when inheritance/ABI/packing is involved.
3. Verify whether updates target independent fields or the same field. Examine lifetime/allocation: reused addresses can represent different objects at different times.
4. Change one thing: per-worker accumulation then reduction, separate hot independent write fields, batch publication, or reduce shared-counter frequency. Keep required atomic/order semantics; replacing atomics with a race is not an optimization.
5. Recheck both throughput/latency and the affected line traffic, with the same workload. Padding increases footprint and may hurt locality elsewhere.

Example diagnosis, not a universal layout prescription: worker A updates `counters[0]`, worker B updates `counters[1]`, both atomically. If their addresses fall in one coherence line, the fields are logically independent but may bounce ownership. Compare a per-worker layout separated at the **measured target** coherence granularity against packed counters. C++ `alignas` aligns the object start but does not automatically separate every member. `std::hardware_destructive_interference_size`, when available, is an implementation hint with ABI/build implications, not a runtime probe or guaranteed universal cache-line size. Check array element stride as well as alignment.

## 4. perf c2c when the hardware actually supports it

First inspect local `perf c2c record -h` and, where supported, `perf c2c record -e list`. The needed PMU facilities differ across Intel, AMD, Arm and PowerPC and may be absent/unsupported on the current hardware/kernel. A permission or capability failure is not a zero-sharing result. [perf c2c manual](https://man7.org/linux/man-pages/man1/perf-c2c.1.html)

For a bounded trusted workload, this forwards normal recording options after the separator (verify local help if an older version parses options differently):

```sh
perf c2c record -- -o c2c-app.data -g -- ./app representative-input
perf c2c report -i c2c-app.data --stdio
```

Use a fresh destination rather than overwrite an earlier trace. Keep matching local binaries/symbols; do not enable symbol-server acquisition on an offline machine. Inspect line addresses, instruction locations, offsets, TIDs and available local/remote HITM or peer-sharing columns. Then connect the samples to the actual field ownership. A dominant HITM line may be a legitimately shared synchronization word: samples alone do not distinguish harmful false sharing from required communication. Hardware sampling/filtering means absent samples are not proof of absence.

If c2c is unavailable, do a controlled layout/update-frequency experiment plus regular timing and supported CPU counters. The conclusion is then “layout experiment supports a sharing hypothesis,” not “c2c confirmed false sharing.” No need to install a profiler or grant privileges merely to continue useful diagnosis.

## 5. Lock contention and wait stacks

CPU samples alone underrepresent threads sleeping on a mutex; a low-CPU slow process may spend most time off CPU. Conversely, user-space spinning can show high CPU without entering a blocking syscall.

- Inspect per-thread CPU and voluntary/involuntary switch rates, then bounded repeated thread stacks or a supported off-CPU/scheduler trace. A repeated futex wait is a clue, not identification of a particular C++ mutex owner or proof of deadlock.
- For an authorized diagnostic code change, measure monotonic acquisition-start→success (wait), success→unlock (hold), contention count and tail distributions around the suspected critical section. Buffer/aggregate locally and avoid logging under the hot lock. Measure instrumentation overhead; do not ship a new global tracing framework just for one question.
- Distinguish lock wait from condition-variable idle wait, barrier imbalance, I/O, allocator contention and scheduling delay. Correlate timestamps with owner activity rather than sum overlapping waiter times into wall-clock time.
- Inspect critical-section size, hot allocation/logging, lock ordering and work partition. Batching can reduce acquisition cost but lengthen hold/tail latency. Sharding may increase memory or complicate invariants; verify correctness and quality as well as throughput.

`perf lock` primarily exposes kernel lock instrumentation; it is **not** a universal pthread/std::mutex profiler. Check locally available events and tooling before using `perf lock record/report` or BPF contention modes. Kernel tracing/BPF may require unavailable permissions and instrument a different scope than the application mutex. Do not claim a userspace lock is uncontended because a kernel-lock report is empty. [perf lock manual](https://man7.org/linux/man-pages/man1/perf-lock.1.html)

For an already installed syscall tracer, a short authorized `strace -f -c -e trace=futex -p PID` can summarize futex calls, but it changes timing and must be ended explicitly after the bounded observation. It misses uncontended user-space fast paths and spins, and futex time includes more than mutex ownership. Prefer the less intrusive sampler first; do not use syscall tracing as the performance baseline.

## 6. Non-Linux equivalents and limits

- **Windows:** installed WPR/WPA CPU Usage (Precise) views can relate ready/running/waiting transitions; CPU sampling shows hot spin paths. Use an appropriate already installed vendor profiler for supported cache/PMU data. WPA scheduler evidence is not a drop-in c2c ownership trace. Avoid changing recording sessions or symbol-server policy implicitly.
- **macOS:** installed Instruments Time Profiler/thread-state views separate running from waits; supported processor-counter instruments depend on hardware/tool version. Do not label generic samples as Intel HITM evidence on Apple Silicon. Use controlled layout experiments when precise sharing instrumentation is unavailable.
- On all systems record what was actually available, attribution scope and perturbation; no automatic installations or privileged policy changes.

## Offline interpretation exercises

| Observation | Defensible next action, not a verdict |
| --- | --- |
| LLC misses rise but elapsed time falls and useful work doubles | Normalize by work; do not reject the change on raw misses |
| One hot c2c line is the same atomic queue head for every worker | Investigate true sharing/algorithmic serialization, not only padding |
| Distinct per-worker counters share a line; separating them reduces line traffic and runtime | Evidence supports false sharing; test memory footprint and other workloads |
| 32 workers spend time in futex waits while one owner allocates under a lock | Measure hold/wait distribution and move safe unrelated work outside the lock |
| More workers stop improving throughput; socket traffic is stable but competing process load changes | Do not attribute socket bandwidth to the target without isolation/control |

Record: workload/build/CPU → measurement availability and scope → specific hot code/line/lock → falsifiable hypothesis → focused change → comparable time, traffic and correctness → unresolved platform limitations. Sampling commands here were documented, not claimed executed.

## From diagnosis to a fix

Use [concrete remedies and preventive patterns](cache-and-synchronization-remedies.md) for evidence-gated implementation choices, correctness/side effects and A/B acceptance. Do not stop at a counter label or apply every remedy at once.
