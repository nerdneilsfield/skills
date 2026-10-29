# Original offline remediation correctness examples

These are runnable **C++20 correctness demonstrations**, not measured speedups, a benchmark framework, a production thread pool or a new dependency recommendation. Keep an existing C++17 project's standard unless its task authorizes otherwise. For a C++17 adaptation, thread join-on-error needs an explicit RAII design; do not mechanically replace `jthread` with `thread`.

## Already-installed toolchain only

From this directory, with an installed C++20 compiler and supported native threads:

```sh
c++ -std=c++20 -Wall -Wextra -Wpedantic -Werror -pthread -O0 -g \
  remediation_examples.cpp -o /tmp/remediation-debug
/tmp/remediation-debug
c++ -std=c++20 -Wall -Wextra -Wpedantic -Werror -pthread -O2 -DNDEBUG \
  remediation_examples.cpp -o /tmp/remediation-release
/tmp/remediation-release
```

Use a writable fresh output path; commands above illustrate a Unix-like shell/toolchain. With an already configured MSVC developer environment, use its C++20/native-thread flags and a chosen local output path rather than copying `-pthread`. No package, internet or library installation is needed. If the installed standard library lacks `std::jthread`, report that the C++20 fixture cannot run; do not silently upgrade the user's toolchain.

Expected stdout for both builds: `all correctness checks passed`, exit 0. Explicit `require` checks remain active under `NDEBUG`; success is not an assertion-disabled no-op. The separately distributed development-validation suite compiles and runs both configurations in temporary directories when an installed Unix-style `c++` is available, with an explicit skip otherwise. That suite is not part of this runtime bundle; the local compiler commands above remain self-contained.

## What each example proves—and does not

| Example | Concrete change | Checked contract | Remaining performance/context decision |
| --- | --- | --- | --- |
| `shared_tally` → `local_tally` | Keep a count local during the loop; publish once to pre-sized per-worker storage; join then sum | Same final count for 1/2/4/16 requested workers, zero requests normalized, empty input | No live progress contract; time representative inputs; tiny jobs can be slower from thread startup |
| `column_first` → `row_first` | Traverse row-major data contiguously | Same bounded integer sum for a rectangular matrix and empty case | Inputs must match dimensions and sum must fit int64; floating-point order requires an accuracy contract; no speed measured |
| `BoundedQueue` + `queue_pipeline` | Bounded buffering, predicate blocking, work outside queue mutex, close-and-drain and join | No duplicate/missing jobs on success, peak <= capacity, closed rejects pushes, drains queued values, worker exception propagates | Queue capacity/worker budget from measured workload; blocking can deadlock if producer owns a resource consumer needs; not a universal executor |
| `transform_reuse` | Clear/reuse output capacity for a bounded owned batch | Correct final values, capacity retained, alias rejected | Keeps peak allocation alive, invalidates views on clear/reallocation, no real allocator/performance measurement |

The tally caller must supply a finite, justified worker budget: `min(input.size(), requested)` only bounds workers by items and does not discover effective CPUs/quotas. The fixture tests a few small requests, not arbitrary thread counts. The tally fixture uses no throwing operation inside workers; launch failures are handled by `jthread` lifetime. Storage is fully sized before threads start. Adjacent partial-result slots are written only once after local accumulation, so padding them is not automatically warranted. `memory_order_relaxed` in the *baseline* is valid for this independent count plus join; it is not advice to weaken an atomic that publishes other data.

The row/column example uses small bounded integer values so reordered addition has the same result. Real floating reductions can change rounding, cancellation and reproducibility; compare against the numerical error budget. The matrix helpers assume a buffer matching `rows * columns` without overflow and sum within int64; establish these before using the pattern on untrusted dimensions.

## Queue lifecycle and failure behavior

`close()` updates the predicate under its mutex, wakes **both** blocked producers and consumers, then releases the lock before any joins. Consumers use predicate waits, drain already queued items and stop when closed+empty. `jthread::request_stop` alone does not wake an ordinary condition-variable wait; the example's explicit close/notify is essential.

Thread launch/allocation/producer failures trigger close before stack unwinding joins previously started workers. Worker exceptions are captured in a mutex-protected first-error slot and close the queue, which unblocks the producer; the error is rethrown after joins. In an error run, some submitted/unsubmitted work can remain uncompleted; the function **fails**, not claims successful exactly-once processing. Real side effects may need per-job status, idempotency or transactional semantics; adding those blindly would make a different framework.

The reuse helper clears output before reserving/refilling; an allocation failure or later operation failure does not preserve the previous output and may leave a partial result. Use it only when that failure contract is acceptable, or compute into owned temporary storage and publish after success if the application requires a strong commit boundary.

The queue stores `int` so moving a job cannot throw. For real payloads, prefer explicit owned handles or an established queue whose exception guarantees fit the application; do not assume this example safely generalizes to every throwing copy/move type. The `hits_mutex` exists only to validate exact-once delivery and is not a recommended fast telemetry design. A job-specific callback/executor is deliberately absent.

## How to turn a demonstrated pattern into an optimization

1. Use local profiling evidence to choose **one** applicable pattern; do not transplant all examples into a project.
2. Write the relevant behavior, ownership, failure, progress/latency and numeric contract. Keep source data/order identical where required.
3. Apply the smallest change preserving that contract; reuse the existing pool, buffer and synchronization facilities instead of creating a new framework.
4. Measure end-to-end before/after using the same representative work and environment, plus the suspected causal counters. Keep release-like timing separate from sanitizer runs.
5. Reject regressions in output quality, tail latency, memory, shutdown/error handling or complexity. If the measured target is reached within budget, stop; more padding, pools or lock-free code are not automatically better.

Read [cache/synchronization remedies](../../references/cache-and-synchronization-remedies.md) and [thread/memory remedies](../../references/thread-and-memory-remedies.md) for evidence gates, side effects and prevention patterns.
