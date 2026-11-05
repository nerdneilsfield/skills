# Evaluations

Costly, model-backed checks live here. Deterministic checks stay in `tests/` and run in CI; nothing here runs in CI.

- `trigger/`: 220 blind routing queries for the C++ and Python skills, and the runner. Compare two revisions on the same queries: `python3 evals/trigger/run_trigger.py HEAD~1 old` then `... WORK new`. Run each side three times before trusting a small difference. `claude` must be on `PATH`. The query set leans towards knowledge questions; `dataviz` and other built-in skills can still load.
- `behavior/`: with-skill and without-skill runs, with the case files, fixtures, harness, and `REPORT.md` from the run at `feb683c`. The harness uses the fixed root `/tmp/behavior-eval`: copy `evals/`, `fixtures/`, and `harness/` there, unpack the revision under test into `skills/` with `git archive`, then run `python3 harness/run_full.py` detached. `pytest` and `coverage` must be available, or two Part B checks record NA. Cost was about $3.88 for 100 Sonnet runs.

Keep a holdout: do not tune descriptions against every query you later report.
