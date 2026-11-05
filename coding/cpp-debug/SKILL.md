---
name: cpp-debug
description: "Use when C++ crashes, hangs, races, corrupts memory, or fails nondeterministically, or when a wrong result or build/test failure is still unexplained after the first diagnostic and nearby diff. Defer shared conventions to cpp. Not for project setup (cpp-project-init), measured speed work (cpp-performance), or Eigen/solver/numerical-contract failures (cpp-numerics)."
---

# C++ diagnosis from evidence

Find the first violated contract, not a patch that merely hides the symptom. This skill owns crashes, hangs, races, memory corruption, nondeterminism, and failures that stay unexplained after the first diagnostic and a local check. Defer shared language and ownership rules to `cpp`. Defer project creation, CMake presets, and vendoring to `cpp-project-init`. Defer measured CPU, cache, thread, and memory tuning to `cpp-performance`. Defer Eigen, solver, manifold, and numerical-contract failures (non-finite values, divergence, wrong residual or Jacobian) to `cpp-numerics`. Preserve existing build and dependency choices during a local fix. CUDA is outside this skill.

If a needed named skill is missing, tell the user to install that exact skill from this bundle. Do not globally search, fetch a substitute, automatically install, or invent its contents; continue only independent minimal triage.

## Minimal triage before deeper diagnosis

A routine failed test or obvious compiler error does not use this whole workflow. First read the first diagnostic and failing assertion, inspect the nearby diff, input, and expected behavior, reproduce with the existing focused command, and make a supported local correction with its regression check. Stop when that resolves the issue.

Continue in this skill when the cause remains uncertain, reproduction is unstable, the binary or core identity is unclear, or the evidence is a crash, hang, race, or memory or undefined-behavior failure. Hand wrong or non-finite numerical results to `cpp-numerics` when the model or data contract is the relevant question. Do not automatically collect a core, install tools, enable every sanitizer, or run a full platform matrix because a test turned red.

## Offline supporting materials

- For missing reproduction, wrong results, executable/core identity or debugger inspection, read [crashes and symbols](references/crashes-and-symbols.md).
- For sanitizer selection, races or hangs, read [sanitizers and hangs](references/sanitizers-and-hangs.md).
- To record installed-tool paths without executing them, run `python3 scripts/environment_snapshot.py --help` or `python3 scripts/environment_snapshot.py` from this skill directory. Output is allowlisted JSON on stdout, not a full environment dump; review paths for personal directory names before sharing. It proves neither tool versions nor permissions.
- These materials work without web access. Missing local tooling means a stated limitation/fallback, not implicit installation.


## Capture before changing

Record expected versus observed behavior, exact invocation/input or seed, failing revision, platform, compiler, build preset/options, relevant logs and frequency. Separate observed facts from hypotheses. Inspect the actual compilation database/build commands before trusting editor diagnostics; stale generated headers or a different macro set can create a false problem.

For a crash, retain the matching executable, shared libraries, debug symbols and core/minidump where available. Verify build IDs or equivalent identity: symbols from another build are not evidence for the failing binary. Respect sensitive input/core contents; do not upload them without authorization.

If there is no reproduction, ask for the smallest missing artifact and improve bounded capture/logging around the suspect boundary. Reduce input or repeat the recorded seed when possible. Do not call a speculative change a fix; state what observation would discriminate the hypotheses.

## Select the next experiment

| Symptom | Evidence and focused tools |
| --- | --- |
| Incorrect result / failing test | Expected behavior, minimal input and first incorrect state; verify assumptions before patching |
| Compile error | First relevant diagnostic, actual command/includes/macros, generated inputs; reduce one translation unit |
| Link/ABI error | Exact link line, symbol signatures, library order/architecture, runtime/standard-library and ABI compatibility |
| Crash/use-after-free | GDB/LLDB or platform debugger with matching symbols; all-thread stack; ASan where supported |
| Arithmetic/alignment UB | Operand ranges and contracts; targeted UBSan run |
| Race/corruption under concurrency | Ownership and synchronization, captured interleaving; supported TSan build |
| Hang/deadlock | Repeated all-thread stacks, lock ownership/wait graph; distinguish blocked I/O from livelock |
| Numerical divergence/NaN | First non-finite value, data/layout/units and solver state; use `cpp-numerics` |

Use the debugger available on the platform, not a required Linux-only stack. A minimal GDB inspection for an already captured matching executable/core is:

```sh
gdb -nx -iex 'set auto-load off' -iex 'set debuginfod enabled off' ./matching-program ./core
# At the GDB prompt:
# info sharedlibrary
# thread apply all bt full
```

Paths are illustrative; select the retained artifacts, not the latest rebuilt executable. Optimized code can reorder/eliminate variables. Reproducing in a symbol-rich release-like build may be necessary; Debug-only success does not explain a Release crash.

## Isolate and repair

1. Trace from the earliest bad state through ownership, bounds, lifetime, initialization and synchronization. A crash in a library does not establish that the library caused the corruption.
2. Choose one falsifiable hypothesis and the cheapest informative experiment. Preserve failure evidence before editing; do not batch speculative fixes.
3. Minimize the reproducer while retaining the failure. If a recent regression is known, a controlled revision comparison or bisect may be more useful than adding logs everywhere.
4. Fix the responsible contract with the smallest scoped change. Adding sleeps, swallowing errors or disabling checks does not establish causality.
5. Run the original reproducer and a regression check for the failing behavior, then relevant nearby tests. For intermittent failures, record repetitions and exposure; absence of recurrence is limited evidence, not proof of impossibility.

## Instrumentation boundaries

Use separate diagnostic presets/build directories. Check toolchain/runtime support; instrument relevant compilation and linking. ASan+UBSan can coexist where supported; TSan uses a separate build from ASan. Do not mix diagnostic measurements with performance claims.

If a tool or artifact is missing, report exactly what cannot be checked and continue with available evidence. Never mark a skipped check passed. Do not install every tool or introduce an entire platform matrix for one bug.

For flaky asynchronous tests, synchronize on observable completion with bounded waits, preserve seeds and isolate temporary files. Ensure workers stop/join even after failed assertions; a timeout alone does not guarantee teardown finishes. Prefer existing concurrency primitives over test-only architecture.

## Handoff

Report: symptom/reproducer → evidence → supported cause (or remaining hypotheses) → focused change → exact checks and limitations. Distinguish a verified correction from an unconfirmed mitigation. Keep input/core locations private as appropriate.

## References

- [GDB manual](https://sourceware.org/gdb/current/onlinedocs/gdb.html/), [LLDB tutorial](https://lldb.llvm.org/use/tutorial.html): use installed-version commands.
- Clang [AddressSanitizer](https://clang.llvm.org/docs/AddressSanitizer.html), [UndefinedBehaviorSanitizer](https://clang.llvm.org/docs/UndefinedBehaviorSanitizer.html), [ThreadSanitizer](https://clang.llvm.org/docs/ThreadSanitizer.html): platform support and limitations.
- [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines): lifetime (F.43), overflow (ES.103–105), concurrency (CP.2/8/9). These are reading pointers, not copied guide text.
