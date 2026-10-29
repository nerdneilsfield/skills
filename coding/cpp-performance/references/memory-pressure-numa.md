# Memory residency, paging pressure and NUMA: separate the mechanisms

Load when a C++ workload slows as data size/worker count grows, faults spike, memory approaches a limit, or CPU utilization drops while elapsed time rises. This is an offline operating guide for an authorized process and tools already installed. Commands only inspect state; do not add `sudo`, change reclaim/swap policies, clear caches, install packages or alter affinity as a diagnostic shortcut. No CUDA tools are involved.

Start with a question: **insufficient resident capacity, excessive allocation/first-touch, backing-store faults, remote-node access, or saturated memory bandwidth?** These produce overlapping symptoms but need different experiments. Preserve the representative input, code/build identity and quality checks before tuning.

## 1. Identify what each number can actually establish

| Observation | Meaning and important limit |
| --- | --- |
| Virtual size / `VmSize` / VSZ | Address space mapped/reserved; not RAM consumed. Large sparse reservations or thread-stack reservations can dominate. |
| RSS / `VmRSS` | Resident process mappings; shared pages can be counted in several processes. It excludes pages currently swapped out; do not sum per-thread RSS as independent allocations. |
| PSS | Shared resident pages divided among current sharers; useful for attribution, not an invariant ownership bill. Another process starting/exiting can change PSS without this process allocating. |
| `Swap` / `SwapPss` in smaps | Swapped mapping bytes and proportional share where supported; an amount, not the current swap transfer rate. |
| Minor faults | Fault handling without backing-store reads, often first-touch, copy-on-write or mapping a page already in cache; not necessarily a performance defect. |
| Major faults | Faults needing backing-store reads; they can be file-backed data/code, not just anonymous swap-in. Fault counts are events, not I/O byte counts. |
| System `pswpin` / `pswpout` | Cumulative swap page counts; interval deltas measure activity across the observed system, not which process caused it. |
| PSI memory stall time | Time lost to memory pressure in the measured system/cgroup; not bytes and not a per-process blame metric. |
| NUMA pages on node N | Where mapped pages reside now; not how many accesses came from another node. |

Use the installed kernel's field names/units. Many `/proc` sizes labeled `kB` use 1024-byte units. Never assume the machine's base page size is 4096 bytes; a valid Linux query is `getconf PAGESIZE`. Transparent/explicit huge pages and mapping page sizes require their own accounting. Kernel support and permission restrictions can omit fields; absent is not zero.

## 2. Bounded first collection: process plus system, same phase

Replace `12345` with the verified authorized PID. Confirm process identity before and after the window; a PID can be recycled. The parenthesized command field in `/proc/PID/stat` may contain spaces, so a naive `awk '{print $22}'` identity parser is unsafe. Prefer the included sampler's identity handling or a correctly parsed start-time field.

```sh
PID=12345
# Quick single snapshot; do not read cmdline/environ or memory contents.
grep -E '^(Name|Pid|Threads|VmSize|VmRSS|RssAnon|RssFile|RssShmem|VmSwap|Mems_allowed_list):' /proc/$PID/status
# Installed sysstat: one-second intervals, ten reports, memory/fault activity.
pidstat -r -p "$PID" 1 10
# Installed procps: first line's rates cover boot history; remaining lines cover intervals.
vmstat 1 11
```

`pidstat` reports `minflt/s`, `majflt/s`, RSS and virtual size; its ordinary process view is not a sum over every process in a job tree. `-t` adds thread observations, but shared address-space metrics must not be summed across those rows. Read fault rates alongside the phase of work: loading a dataset, spawning workers and entering steady-state often have different normal profiles.

`vmstat` is system-level. Inspect `si/so` for swap transfer, `bi/bo` for block-device traffic, and `r/b` plus CPU fields for runnable/blocked context. Do not label every block read swap. The first report's rate averages are not the same measurement window as the subsequent one-second reports. Units/options differ across procps versions; keep the header and installed-version help with the result. If either tool is absent, use the `/proc` snapshots below and state the missing view; do not silently install it.

### `/proc` fallback and low-frequency attribution

