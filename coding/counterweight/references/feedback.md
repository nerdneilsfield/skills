# Feedback and Debugging

Default to simple functional verification and evidence that the changed code can run. Often one existing focused check, smoke run, or worked example proves both. For text/config-only edits, a relevant static check is enough. Deep does not change this default.

Implement a runnable version first by default, then check the real behavior and hand it over for use. User reports, real inputs, and observed failures usually provide better next-step evidence than agent-invented scenarios. Do not hold delivery for a speculative test suite. TDD remains useful when explicitly requested, when an existing failing test already defines the task, or when a small test-first loop directly helps solve an observed bug; it is not a prerequisite for starting implementation.

Start with the smallest useful check. Add another only when it covers a separate explicit requirement, a real safety boundary, or a mandatory repository gate that the first cannot establish:

- Feature: run a representative input through the changed path and inspect the expected result; use an existing focused test if cheaper.
- Bug: run the reported reproducer and confirm the symptom is gone.
- Build/import change: compile, typecheck, or load the affected entry point as appropriate.
- Text/config: inspect the diff or use the relevant parser/config check.

Stop when existing evidence is sufficient. Fresh evidence must match the claim: a parser check cannot prove runtime behavior, and a broad suite cannot prove an unreproduced symptom is fixed.

Do not turn acceptance into an exhaustive test campaign. When a failure is extremely unlikely and unsupported by current evidence, do not add a test for it. Do not invent numerical probabilities; look for a reported symptom, actual reachable failure in the changed path, or an explicit requirement. Add checks beyond basic functionality only when that evidence makes them useful. A label such as Deep, public API, or migration is not by itself a reason for a large suite, fuzzing, stress tests, or a combinatorial edge-case matrix. Honor checks explicitly required by the user or repository.

## Permanent vs throwaway tests

Split checks by whether they must survive this session. The same restraint applies to both: do not invent speculative cases, self-confirming oracles, or a coverage matrix. A throwaway file is not a license to write a suite.

### Permanent tests

Do not add a test to the project's test tree merely because code changed. Keep one only when the behavior deserves future protection, its expected result comes from outside the implementation, it can falsify a plausible wrong implementation, and its maintenance cost is justified.

Be extremely restrained. Prefer an existing check, a one-off command, or a small extension of an existing test file. Add at most the focused cases those four conditions support. Do not add a new test file, fixture factory, or test helper to make the suite look complete.

Reject tests that only assert field presence, parameter forwarding, mock call counts, private implementation, a constant against itself, or an expected value recomputed by the algorithm under test. For text, simple config, imports, and mechanical wiring, targeted static or runtime verification is usually enough.

An observed bug or explicitly required contract may justify one focused test; a merely imaginable rare failure does not. When the independent-oracle rule and a concrete regression risk both hold, put that test in the project's test tree, not only in `/tmp`.

### Throwaway checks

A successful one-time smoke, reproducer, or probe need not remain in the repository. When a disposable script or fixture is useful, keep it out of the project's test tree, even as an untracked file. Test runners often collect files named like tests, and later sessions treat anything under the test tree as committable work.

Put throwaway checks in `/tmp` or `$TMPDIR`, or in one local directory that will not be committed: an already-gitignored path, or an untracked scratch directory that is never staged. Prefer `/tmp` when isolation is enough; use a local scratch path when the check must import project code, fixtures, or build output. If the file lives in the working tree, place and name it so the project's test runner will not collect it.

Do not add a gitignore rule, tracked scratch path, or CI/test-discovery entry to host a throwaway check. Never stage or commit these files. Remove them after the check unless the user asks to keep the reproducer. Prefer a one-off command over a temp file when it is enough.

## Failure routing

If existing evidence makes the cause clear, fix it directly and verify the affected path. Escalate to hard debugging only when the cause is unclear, one bounded reasonable fix failed, the same class of failure recurred, multiple root causes remain plausible, or performance, concurrency, or environment prevents discrimination.

## Hard debugging

Build the tightest practical feedback loop around the exact symptom. Minimize the reproducer when that narrows the hypothesis space. State a falsifiable hypothesis and make the smallest probe that distinguishes it; prefer targeted instrumentation at relevant boundaries over broad logging.

Each iteration must produce at least one of:

- new evidence;
- a falsified hypothesis;
- changed reproduction behavior;
- a discriminating observation.

Without one, do not mechanically repeat the direction. Change the probe, revisit assumptions, obtain the missing environment or artifact, or report the blocker.

Fix the root cause at the narrowest shared point supported by caller and data-flow evidence. Afterward, run the original reproducer and any earned regression test. Remove temporary instrumentation and throwaway harnesses from `/tmp` and the working tree unless the user asks to keep them.
