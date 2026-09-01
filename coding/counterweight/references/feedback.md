# Feedback and Debugging

Use the cheapest feedback that can answer the current question, roughly in this order:

1. syntax or parser check
2. diagnostics or typecheck
3. compile
4. existing relevant tests
5. small smoke test
6. worked example or golden output
7. real reproducer

Stop when existing evidence is sufficient. Fresh evidence must match the claim: a parser check cannot prove runtime behavior, and a broad suite cannot prove an unreproduced symptom is fixed.

## Permanent tests

Do not add a permanent test merely because code changed. Keep one only when the behavior deserves future protection, its expected result comes from outside the implementation, it can falsify a plausible wrong implementation, and its maintenance cost is justified.

Reject tests that only assert field presence, parameter forwarding, mock call counts, private implementation, a constant against itself, or an expected value recomputed by the algorithm under test. A successful one-time smoke or reproducer need not remain in the repository.

For meaningful behavioral logic, bugs with a stable seam, public contracts, security boundaries, migrations, and data invariants, a focused permanent test often earns its cost. For text, simple config, imports, and mechanical wiring, targeted static or runtime verification is usually enough.

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