```sh
# System capacity/context, single snapshot.
grep -E '^(MemTotal|MemAvailable|MemFree|Cached|SwapTotal|SwapFree|Dirty|Writeback|AnonPages|Slab):' /proc/meminfo
# System cumulative counters: take a second snapshot after the same bounded workload phase.
grep -E '^(pgfault|pgmajfault|pswpin|pswpout|pgscan|pgsteal|allocstall|workingset_refault)' /proc/vmstat
# System pressure; may be unavailable on this kernel/configuration.
cat /proc/pressure/memory
cat /proc/pressure/io
# More accurate residency accounting, at low frequency and only when permitted.
grep -E '^(Rss|Pss|Pss_Anon|Pss_File|Pss_Shmem|Private_Clean|Private_Dirty|Shared_Clean|Shared_Dirty|Swap|SwapPss):' /proc/$PID/smaps_rollup
```

Read smaps/rollup sparingly: deriving detailed mapping accounting can be substantially more expensive than cheap status counters and is not an appropriate millisecond poll loop. `smaps_rollup` may be absent or denied; report that limitation rather than read protected paths or pretend RSS equals PSS. Full `smaps`/`numa_maps` can expose mapping addresses and file paths; collect them only for a concrete question and review before sharing.

For cumulative counter `C`, rate = `(C_end - C_begin) / actual_elapsed_seconds`. Use a monotonic measured interval, not just the requested sleep duration. Negative deltas, reboot/identity change, disappearing files and access errors invalidate a rate; never convert them to zero. Compare overlapping process/system windows, not unrelated runs. `/proc` is not an atomic whole-system snapshot, so small timing discrepancies are expected.

For `pswpin/out`, multiply the page delta by the base page size for an approximate byte transfer rate; retain raw pages and units. For PSI `total` (microseconds), `100 * delta_total / elapsed_microseconds` gives the interval fraction for that stall class. `some` and `full` are overlapping sets, not quantities to add; `full` identifies a more severe simultaneous-stall condition. The avg10/60/300 percentages are smoothed windows, not counters to subtract. Treat a brief stall burst differently from continuous pressure and correlate both with observed latency rather than impose a universal PSI cutoff.

## 3. Distinguish actual pressure from plausible-looking memory numbers

Use this decision sequence on a matched steady-state interval:

1. **Large VSZ, stable modest RSS, no growing pressure:** inspect reservations and thread count, but do not call it a resident leak. Large thread stacks may reserve virtual space while touching only a fraction.
2. **Fault burst at startup, then flat rates:** compare initialization/first-touch time separately from steady-state. Moving work out of the measured region can conceal total latency; report both if startup matters.
3. **RSS rises on repeated equivalent jobs:** separate live object growth from allocator-retained arenas, page cache mappings and fragmentation. Correlate retained allocations/object counts with residency. RSS not falling immediately after `free` alone does not prove a leak.
4. **Major faults rise, swap activity stays flat:** inspect file-backed input/code loading and storage reads. Repeated file-cache eviction/refaulting can cause pressure without anonymous swapping. Do not propose changing swap policy from major faults alone.
5. **Swap transfer + memory stalls + latency increase:** pressure is plausible; identify the applicable host/cgroup limit and concurrent workloads before blaming one process. Compare a smaller working set or fewer simultaneous jobs under unchanged configuration.
6. **Little swapping but reclaim/refault/stall activity:** swap may be disabled or the workload may reclaim file cache. Zero `si/so` does not prove memory is healthy. Examine relevant counter deltas and the cgroup boundary.
7. **Stable residency/fault/pressure, hot streaming loops and flattening throughput:** investigate cache locality and available memory bandwidth, not paging. Hardware memory-controller/uncore counters may be system-scoped and architecture-specific; process LLC misses alone are not total DRAM bytes.

Do not clear page caches to manufacture a “fair” run: it changes other workloads and the experiment. Define whether cold-start or warmed steady-state is the requirement; collect representative runs using an approved isolated environment if the distinction matters.

## 4. Container/cgroup limits can dominate an apparently spacious host

