# Feedback and Debugging

Default to simple functional verification and evidence that the changed code can run. Often one existing focused check, smoke run, or worked example proves both. For text/config-only edits, a relevant static check is enough. Deep does not change this default.

Implement a runnable version first by default, then check the real behavior and hand it over for use. User reports, real inputs, and observed failures usually provide better next-step evidence than agent-invented scenarios. Do not hold delivery for a speculative test suite. TDD remains useful when explicitly requested, when an existing failing test already defines the task, or when a small test-first loop directly helps solve an observed bug; it is not a prerequisite for starting implementation.

Choose one useful check, not a ladder of checks to run in sequence:

- Feature: run a representative input through the changed path and inspect the expected result; use an existing focused test if cheaper.
- Bug: run the reported reproducer and confirm the symptom is gone.
- Build/import change: compile, typecheck, or load the affected entry point as appropriate.
- Text/config: inspect the diff or use the relevant parser/config check.

Stop when existing evidence is sufficient. Fresh evidence must match the claim: a parser check cannot prove runtime behavior, and a broad suite cannot prove an unreproduced symptom is fixed.

Do not turn acceptance into an exhaustive test campaign. When a failure is extremely unlikely and unsupported by current evidence, do not add a test for it. Do not invent numerical probabilities; look for a reported symptom, actual reachable failure in the changed path, or an explicit requirement. Add checks beyond basic functionality only when that evidence makes them useful. A label such as Deep, public API, or migration is not by itself a reason for a large suite, fuzzing, stress tests, or a combinatorial edge-case matrix. Honor checks explicitly required by the user or repository.

## Permanent tests

Do not add a permanent test merely because code changed. Keep one only when the behavior deserves future protection, its expected result comes from outside the implementation, it can falsify a plausible wrong implementation, and its maintenance cost is justified.

Reject tests that only assert field presence, parameter forwarding, mock call counts, private implementation, a constant against itself, or an expected value recomputed by the algorithm under test. A successful one-time smoke or reproducer need not remain in the repository.

Consider a permanent test only after the independent-oracle rule already passes and a concrete regression risk justifies maintaining it. An observed bug or explicitly required contract may justify one focused test; a merely imaginable rare failure does not. Prefer reusing an existing check or running a one-time functional example when sufficient. For text, simple config, imports, and mechanical wiring, targeted static or runtime verification is usually enough.

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

Fix the root cause at the narrowest shared point supported by caller and data-flow evidence. Afterward, run the original reproducer and any earned regression test. Remove temporary instrumentation and throwaway harnesses unless they have an explicit continuing use.
