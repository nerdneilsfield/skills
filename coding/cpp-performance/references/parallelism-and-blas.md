# CPU parallelism and BLAS: one shared policy

This is the single owner for application/solver/BLAS thread budgets, runtime-control selection and the outer-versus-inner experiment. Both `cpp-performance` and `cpp-numerics` link here; numerical modeling and quality acceptance stay in [sparse/BLAS numerical validation](../../cpp-numerics/references/sparse-blas-validation.md). Do not load every performance reference: read this when nested pools, solver/BLAS threading or parallel-work ownership is actually implicated.

## Establish the resource and ownership contract

Record the application's workers, OpenMP teams, solver settings, BLAS implementation/build, active runtime and phase-specific behavior. A configured maximum or environment variable is not proof of effective runnable threads. Libraries may reuse, serialize or dynamically resize teams; `outer × inner` is potential demand, not an observed count.

Use the actual allowed CPU masks/cpuset, visible ancestor quota, shared cgroup peers and memory budget. Host logical CPU count is not a guaranteed allocation, and physical cores are not a universal optimal worker count. When capacity is uncertain, use [scheduler/thread capacity](scheduler-thread-capacity.md) and the [proc sampler](proc-sampler-guide.md) for bounded evidence rather than inventing a precise budget.

Choose one orchestration-level CPU-work budget. Pass it through the existing executor and inner library configuration, instead of letting each component independently choose host `hardware_concurrency()`. Keep CPU-heavy concurrency separate from outstanding I/O. Do not build a new scheduling framework for one setting.

## A/B experiment owned here

Keep identical successful work, input identity, optimized build, warmup policy, numerical/output budget and machine conditions:

| Experiment | Outer jobs | Inner solver/BLAS | Question |
| --- | --- | --- | --- |
| Serial reference | 1 | 1 | Work/correctness reference |
| Outer owner | relevant bounded k | 1 | Independent jobs scale? |
| Inner owner | 1 | relevant bounded k | Large numerical kernel scales? |
| Existing or justified nested setting | bounded current/test value | bounded current/test value | Explain a regression; not the default |

Sweep a few values below/around/above plausible effective capacity, not every combination. Include small and large representative jobs; fixed 3×3/6×6 kernels and large dynamic GEMM/solves have different overheads. If input work changes through dropped frames, fewer iterations or weaker tolerances, the timing is not a like-for-like scaling result.

Measure useful throughput, appropriate tail latency, CPU time per completed item, active-thread coverage, runnable delay/switches, throttling and memory. A low switch count is not the objective. Flat scaling can be bandwidth saturation or serial work; worse scaling can be oversubscription, lock contention or scheduling overhead. Neither alone proves false sharing. Follow the evidence into the relevant local reference only if needed.

## Select actual backend controls, offline

1. Identify the pinned backend version, build flags and linked threading layer from existing local build records/configuration. If unavailable, record the limitation; do not guess or download another library.
2. Check whether controls are process-global, thread-local, per-call or read at startup. Global changes from concurrently executing jobs can race or disturb unrelated work; set them before workers start or use a documented local mechanism where available.
3. For startup controls, run each configuration in a fresh process. Record conflicting variables/settings instead of silently stacking them. Do not modify a service's global environment as part of read-only observation.
4. Verify effective runtime behavior using installed local inquiry APIs, thread samples or a permitted profiler. Without that evidence, the requested setting is not a verified team size.

### OpenBLAS

A confirmed pthread OpenBLAS build commonly uses `OPENBLAS_NUM_THREADS=1` to request a single inner thread. For example, in a Unix-like shell, with an already built authorized finite application:

```sh
OPENBLAS_NUM_THREADS=1 ./existing-app representative-input
```

This changes only that launched process's environment and requires permission to run it. It is **not** a universal instruction for an OpenMP OpenBLAS build. Build/runtime controls differ, and an application may override them through an API. Verify local build type, precedence and active threads. Do not assume the same variable controls Eigen's own parallel paths, another BLAS, OpenMP application workers or Ceres.

### oneMKL

Identify the selected threading layer first: sequential, an OpenMP runtime, or oneTBB. OpenMP-oriented settings do not govern every TBB execution path. For a verified OpenMP-threaded oneMKL build, documented MKL-specific controls such as `MKL_NUM_THREADS` can select its team budget; they are not an application-wide promise. Do not infer oneTBB control from the presence of an MKL/OpenMP variable, mix incompatible runtimes casually, or copy an older platform's API name without checking the installed headers/build.

The references below use versioned Linux 2025.1 documentation, not an assumption that every project uses that release or Linux. If the project's retained docs/headers describe a different supported runtime, follow that version. No internet is required to apply the experimental method above.

## Correctness, remedies and prevention

Fewer workers can change ordering, deadlines and progress behavior. A worker waiting on a task scheduled to the same exhausted pool can deadlock; reducing a pool does not repair that dependency. Library global state must be reentrant under the proposed call pattern. Floating reductions can change rounding/convergence; use the numerical skill's predeclared accuracy and geometry criteria.

For many independent frames/tiles, test the outer-owner configuration. For one large solve, test the inner-owner configuration. Preserve the existing pool/library interfaces and revert a change that regresses quality, memory or required latency. If changing task granularity, cancellation or buffer ownership is necessary, continue into [thread/memory remedies](thread-and-memory-remedies.md), not a second independent thread-control policy.

Prevent recurrence by keeping one explicit inspectable budget and documenting which layer owns parallelism for each phase. Retain a representative nested-call workload and error/shutdown check when those behaviors changed. Stop when the requested target is met by a maintainable measured configuration; do not pursue a magic worker count, lock-free redesign or new framework without further evidence.

## Provenance

- [OpenBLAS runtime variables](https://www.openmathlib.org/OpenBLAS/docs/runtime_variables/): match the retained release and pthread/OpenMP build.
- [oneMKL Linux 2025.1 threading](https://www.intel.com/content/www/us/en/docs/onemkl/developer-guide-linux/2025-1/improving-performance-with-threading.html): a versioned official reference, not the old Windows edition.
- Resource/scheduler evidence and kernel sources are in [scheduler/thread capacity](scheduler-thread-capacity.md). Source links are provenance, not runtime downloads.