Host `MemAvailable` does not establish that the target's cgroup can allocate more memory. Read `/proc/PID/cgroup` and the actual cgroup mount mapping (including container mount namespaces) before resolving paths. Do not blindly concatenate a host mount prefix with a path seen inside another namespace.

For an already resolved, authorized cgroup v2 directory, inspect these files if present:

```text
memory.current
memory.max
memory.high
memory.swap.current
memory.swap.max
memory.events
memory.events.local
memory.stat
memory.pressure
```

`memory.current` is group accounting, not the sum of target-process RSS. `memory.max` and `memory.high` express different constraints: the high boundary can cause reclaim/throttling; max is the hard boundary with possible reclaim/allocation failure/OOM behavior. `max` text means no limit at that level, not necessarily no tighter ancestor. Read relevant ancestors within the accessible hierarchy; siblings may share an ancestor budget. Events are cumulative, so compare deltas during the workload. Distinguish hierarchical events from local events when attributing changes. Do not modify any limit, reclaim trigger, swap setting or pressure trigger as part of read-only inspection.

Cgroup v1, hybrid layouts and unavailable controllers have different files. State the detected mode and unavailable fields instead of treating v2 filenames as portable. A container view can also omit host processes that caused system-level pressure.

## 5. NUMA: location is evidence, not yet a remote-access diagnosis

With installed numactl tools and permissions:

```sh
numactl --hardware
numastat -p "$PID"
numastat -m
# Target mapping placement/policy; may be large and contain filenames.
cat /proc/$PID/numa_maps
# Existing affinity/allowed placement inspection, not modification.
grep -E '^(Cpus_allowed_list|Mems_allowed_list):' /proc/$PID/status
```

`numactl --hardware` describes available topology; `numastat -p` shows process memory placement and `-m` per-node memory context. Default `numastat` allocation-hit/miss counters concern allocation locality, not CPU cache misses or direct remote-load counts. Do not interpret a high cumulative allocation-miss number without interval/context. `numa_maps` reports mapping policy and per-node resident page counts; inspect relevant mappings rather than sum unlike base/huge page units blindly.

Build a hypothesis from **where hot workers run + where their hot data resides + which memory they actually touch**. A process legitimately spanning nodes can have balanced placement while individual workers repeatedly read remote data. Conversely, pages on node 1 are not “remote” when the consuming thread runs there. CPU migration or a serial initialization phase may change the relationship. Allocation policy, first touch, shared pages, automatic NUMA balancing and memory-node restrictions all affect interpretation; none justify blanket pinning.

For an approved isolated follow-up experiment, compare the existing configuration with a deliberate ownership/locality change: parallel initialization by owning workers, per-worker shards, or a documented affinity/placement setting for that test process. Keep input/work amount/threads and quality fixed, include initialization cost, record allowed CPUs/nodes and compare end-to-end latency/bandwidth. Such placement changes are a separate authorized experiment, not a side effect of observation. Reject improvements that merely exclude work or create imbalanced memory exhaustion.

Use supported load-latency/remote-access hardware evidence when available, noting model-specific events and sampling bias. If unavailable, call the remote-access cause a hypothesis supported by placement/timing rather than a measured remote-traffic rate. See [profilers and threading](profilers-and-threading.md) for the existing platform tooling boundaries.

## 6. Worked offline interpretation fixtures

These are synthetic examples; they do not report measurements of the user's project.

