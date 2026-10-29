---
name: cpp-performance
description: Use when C++ CPU latency, throughput, memory use, cache/cacheline contention, context switching, thread oversubscription, paging, or scalability is a measured problem or an explicit optimization target.
---

# Measured C++ CPU optimization

Optimize the bottleneck of a representative workload, not a list of coding preferences. Use shared `cpp` conventions; use `cpp-debug` first for undefined behavior and `cpp-numerics` for floating-point/solver changes. CUDA is deferred and not part of this skill.


Shared language policy is `cpp`; build/vendor changes use `cpp-project-init`, uncertain UB uses `cpp-debug`, and model/precision questions use `cpp-numerics`. If a needed named skill is missing, ask the user to install that exact skill from this bundle. Do not globally search, fetch a substitute, automatically install or invent it; continue only independent measurements/reasoning.

## Start with the matching symptom, not all references

Read the matching row first. These are routes, not cumulative requirements. Follow a related reference when evidence crosses layers (for example runnable pressure plus memory stalls); do not enforce an artificial one-reference limit or preload the entire directory.

| Present question / evidence | First local reference | Continue only if needed |
| --- | --- | --- |
| No trustworthy baseline, noisy timing, unclear acceptance | [Measurement/report](references/measurement-and-report.md) | [Existing sample JSON tool](references/local-benchmark-tool.md) |
| Need the platform's CPU/stack profiler | [Profiler selection](references/profilers-and-threading.md) | Relevant mechanism below |
| Cache/TLB/bandwidth, shared lines or lock contention | [Cache/shared-line evidence](references/cpu-cache-sharing-contention.md) | [Cache/synchronization remedies](references/cache-and-synchronization-remedies.md) |
| Context switches, migrations, runnable delay, usable CPU/quota | [Scheduler/thread capacity](references/scheduler-thread-capacity.md) | [Read-only PID sampler](references/proc-sampler-guide.md) |
| Nested application/solver/BLAS teams or thread-budget selection | [Parallelism/BLAS policy](references/parallelism-and-blas.md) | Capacity evidence or numeric quality as indicated |
| RSS/PSS, faults, reclaim, swap or NUMA | [Memory/NUMA evidence](references/memory-pressure-numa.md) | [Thread/memory remedies](references/thread-and-memory-remedies.md) |
| A cause is already supported; need a scoped fix/prevention | [Cache/synchronization remedies](references/cache-and-synchronization-remedies.md) or [thread/memory remedies](references/thread-and-memory-remedies.md) | [Runnable correctness examples](assets/remediation-examples/README.md) |
| Eigen/solver model, data layout or numerical quality fails | `cpp-numerics` | Its relevant model/validation reference |

Tool invocation, schemas, permissions, examples and limitations live with the matching local guide. References are self-contained offline; source links are provenance. If a cross-skill owner is missing, name the exact skill for the user to install from this bundle, not a global search or automatic download.

## Define a comparable baseline

Record the required metric and acceptance budget: throughput, median/tail latency, peak memory, allocations or scaling. Select realistic input identities, sizes, seeds and output correctness checks. For SLAM/reconstruction, distinguish tracking, feature/point processing, correspondence, residual evaluation, linear solve and data conversion before choosing a kernel benchmark.

Measure a release-like optimized build with symbols suitable for profiling. Record revision, compiler/flags, CPU/ISA, OS, dependency versions, thread counts and relevant affinity/power settings. Sanitizer Debug runs diagnose behavior; they are not the baseline for a production speedup.

Control warmup, cache state and competing load according to the workload. Repeat enough to expose variation and record the measurement spread; alternate before/after runs when drift matters. Use the same inputs and machine conditions. Treat a difference inside noise as inconclusive, not a win.

## Profile before selecting a change

| Evidence | Inspect next |
| --- | --- |
| CPU hot loop | Algorithm/work count, compiler vectorization report, generated code where informative |
| Allocation/copy hotspot | Ownership, temporary materialization, buffer reuse, realistic lifetime costs |
| Memory stalls | Access locality, working-set size, layout/strides, bandwidth and cache behavior |
| Weak scaling | Lock contention, scheduler activity, false sharing, load imbalance, nested thread pools |
| Solver-heavy time | Model/sparsity, residual versus solve time, backend and thread policy; use `cpp-numerics` |
| Mostly waiting | I/O, producer/consumer boundaries or external service; do not optimize arithmetic blindly |

