# Read-only Linux process/thread/system interval evidence

Use this helper for a first interval record of CPU consumption, scheduler counters, faults, system pressure and visible CPU capacity. It is not a replacement for hardware-event profiling or off-CPU stack tracing. It does not prove a specific mutex caused a wait, identify a contended cache line, measure cache misses/bandwidth, or attribute system swap to a process.

## Run against an authorized target

Prerequisites: Linux with readable `/proc`, already installed Python 3.9+ standard library. No packages, network, sudo, profiler installation or security changes. The target must be one the user has authorized you to inspect. The sampler does not launch it, attach a debugger, send signals, open its memory or change its settings.

From this skill directory:

```sh
python3 scripts/sample_linux_proc.py --help
python3 scripts/sample_linux_proc.py --pid 12345 --duration 10 --interval 1 --max-threads 64
# Optional intentional shell write, after choosing a new destination:
python3 scripts/sample_linux_proc.py --pid 12345 --duration 10 --interval 1 > sample.jsonl
```

Replace `12345` with the verified intended PID. The examples are not a request to inspect that literal process. Use an explicit Python 3 executable if `python3` is not present; Windows/macOS do not have Linux proc semantics and this script rejects them. Their alternate tools are documented in the CPU/memory references, not emulated here.

Add `--smaps` only when PSS/private/swap-sharing information is needed. `smaps_rollup` can require additional permissions and kernel work; it is deliberately off by default. Missing access remains explicit. Do not escalate privileges to fill a field without authorization.

## Bounded collection and output

- Duration is >0 and <=3600 seconds; interval >=0.1 second and <=duration; at most 600 requested intervals.
- Default max threads is 64, configurable 1..256. At most 4096 task directory entries are scanned. Lower numeric TIDs among that scan are selected; this is not a representative random sample or a “hottest threads” ranking. Increase within the supported bound or choose a smaller justified target when important threads are omitted.
- Each pseudo-file read is capped at 256 KiB, collected error entries at 256, total JSONL output at 16 MiB including a final bound notification. Limits are reported in the header. Truncation is visible, not silent success for all threads.
- Records are a `header`, initial `snapshot`, interval-bearing `snapshot` records and an `end` marker when normal duration/output termination occurs. A process that disappears may yield an unavailable snapshot and exit 1 instead of a duration-complete marker.
- Intervals use measured monotonic start-to-start elapsed time, not the requested sleep duration. Each snapshot includes `snapshot_read_seconds`; file reads are sequential, not an atomic system snapshot. Expensive reads can extend duration and distort tight sampling. Choose a period well above collection cost and record that limitation.
- JSON goes to stdout. Output redirection writes only because the caller explicitly requested it. PID/cgroup paths can identify workloads; review recordings before sharing. No command lines, environments, hostnames, arbitrary process memory or call stacks are dumped.

Exit 0: requested duration completed. Exit 1: PID unavailable/disappeared/reused. Exit 2: usage/platform error. Exit 3: output bound. Ctrl-C exits 130. Unavailable optional fields do not automatically fail the entire run: inspect `errors`, sample coverage and available counters before interpreting it.

## How to read the fields

| Field family | Unit / scope | Interpretation and trap |
| --- | --- | --- |
| `process.utime_ticks`, `stime_ticks` | Task-group CPU ticks, excluding separately waited-for children | Divide delta by header clock-ticks/second; not wall time |
| `cpu_percent_one_logical_cpu` | 100% = one logical CPU fully used | 200% may mean about two logical CPUs, not impossible utilization; not normalized by quota |
| `process.num_threads` | Thread count at process-stat read | Count alone does not establish runnable oversubscription |
| `threads[].state`, `selected_thread_state_counts` | Sparse instantaneous states for selected readable threads | R is running/runnable; S/D do not identify a specific lock or I/O source; transient phases can be missed |
| `voluntary/nonvoluntary_context_switches` | Per-thread cumulative events and interval rates | Voluntary can reflect waits; involuntary can reflect scheduling/preemption. Neither count alone is a root cause |
| `process.leader_*context_switches` | Leader only, not task-group aggregate | Do not report as all-thread switches or double-count it with the leader in `threads` |
| `runtime_ns`, `runqueue_wait_ns`, `timeslices` | Per-thread schedstat CPU/runtime, runnable-queue wait and slices | Requires kernel statistics support/enabling; all zeros may be unavailable/disabled, not zero wait |
| `cpu_migrations` | Per-thread `se.nr_migrations` when exposed | A migration is not automatically a harmful NUMA move or cache miss |
| `minflt`, `majflt` | Per-process or per-thread fault counters, explicitly separated | Minor != free, major != swap; see memory reference |
| `rss_pages`, `virtual_bytes`, `VmRSS_kib`, `VmSwap_kib` | Process memory gauges | RSS pages use header page size; virtual space is not resident consumption |
| `smaps_rollup_kib` | Optional process Rss/Pss/private/Swap/SwapPss | PSS apportions shared pages; these are gauges, not allocation throughput |
| `system.ctxt`, `procs_running`, `procs_blocked` | Host-visible context-switch total and instantaneous gauges | Never attribute the entire system count to this PID |
| `system.pswpin/pswpout` | Host-visible cumulative pages swapped | Interval rates are pages/s; multiply by page size for bytes/s, not by an assumed 4096 |
| `pgfault`, `pgmajfault`, `pgscan_*`, `pgsteal_*`, `allocstall*`, `oom_kill` | Host-visible kernel counters where present | Correlate with target counters; absence is not a zero |
| `*_pressure.*_total_us` | Host-visible accumulated stall microseconds | Delta/elapsed microseconds gives a scoped stall-time fraction; some/full and CPU/I/O/memory have distinct meaning |

