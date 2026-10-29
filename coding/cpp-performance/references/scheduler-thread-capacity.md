# Scheduler delay, context switching and too many runnable threads

Use when a multithreaded C++ workload gets slower as workers increase, tail latency spikes, or a container seems CPU-bound despite an apparently large host. All commands below are local Linux examples for an authorized PID/workload. Missing tools or access are reported, not repaired with sudo/sysctl/capability changes. Windows/macOS alternatives are at the end.

## 1. Do not divide threads by the wrong CPU count

Maintain separate quantities:

1. Host online logical CPUs and topology (physical cores, SMT siblings, sockets/nodes).
2. Each relevant thread's allowed CPU mask; affinity is per thread and workers can differ from the leader.
3. Effective cpuset and ancestor restrictions.
4. CPU bandwidth quota, if any, shared with all tasks in the cgroup and affected by ancestor limits.
5. Active **runnable/running** workers during the slow phase, not just all existing sleeping threads.

An application with 200 mostly idle I/O threads on 8 logical CPUs is not automatically oversubscribed. An application with 32 continuously runnable workers constrained to 2 logical CPUs probably warrants a thread-count experiment, but the measured problem might still be memory bandwidth, lock serialization or quota throttling rather than context-switch cost alone.

Read-only first-pass commands, substituting the verified process ID:

```sh
PID=12345
lscpu -e=CPU,CORE,SOCKET,NODE,ONLINE
ps -L -p "$PID" -o pid,tid,psr,stat,pcpu,wchan:24,comm
pidstat -u -w -t -p "$PID" 1 10
cat "/proc/$PID/status"
cat "/proc/$PID/cgroup"
cat /proc/loadavg
```

