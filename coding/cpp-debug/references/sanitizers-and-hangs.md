# Targeted instrumentation, races and hangs

Load when ordinary reproduction points to memory/UB/concurrency faults, or a process stops making progress. Diagnostics change execution behavior; compare their evidence with the original symptom rather than treating every disappearance as a fix.

## Select one useful diagnostic build

| Evidence | Diagnostic experiment | Important limit |
| --- | --- | --- |
| Out-of-bounds or use-after-free | ASan on the failing workload | Only exercised paths; allocation layout/timing changes |
| Suspect arithmetic/alignment/type UB | Relevant UBSan checks | Not all language UB is diagnosed; unsigned wrap can be defined |
| Unsynchronized conflicting access | TSan in a separate supported build | High overhead; runtime/platform support and instrumentation coverage matter |
| Missing initialization | Track first use and initialization path; consider supported MemorySanitizer only when dependency instrumentation is feasible | Do not add MSan blindly to mixed uninstrumented code |

Use the project's target/preset structure. For a supported Clang toolchain, an example target-level ASan/UBSan configuration is:

```cmake
# Opt-in diagnostic configuration, not unconditional release policy.
target_compile_options(app PRIVATE -g -fno-omit-frame-pointer
  -fsanitize=address,undefined)
target_link_options(app PRIVATE -fsanitize=address,undefined)
```

`app` is illustrative. Instrument relevant first-party libraries too and link the final executable with the compiler driver so the runtime is included. Do not paste GNU-style flags into an unsupported toolchain. Keep TSan separate from ASan; use `-fsanitize=thread` at compilation and final linking only where supported. Select optimization with the actual compiler guidance and failure, not a universal Debug-only assumption.

Preserve the complete first report: failure type, access, allocation/free stacks, binary identity and input. Fix a cause, rerun the original reproducer, then relevant tests. Confirm symbols resolve before acting on line numbers. A suppression needs a narrow documented reason and follow-up; suppressing a first-party report is not a fix.

No report can mean the path did not run, the required code was not instrumented, runtime setup was wrong, or the issue was outside the check's scope. Document which was verified. Instrumented timing is not a production benchmark.

## Hangs: distinguish blocked, deadlocked and busy

1. Record the operation that should complete, its external dependencies, expected bound and last observed progress. “CPU is low” alone cannot establish deadlock.
2. On an authorized process, use an available debugger to obtain all-thread stacks. Attachment usually pauses the process; arrange an acceptable interruption window first.
3. Resume briefly and collect another bounded observation when safe. Repeated identical blocked stacks plus a wait-for cycle support deadlock; a single snapshot does not.
4. Trace lock ownership, acquisition order, condition predicates, queued work, joins and external I/O. Check whether a worker awaits an event only the blocked joining thread can produce.
5. For a busy process, compare stack samples/progress counters to distinguish real work, retry loops, livelock and starvation. Route CPU cost to the performance skill only after correctness is understood.

Illustrative live attach commands, **only after authorization**, are `gdb -nx -iex 'set auto-load off' -iex 'set debuginfod enabled off' -p PID` or `lldb --no-lldbinit -p PID`. The debuginfod-off setting applies when supported; if the installed GDB lacks that command, keep automatic symbol acquisition disabled/unavailable and use local symbols only. Replace `PID` with the verified intended process. Inspect stacks using [crashes-and-symbols.md](crashes-and-symbols.md), then detach explicitly (`detach` in GDB; `process detach` in LLDB). Detach/resume semantics and signal handling vary; verify the process resumes as intended. Do not leave an attached production process paused or issue a kill command to “finish diagnosis.”

## Stable concurrency regression

Use an existing future/event/condition variable with a bounded wait, not guessed sleeps. Test the predicate and shutdown behavior, including failure paths. Ensure worker teardown can complete even if an assertion fails; a timed assertion does not prevent a later join from hanging. Keep seeds, worker counts and repetition/exposure in the record. A stress pass means no failure observed under that exposure, not proof of race freedom.

## Sources and version checks

- Clang [ASan](https://clang.llvm.org/docs/AddressSanitizer.html), [UBSan](https://clang.llvm.org/docs/UndefinedBehaviorSanitizer.html), [TSan](https://clang.llvm.org/docs/ThreadSanitizer.html), [MSan](https://clang.llvm.org/docs/MemorySanitizer.html): use the documentation for the installed compiler/runtime and supported platform.
- GDB [attach](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Attach.html); LLDB [tutorial](https://lldb.llvm.org/use/tutorial.html): attachment permissions and process behavior are platform-specific.
- CMake [target_compile_options](https://cmake.org/cmake/help/latest/command/target_compile_options.html) and [target_link_options](https://cmake.org/cmake/help/latest/command/target_link_options.html): keep diagnostics target-scoped and compatible with the selected minimum version.
