# Evaluations

Costly, model-backed checks live here. Deterministic checks stay in `tests/` and run in CI; nothing here runs in CI.

- `trigger/`: 220 blind routing queries for the C++ and Python skills, and the runner. Compare two revisions on the same queries: `python3 evals/trigger/run_trigger.py HEAD~1 old` then `... WORK new`. Run each side three times before trusting a small difference. `claude` must be on `PATH`. The query set leans towards knowledge questions; `dataviz` and other built-in skills can still load.

Keep a holdout: do not tune descriptions against every query you later report.
