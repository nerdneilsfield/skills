# From a hot stack to the work that can be removed

## Start broad, narrow only when justified

A sampled stack estimates where execution is observed. It does not count calls exactly;
brief functions can fall between samples. Capture a representative interval long enough
to include the operation, then inspect both caller context and expensive descendants.
A flamegraph width represents attributed samples/time, not chronological ordering.

If call frequency matters, cProfile reports `ncalls`, self time (`tottime`) and inclusive
subtree time (`cumtime`). A coordinator can have large inclusive time while doing little
work itself. Do not add overlapping inclusive entries into a total. Once a specific Python
function is implicated, line_profiler can show which lines deserve inspection. A line
containing a native call attributes its elapsed work to that call site; it does not explain
the internal kernel. Profiling every line initially adds noise and cost.

## Python CPU: remove work before changing execution engines

Evidence: repeated parsing/formatting or linear scans dominate self time/call counts.
Remedy: parse once within the needed lifetime; build an index if reuse pays for construction;
batch crossings of Python/native or I/O interfaces; eliminate repeated conversions.
Risk: an index changes memory/lifetime, caching may serve stale values, batching increases
latency and cancellation granularity. Verify identical results and total work, memory at
representative cardinality, and end-to-end latency. Prevent recurrence with explicit
ownership and bounded reuse, not a blanket instruction to cache every function.

Only consider compilation/JIT/native extensions after removing avoidable work and measuring
remaining CPU. Include warmup, dispatch, build/deployment complexity and buffer ownership in
the comparison. A function moved to C is not proven faster by its improved cProfile ranking.

## Native CPU: change the level of investigation

Evidence: samples enter a numerical/image/serialization extension and stay there, or Python
self time is small while process CPU is large. First inspect data size, layout, dtype,
conversion/copy costs and library thread settings. Then use native stacks with symbols or
an appropriate native profiler; missing symbols mean incomplete attribution, not zero cost.
Numerical precision/model changes require `python-numerics`-style accuracy checks.

Scalene's Python/native breakdown can discriminate layers,
but its percentages are observations under a selected mode, not a universal diagnosis.

A Python call stack does not expose cache-line bouncing, TLB misses, NUMA placement or
memory bandwidth saturation. Confirm those with hardware/OS tools and native code evidence.
Cache misses alone do not prove false sharing. For a native extension, reuse available C++
performance guidance; otherwise explain the needed counter/stack evidence rather than
inventing a conclusion from Python line timings.

## Useful next experiment

Change one hypothesis: halve repeat parsing, increase batch size within latency bounds,
use a contiguous input without repeated conversion, or limit a nested native thread team.
Re-profile only to confirm the hotspot moved; establish benefit with unprofiled repeats.
If the dominant cost lies outside the optimized scope, stop tuning that scope.

## Provenance

- Sampling/native/GIL limits: https://github.com/benfred/py-spy
- Deterministic profiler interpretation: https://docs.python.org/3.14/library/profile.html
- Local line attribution: https://github.com/pyutils/line_profiler
- Python/native decomposition: https://github.com/plasma-umass/scalene