`ps` CPU percentages need not represent the same short interval as pidstat; use it mainly for identity/state/topology context. Redact names/paths before sharing. The `Cpus_allowed_list` field in each `/proc/PID/task/TID/status` is the mask for that task, not necessarily the whole program's mask. If installed, `taskset -pc TID` reads a task's current affinity; **do not** add a CPU-list argument that would change it during observation. [Affinity API](https://man7.org/linux/man-pages/man2/sched_getaffinity.2.html), [proc status](https://man7.org/linux/man-pages/man5/proc_pid_status.5.html)

A single `/proc` or `ps` snapshot is not a timeline. Threads can sleep/wake or vanish between reads. Repeated sampling provides state occupancy estimates only; it misses short bursts and does not count exact migrations from the last-observed CPU field.

## 2. Container/cgroup bandwidth is not a core count

For cgroup v2, resolve the target's `0::...` membership against the actual cgroup2 mount visible in its namespace. Do not blindly concatenate an arbitrary target path onto `/sys/fs/cgroup`: mount roots, namespaces and escaped names can differ. Inspect `/proc/PID/mountinfo` or the known container mapping; if mapping is ambiguous, report quota unknown rather than the host root's value.

At the verified cgroup directory, read `cpu.max`, `cpu.stat` and `cpuset.cpus.effective` when present; inspect visible ancestors for tighter limits. `cpu.max` is `quota period` in microseconds, or `max period`. Example `200000 100000` permits an aggregate budget equivalent to two fully busy logical CPUs on average per period, **not** reservation of two physical cores. Multiple tasks consume it together; a larger runnable team can exhaust the budget early. `max` at a child does not negate an ancestor's limit. Take deltas of throttling counters, not lifetime totals. Field availability and hierarchy semantics vary by kernel; newer `cpu.stat.local` may expose additional inherited effects. [cgroup v2 CPU/cpuset documentation](https://docs.kernel.org/admin-guide/cgroup-v2.html)

For a rough *upper-bound hypothesis*, combine mask/cpuset cardinality with visible finite quota/period limits. Do not round a fractional quota up and call that guaranteed compute capacity. SMT, hybrid CPU performance, contention with other cgroup tasks, host steal time and ancestor limits can all reduce effective throughput. cgroup v1 uses different mounts/files (`cpu.cfs_quota_us`, `cpu.cfs_period_us`); do not treat missing v2 files as unlimited v1 CPU.

Keep unknown explicit. A profile from a container may show host-wide `/proc/stat`/loadavg rather than its scheduling allocation. Never normalize target utilization by host CPU count simply because `os.cpu_count()` returned it.

## 3. What the counters mean

| Observation | Meaning and useful comparison | It does not establish |
| --- | --- | --- |
| Per-thread CPU time delta | Time actually charged while running; divide by monotonic elapsed interval, state normalization basis | Queue delay or useful work; spinning consumes CPU too |
| Voluntary context switches | Blocking-related switches; correlate with locks/I/O/conditions | Every switch is lock contention or harmful |
| Involuntary context switches | Preemption-related switches; compare with runnable load and throughput | Exact switching cost or cause by itself |
| CPU migrations | Scheduler movement counted by an appropriate event | Last observed CPU changes count all migrations |
| Runnable/running state snapshots | Sampled ready/executing population | Exact queue history or every wakeup |
| Runqueue-wait delta | Available schedstat waiting-to-run time | Sleep time; missing/disabled data is not zero delay |
| Throttling deltas | Cgroup bandwidth restriction activity in that accounting scope | Other groups' limits, physical core identity or all latency |

`sched_yield` does not necessarily count as a voluntary switch: a yielding task may remain TASK_RUNNING and be accounted as nonvoluntary. `pidstat -w` reports per-second task switches and `-t` includes threads. Interpret rates jointly with work completed and latency; a healthy high-throughput server may switch often. [pidstat manual](https://man7.org/linux/man-pages/man1/pidstat.1.html)

For `/proc/PID/task/TID/schedstat`, the three values are runtime nanoseconds, runqueue-wait nanoseconds and scheduling-slice count. Compute same-thread-identity deltas over measured elapsed time; counters reset/disappear when tasks change. Availability/accounting can depend on kernel configuration and schedstats enablement, so a constant zero field can be unavailable rather than an idle queue. Do not enable kernel-wide statistics automatically. [Kernel scheduler statistics](https://docs.kernel.org/scheduler/sched-stats.html)

Host `/proc/loadavg` combines runnable work and uninterruptible-wait contributions in its averages; it is not CPU utilization. Its runnable snapshot and host `/proc/stat` runnable/blocked counts are contextual evidence, not target attribution. A large load average with many D-state tasks can mean I/O pressure rather than too many CPU workers. [proc loadavg](https://man7.org/linux/man-pages/man5/proc_loadavg.5.html)

## 4. Bounded scheduler evidence

Start with low-overhead per-thread sampling and a thread-count sweep. Where the local perf version supports a timed existing-process count:

```sh
perf stat -p "$PID" --timeout 5000 \
  -e task-clock,context-switches,cpu-migrations,page-faults
```

Check local `perf stat -h` for `--timeout` and event availability. Verify which existing/new threads the attachment actually covers; a task that exits or a changing worker pool can make coverage incomplete. State collection duration and whether target work changed during it.

For a launchable finite trusted task instead:

```sh
perf stat -e task-clock,context-switches,cpu-migrations -- ./app representative-input
```

Do not add `-a` casually. A scheduler trace may need broader context to see the task that wakes a target, and can expose unrelated system activity. Only if system-scoped recording is explicitly authorized and available, use a short observation with a fresh file:

```sh
perf sched record -o sched-window.data -- sleep 5
perf sched timehist -i sched-window.data -p "$PID" --summary
perf sched timehist -i sched-window.data -p "$PID" --wakeups --migrations
```

`perf sched record` collects scheduler context that may be system-wide even though `sleep` bounds its duration; filtering the report by PID does **not** limit what was recorded. Check installed help and collection scope before starting. Do not run `perf sched replay` for inspection: replay creates synthetic work. `timehist` distinguishes off-CPU wait from runnable-to-running delay; the former can include intentional sleeping. Trace loss, missed wakeups and boundary-truncated intervals weaken exact delay interpretation. [perf sched manual](https://man7.org/linux/man-pages/man1/perf-sched.1.html)

If scheduler tracepoints/permissions are unavailable, retain the sampled per-thread CPU/states/switch rates and available schedstat/cgroup evidence. Say “sampling supports oversubscription” rather than invent a precise scheduling-delay histogram. No permission bypass is required to proceed with an application-level worker-count experiment.

## 5. Separate queueing from locks and work imbalance

- **Many R-state workers, growing runqueue delay, high effective CPU use:** test fewer workers and larger tasks/batches. Context-switch/migration trends help, but throughput and tail latency decide whether the change helps.
- **Most workers sleeping while one consumes CPU:** inspect the serial owner, pipeline stage, critical section or uneven partition. Lowering a thread count may not fix the bottleneck.
- **High CPU with hot retry/spin stacks:** treat synchronization work as CPU demand; inspect shared state/backoff before adding workers.
- **Many D-state tasks or fault/I/O pressure:** route to memory/I/O investigation; do not call every off-CPU delay scheduler oversubscription.
- **Quota throttling rises while host has idle CPUs:** fewer active workers or changed phase scheduling may reduce bursts, but changing deployment quota is a separate authorized policy decision.
- **Migrations rise with a slowdown:** check NUMA/data placement, cache warmth and heterogeneous CPUs. Affinity can help or harm balancing; record an explicitly authorized controlled experiment, not an automatic pinning “fix.”

For barriers, instrument the arrival-time spread per iteration and last-arriving worker; long wait by early arrivals can reflect imbalanced work rather than a slow barrier primitive. For queues, measure depth and producer/consumer service times. A thread pool with many blocked workers can starve tasks needed to release them even when overall CPU use is low.

## 6. Nested parallelism: route to the shared policy

Once scheduler evidence implicates competing worker layers, use [parallelism/BLAS policy](parallelism-and-blas.md), which owns the inventory, budget, outer/inner experiment and runtime-control rules. Use this reference's mask/quota/runqueue observations to constrain that experiment; no separate thread-control matrix is maintained here.

## 7. Cross-platform mapping

On Windows, installed WPR/WPA CPU Usage (Precise), ready-time and wait-analysis views are the scheduler path; CPU affinity, processor groups, CPU sets and job/container restrictions require their own accounting. Task Manager's logical-processor count is not proof of a process's entitlement. On macOS use installed Instruments thread-state/scheduling views and process sampling; QoS, heterogeneous cores and system pressure differ from Linux cgroups. Do not translate Linux `/proc` counters or perf event names into nonexistent equivalent commands. If the required trace tooling is missing, use local app timers/thread instrumentation and state the attribution gap.

## Offline interpretation fixtures

1. **Host 64 logical CPUs; allowed mask 0–7; visible quota 150000/100000; 24 active workers.** Capacity is not 64 or even guaranteed 8. Test throttling/runnable delay and worker-count reductions around the 1.5-CPU bandwidth constraint; note unseen ancestors/shared group peers.
2. **120 threads, typically 3 R and 117 sleeping; throughput improves with more I/O concurrency.** Raw thread count alone does not prove harmful CPU oversubscription.
3. **Involuntary switches and queue delay rise at 32 workers, but bytes/s plateaus and throughput falls.** Both memory saturation and scheduling overhead are plausible; compare 8/16/32 while tracking useful work and memory traffic.
4. **timehist off-CPU wait 200 ms, scheduling delay 0.2 ms.** Most of that interval was not waiting runnable on the CPU queue. Inspect sleep/lock/I/O cause before blaming scheduler delay.
5. **One sample shows CPU 2, next CPU 7.** At least a placement change occurred; this is not an exact migration count, and intermediate migrations may be missed.

State the resource envelope, measurement scope, thread identities, observed pressure, competing hypotheses and the next controlled change. Read-only observation is not entirely free: polling thousands of tasks too frequently adds cost, so bound duration/thread/output volume and disclose truncation.

## From diagnosis to a fix

Use [concrete remedies and preventive patterns](thread-and-memory-remedies.md) for evidence-gated implementation choices, correctness/side effects and A/B acceptance. Do not stop at a counter label or apply every remedy at once.