`counter_decreased` means the sampler refuses subtraction for that field; it does not turn a reset into a huge unsigned rate. `unavailable` means a value was missing. `new_or_reused_thread` means there was no matching prior TID/start-time identity, so no interval CPU/switch delta is fabricated. Threads absent from the selected next snapshot can have exited, become inaccessible or been omitted by truncation; absence alone is not an exit event.

For example, a `runqueue_wait_ns.delta` of 200,000,000 over 1 second is 0.2 seconds accumulated runnable waiting for that sampled thread. It is not necessarily a single 200 ms wait and is not a mutex-blocked duration. Summing across many threads can exceed wall time. If `schedstats_enabled_raw` is `0`, missing or unavailable, a zero counter does not prove that runnable delay was absent.

## Capacity is a constraint, not a physical-core count

The header does not claim physical cores. `system.visible_logical_cpu_count` counts visible `/proc/stat` CPU rows. `capacity.leader_affinity_logical_cpus` is the leader's allowed logical-CPU list; each selected thread also exposes its own list. Threads can have different affinity.

The sampler supports the visible cgroup v2 mount `/sys/fs/cgroup` only after verifying its unique mapping in `/proc/self/mountinfo`. It resolves the process's unified path against that mount's root (including a subtree mount); missing/ambiguous mappings yield unknown rather than a guessed group's quota. It then walks up visible parents, collecting `cpu.max`; the minimum finite quota/period is reported as `cgroup_v2_quota_cpu_equivalents`. `max` is not a finite quota. A value of 0.5 denotes CPU bandwidth equivalent to half a CPU over the configured period, not a dedicated half-core or an affinity set. Also inspect `cpuset.cpus.effective`, per-thread affinity, quota periods, peer contention and throttling.

Important limits:

- Ancestor walking is capped at 64 groups and reports `ancestry_truncated` if the visible mount root was not reached. Container mount/cgroup namespaces can hide or remap ancestors. Files may be absent at the root or controller-disabled groups. Read errors and `quota_scope` qualify the result; visible records are not guaranteed to expose the full effective host constraint.
- Null quota can mean no finite quota among visible records **or** unavailable records. Distinguish using `visible_cpu_max_records`, status and errors; do not convert null to unlimited.
- cgroup v1 is explicitly reported as unsupported for this quota helper; use the offline scheduler reference's `cpu.cfs_quota_us`/period and ancestor procedure. Do not infer the host CPU count as usable capacity.
- A process/group can move between samples. Cgroup counter differences are computed only when the visible cgroup path matches; namespace changes or hidden limits still need manual interpretation.
- `nr_throttled`, `nr_periods`, `throttled_usec` are cgroup-level counters shared by workloads in that group, not exclusive attribution to this process. Throttled microseconds can reflect multiple execution entities; do not equate them uncritically to wall latency.

A 200-thread service with 195 sleeping threads may be fine. A 32-worker compute loop constrained to 2 CPU-equivalents, with increasing runnable delay, throttling and worse throughput, warrants reducing/redistributing parallelism. The sampler supplies parts of that evidence; its snapshots do not alone establish the causal chain.

## Next experiment by observed evidence

| Observation | Next targeted check |
| --- | --- |
| CPU busy, low runnable delay, bad scaling | [Cache/bandwidth/shared-line evidence](cpu-cache-sharing-contention.md), algorithm/layout work |
| Many selected R states, rising runqueue wait/preemption/throttling | [Scheduler and thread capacity](scheduler-thread-capacity.md), controlled thread-count sweep |
| Mostly S/D, low CPU, throughput poor | Authorized bounded wait-stack/off-CPU evidence; distinguish mutex, I/O, condition waits and producer starvation |
| Target faults rise with system reclaim/PSI/swap activity | [Memory pressure and NUMA](memory-pressure-numa.md), distinguish mapped-file faults from paging and other workloads |
| Cacheline contention suspected | Supported `perf c2c`/hardware event evidence plus address-to-object/field ownership; proc data cannot confirm it |
| All optional files absent | Keep PID identity/basic CPU evidence and explicit coverage limits; do not invent zeros or install tools |

## Reproducible local checks

The separately distributed development-validation suite uses original temporary proc/cgroup fixtures. It checks parenthesized stat names, PID/TID identity reuse, counter decreases, CPU unit conventions, selected-thread bounds, visible ancestor quotas and subtree mount-root resolution, permissions/missing files, pressure parsing and output byte limits. That development suite is not in this runtime bundle. The collector and usage commands above remain directly available; no actual target or special permissions are needed for the separate fixture tests.

The implementation was also smoke-tested on an owned finite CPU child process: interval CPU near one logical CPU and explicit unavailable PSI/cgroup files were observed. That validates this environment's basic collection path, not perf availability, all kernel versions, cgroup v1 or the user's workloads.
