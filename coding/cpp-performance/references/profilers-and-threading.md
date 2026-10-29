# CPU profiling, memory behavior and thread ownership

Load when timing identifies a real problem but the cause is uncertain, or thread scaling changes unexpectedly. Commands below are examples for an authorized, trusted workload and installed tools. They are not executed by reading this file. CPU only; no GPU tooling is required.

## Choose the cheapest informative view

| Question | Start with | Read the evidence as |
| --- | --- | --- |
| Where does CPU time go? | Sampled call stacks | Inclusive time includes callees; leaf/self time identifies work in that frame |
| Is low throughput actually waiting? | Thread states/scheduler or bounded stack observations | Low CPU can reflect I/O/locks/producer starvation, not efficient code |
| Is memory traffic the bottleneck? | Hot access pattern plus relevant cache/bandwidth counters | A high miss count alone needs workload size/rate and CPU context |
| Do allocations dominate? | Available allocation profiler or scoped counters | Include frequency/size/lifetime and stack attribution, not only bytes live |
| Why do more threads slow it down? | Thread-count sweep + scheduler/call stacks | Check nested pools, contention, imbalance, false sharing and bandwidth saturation |

Begin process-scoped, bounded collection. System-wide tracing may expose other users/processes and adds scope; do not silently escalate. Profilers write artifacts that can include symbols, paths and workload data. Retain only needed recordings and review before sharing.

## Linux perf: a bounded first pass

Inspect locally available capabilities:

```sh
perf --version
perf list
```

Then, for a known finite workload:

```sh
perf stat -r 5 -- ./app representative-input
perf record -o perf-app.data -g -- ./app representative-input
perf report -i perf-app.data --stdio
```

The workload must terminate or have an existing duration/input limit; do not profile an unbounded service accidentally. `perf-app.data` is a chosen new output file, not an artifact to overwrite blindly. Start with default events; add a small supported event set after a question exists. Five repetitions illustrate syntax, not adequate sample size for all cases.

- Check “not supported/not counted,” event scaling/multiplexing and permission errors. Missing data is not zero cost.
- Verify the recording contains the intended process/code and symbols. Optimized builds need a viable stack-unwinding strategy. If call stacks are truncated, consider a compatible frame-pointer build or supported DWARF call-graph mode; do not compare heavily instrumented timing with the baseline as if identical.
- Read both inclusive and self costs. Expensive solver callers can aggregate child work; a tiny wrapper high in an inclusive report may not be the optimization target.
- Attribute hot functions to the actual binary/revision; stale symbols or a later rebuild can make source attribution wrong.
- Counters such as cycles, instructions, cache misses or HITM are architecture/workload-specific clues. No fixed IPC or miss threshold proves a bottleneck across CPUs.

If permission blocks collection, record it and use available application stage timings or user-space sampling. Do not change kernel security settings, install packages or request system-wide access automatically. A timing-only experiment remains useful but its bottleneck explanation is tentative.

## macOS: Instruments / local Xcode tools

With Instruments already installed, choose the target executable/process and an appropriate CPU sampling instrument such as Time Profiler. Record only a representative bounded interval, verify symbols resolve, then inspect call trees and thread activity. Distinguish wall time from CPU samples and expand callers to see stage attribution. Use an allocation instrument only when allocation is the question.

For local command discovery, `xcrun xctrace list templates` lists the installed templates, and `xcrun xctrace help record` describes that version's recording syntax. Template names/options vary; do not invent an exact command from a different Xcode version. No Xcode installation or account sign-in is required merely to use this guidance: if absent, report sampling unavailable and use the application's existing stage timers/measurements.

## Windows: WPR/WPA when available

Check local recorder capabilities and whether another session is active:

```text
wpr -profiles
wpr -status
wpr -help start
wpr -help stop
```

Use retained local symbols when offline; unavailable symbols remain a stated attribution limitation, not a reason to fetch from symbol servers. Select the supported CPU profile with the scope/privileges needed for this task. Start it only if authorized and it will not disrupt an existing recording; run the bounded workload; stop and save to a new ETL path. Inspect the trace in WPA with symbols for the matching build, CPU usage/call stacks and thread scheduling views. Profile identifiers depend on installed WPR; do not hardcode a profile from another machine. Do not cancel another user's session to make a command succeed.

WPR setup or some profiles may require permissions not currently available. Use an already-supported IDE/user-space profiler or application-level timing as a limited fallback. Do not modify registry/security settings or install the Windows toolkit implicitly.

## Interpreting memory and compiler evidence

Before changing layout, sketch the hot loop's accessed fields, stride, working set and ownership. Test a layout change with actual sizes; SoA can help one traversal while adding conversion costs elsewhere. Padding to reduce false sharing increases footprint and can make other accesses worse.

For a hot loop where vectorization is relevant, inspect compiler optimization remarks and generated code using already installed tools. A compiler declining vectorization can indicate dependencies, aliasing or unsuitable loop shape; do not override it with an unsafe alias promise. Ensure vectorized loops handle remainder elements and alignment, and verify deployment ISA or dispatch behavior.

Do not start with assembly when most time is allocation, a mutex, or an avoidable whole-dataset copy. Changing precision/reassociation/FMA behavior needs numerical quality checks, not only an instruction-count reduction.

## Thread ownership experiment

Use [parallelism/BLAS policy](parallelism-and-blas.md) for the canonical inventory, budget, experiment matrix and backend-control procedure. This profiler reference supplies observations, not a second configuration policy. A scaling plateau still needs mechanism evidence; it does not by itself prove false sharing or oversubscription.

## Offline review fixtures

- **perf unavailable + good repeated timing:** timing comparison may stand; causal/profile explanation remains unverified. Do not install perf or fabricate a recording.
- **hot inclusive wrapper:** inspect children/self time before rewriting the wrapper.
- **outer 8 × inner 8 with poor scaling:** identify actual pools and compare serial/outer-only/inner-only configurations; do not assume 64 runnable threads without observation.
- **AVX proposal for memory-bound loop:** check work/layout and measured memory limitation first; wider vectors are not inherently a fix.

## Provenance

- [Linux perf tutorial](https://perfwiki.github.io/main/tutorial/) and [Intel linux-perf skill](https://github.com/intel/intel-performance-skills/blob/main/skills/linux-perf/SKILL.md).
- Apple [Instruments](https://developer.apple.com/documentation/xcode/instruments) and local `xctrace` help; installed Xcode determines available instruments and CLI syntax.
- Microsoft [WPR options](https://learn.microsoft.com/en-us/windows-hardware/test/wpt/wpr-command-line-options), [WPA](https://learn.microsoft.com/en-us/windows-hardware/test/wpt/windows-performance-analyzer).
- [OpenBLAS](https://github.com/OpenMathLib/OpenBLAS), [oneMKL threading guidance](https://www.intel.com/content/www/us/en/docs/onemkl/developer-guide-linux/2025-1/improving-performance-with-threading.html): the linked version is not a promise about another installed runtime.

External pages are optional provenance. The workflow, interpretation rules, fallback and review fixtures above remain usable offline with the tools already present.

## Deeper system evidence

For actual shared-line/cache/lock investigation use [cache lines and contention](cpu-cache-sharing-contention.md); for scheduling and usable CPU capacity use [scheduler and thread capacity](scheduler-thread-capacity.md); for faults, swap, pressure and NUMA use [memory pressure and NUMA](memory-pressure-numa.md). The local [proc sampler](proc-sampler-guide.md) records interval evidence without requiring perf or changing permissions, but cannot replace hardware counters or wait stacks.