| Evidence from matched windows | Supported reading | Useful next action |
| --- | --- | --- |
| 200 workers reserve large stacks; VSZ 1 TiB, RSS 2 GiB, minor faults mainly during startup | Virtual reservation and first-touch are plausible; no resident-leak proof | Record runnable workers/capacity separately, inspect recurring live allocations; compare startup and steady-state |
| Process 500 major faults/s; system pswpin/out deltas both zero; file read rate increases | Backing-store faults may be file-backed, not anonymous swap | Identify input/mapped-file phase and storage latency before changing memory policy |
| Host MemAvailable 40 GiB; cgroup memory.current near 4 GiB limit, high events rise, group memory PSI rises | Local group pressure can explain stalls despite host headroom | Identify group members/ancestor budgets; compare a smaller concurrent working set without modifying limits |
| 10-second system pswpin delta 2560 pages, base page 4096 bytes | 10 MiB over window, about 1 MiB/s system swap-in; target attribution unknown | Align target fault/latency and group pressure windows; do not assign all 1 MiB/s to target |
| Memory PSI some total increases 300000 us during 2 seconds; full increases 40000 us | About 15% partial and 2% full stall time, overlapping—not 17% | Correlate latency phases and group/system scope; no universal pass/fail threshold |
| numastat places most data on node 0, hot workers mostly node 1, faults/PSI flat | Remote placement is a plausible throughput cause, not proven access count | Controlled locality experiment plus supported remote-access/bandwidth counters |
| Throughput flattens with more workers; RSS/faults/PSI flat; measured controller traffic plateaus | Bandwidth saturation is plausible, not capacity exhaustion | Reduce bytes/work or improve reuse; don't “fix swapping” or indiscriminately add threads |

## 7. Windows and macOS: equivalent questions, different metrics

**Windows:** use installed WPR/WPA memory/working-set views and suitable hard-fault/storage traces for the matching target/interval. Inspect profile availability with `wpr -profiles`, avoid disrupting an existing recording, and keep trace collection separately authorized. Working set is resident memory; private bytes/commit describe different accounting. A hard fault can read a mapped file or paging file, so page-fault activity alone is not “pagefile thrashing.” Keep system memory and process attribution separate. Linux PSS, PSI and `/proc` rates have no automatic one-to-one translation. If the installed toolkit cannot supply the relevant trace, retain an explicit limitation and available application counters.

**macOS:** Activity Monitor's Memory view exposes memory pressure, compressed memory and swap used; pressure is not simply “free RAM is low.” Use installed Instruments Allocations/VM-related views for target ownership and lifetime questions. `vm_stat` is a system snapshot; preserve its reported page size before deriving bytes and check the installed help for version-specific sampling behavior. Swap used is an amount, not an instantaneous swap rate, and compressed memory changes the interpretation. There is no claim that Linux NUMA/proc/PSI commands work on macOS. Do not run a memory-pressure stress mode merely to observe a live workload.

## Report the evidence, not a diagnosis from one counter

Record target identity/time window, host versus cgroup scope, raw units/counter deltas, residency and fault trends, pressure/swap context, topology/placement and actual workload latency/quality. State exactly which observation supports capacity pressure, file refaulting, allocator retention, NUMA locality or bandwidth limitation—and what remains unmeasured. Include probe overhead and missing permissions/tools. No general RSS percentage, fault rate, PSI value or node split proves a universal bottleneck.

## Verified source provenance

Command/field semantics were checked against primary project/kernel documentation; procedures above are original synthesis and remain usable offline. Installed kernel/sysstat/procps/numactl versions can differ.

- Linux kernel [proc interfaces](https://www.kernel.org/doc/html/v6.12/filesystems/proc.html), [PSI](https://www.kernel.org/doc/html/v6.6/accounting/psi.html), [cgroup v2 memory controller](https://www.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html), [NUMA policy](https://cdn.kernel.org/doc/html/latest/admin-guide/mm/numa_memory_policy.html).
- procps [vmstat manual](https://man7.org/linux/man-pages/man8/vmstat.8.html), sysstat [pidstat manual](https://man7.org/linux/man-pages/man1/pidstat.1.html), numactl [numastat manual](https://man7.org/linux/man-pages/man8/numastat.8.html), Linux [process stat fields](https://man7.org/linux/man-pages/man5/proc_pid_stat.5.html).
- Microsoft [working sets and page faults](https://learn.microsoft.com/windows/win32/memory/working-set), [WPT memory footprint analysis](https://learn.microsoft.com/en-us/windows-hardware/test/wpt/memory-footprint-optimization); Apple [Activity Monitor memory view](https://support.apple.com/en-mide/guide/activity-monitor/actmntr1004/10.14/mac/15.0).

## From diagnosis to a fix

Use [concrete remedies and preventive patterns](thread-and-memory-remedies.md) for evidence-gated implementation choices, correctness/side effects and A/B acceptance. Do not stop at a counter label or apply every remedy at once.
