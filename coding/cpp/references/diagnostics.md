# Targeted diagnostics and reproducible checks

Use this reference when a concrete failure or requested change needs more than the ordinary build and functional check. Choose the relevant section; these are not cumulative completion gates.

## Select diagnostics by the suspected failure

| Evidence or change | Useful next check |
| --- | --- |
| Invalid memory access, use-after-free, ownership changes | AddressSanitizer on the affected workload |
| Suspected undefined arithmetic, alignment, or related UB | UndefinedBehaviorSanitizer on the relevant path |
| Shared mutable state or suspected races | ThreadSanitizer where supported, with a workload that exercises the interaction |
| Public header depends on include order | Compile a translation unit that includes it first |
| Claimed performance improvement | Comparable before/after measurements and a behavior check |

Check compiler, runtime, and platform support before adding flags. ASan and UBSan can share a configuration where supported; keep TSan in a separate build from ASan. Apply required instrumentation to both compilation and linking, and to the relevant code under test. Reuse CMake target settings and presets instead of inventing shell-only builds. A clean run only covers the paths exercised; do not present it as proof of all memory or concurrency safety.

Do not install every diagnostic tool, enable every sanitizer, or create a platform matrix for one local bug. If a required tool cannot run, state that limitation and use available evidence without calling the skipped check passed.

## A useful performance comparison

For a requested parser speedup, for example:

1. Select a representative input corpus and check the expected parsed results.
2. Record the release-like preset, compiler, input identity, and baseline measurement.
3. Profile the relevant workload to identify where time or allocations are spent.
4. Make the focused change and rerun the same behavior check and measurement, controlling cache/warmup conditions and repeating enough to understand noise.

Measure what motivated the task: throughput, latency, peak memory, or allocation count. Include tail latency when it matters to the requirement. Do not turn every comparison into a benchmark framework or claim a small noisy difference as an improvement. Preserve observable semantics; options such as fast-math or machine-specific instruction sets require explicit compatibility and behavior consideration.

## Stable asynchronous tests

Suppose a Catch2 test starts a worker and checks its result. Sleeping for 100 ms before checking does not establish that the worker finished. Signal completion through the operation's existing future, condition variable, or equivalent event, then use a bounded wait. Ensure the worker is stopped and joined on assertion failure as well as success; a timed wait alone does not prevent teardown from hanging.

Use a controllable clock when time itself is the behavior being tested and the design already permits it. Keep random seeds reproducible, isolate temporary paths, and reset task-owned state. Do not create a generic clock abstraction, dependency-injection framework, or mock hierarchy solely to satisfy these examples. Real filesystem or network interaction belongs in an appropriately scoped integration check when that interaction is the behavior under test.

## Reading sources

Selected ideas come from [ECC's cpp-testing](https://github.com/affaan-m/ecc/blob/main/skills/cpp-testing/SKILL.md) and [Jeffallan's C++ Pro](https://github.com/Jeffallan/claude-skills/blob/main/skills/cpp-pro/SKILL.md). Their GoogleTest, dependency-download, unconditional sanitizer, and benchmark defaults are not adopted here. The main skill's Catch2, vendoring, and proportional-verification rules remain authoritative for this skill.