Use available platform tools: Linux perf for CPU counters/sampling, macOS Instruments for CPU profiling, Windows WPR/WPA or an available supported profiler. Tool absence or permissions are a stated limitation, not permission to claim a profile was collected. Request authorization before installing tools or changing privileged settings.

An illustrative Linux experiment, only with available perf permissions and a known workload:

```sh
perf stat -r 5 -- ./app representative-input
perf record -g -- ./app representative-input
perf report
```

Choose events and stack-unwinding options for the actual CPU/build. The repetition count is illustrative, not statistical certification. Counter availability, multiplexing and sampling overhead affect interpretation. IPC, cache misses and HITM are clues, not architecture-independent pass/fail thresholds. Profiles of a microbenchmark must be checked against end-to-end behavior.

## Change one supported cause

Prefer reducing needless work, allocations, copies or poor locality before hand-written intrinsics. Retain observable semantics and the ownership model. `std::move`, `emplace_back`, wider SIMD, lock-free containers, custom allocators and extra threads are hypotheses, not guaranteed improvements.

For SIMD, establish deployment ISA/dispatch compatibility, bounds/tails and alignment. Do not add `restrict`-like non-alias promises without proof. For layout changes, check sharing/false sharing and interface costs rather than assume padding or SoA always wins.

For thread budgets, nested pools and BLAS controls, use the single [parallelism/BLAS policy](references/parallelism-and-blas.md); keep this entrypoint from restating that procedure.

Floating-point reassociation, FMA changes, lower precision and fast-math require explicit numerical/compatibility acceptance criteria. Verify finite values, accuracy and downstream convergence/geometry; a faster kernel with degraded SLAM pose or failed cases is not accepted on time alone. Do not silently enable fast-math globally.

## Remedy, verify, then prevent recurrence

Do not stop at naming a bottleneck. For supported causes provide the smallest concrete change, the preconditions that make it valid, ownership/order/numerical risks, and the exact before/after check. Apply authorized changes in the existing design; reuse its pool, buffer and synchronization mechanisms rather than adding a framework.

Separate a measured remedy from a candidate experiment. Tie prevention to the demonstrated mechanism: stable layout/lifetime contracts, one parallelism budget, bounded work/memory, short invariant-preserving lock scope, and representative regression workloads as relevant. Padding, lock-free structures, affinity, huge pages or system tuning require specific justification, not a checklist.

Accept only when correctness/quality, useful work, latency and resource budgets hold under comparable measurements. Once the requested target is met with a maintainable change, stop. If not met, keep the remaining uncertainty explicit and choose the next discriminating experiment instead of stacking unmeasured tweaks.

## Recheck and report

Run the same functional/quality check and representative timing after the focused change. Include relevant boundary sizes and a non-hot-path regression where the optimization changes shared behavior. Revert or revise a change that regresses correctness, memory or the required latency metric.

Report a compact comparison:

| Item | Record |
| --- | --- |
| Workload/environment | Input identity, revision/build, CPU and threads |
| Before / after | Metric, units, repeated-run spread and correctness/quality result |
| Explanation | Profile evidence, changed cause and scope |
| Limits | Unmeasured platforms, unsupported counters, noise or untested input regimes |

Without comparable measurements, report a proposed experiment rather than an established speedup. If timing improves without profile evidence, distinguish the measured change from its unverified causal explanation. Do not build a benchmarking framework or run all diagnostics for an unrelated source edit.

## References

- Intel's [linux-perf](https://github.com/intel/intel-performance-skills/blob/main/skills/linux-perf/SKILL.md) and [performance-patterns](https://github.com/intel/intel-performance-skills/blob/main/skills/performance-patterns/SKILL.md): reference workflows, not universal thresholds or code to copy.
- [Linux perf wiki](https://perfwiki.github.io/main/), [Intel optimization manuals](https://www.intel.com/content/www/us/en/developer/articles/technical/intel64-and-ia32-architectures-optimization.html), [Agner Fog resources](https://www.agner.org/optimize/): consult target/version-specific material; do not mirror manuals.
- [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines) Per rules; [Effective Modern C++ author materials](https://www.aristeia.com/EMC%2B%2B.html) and [A Tour of C++](https://www.stroustrup.com/tour3.html) for language/container costs. Read the relevant legal source, not an unlicensed book copy.
