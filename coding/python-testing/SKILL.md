---
name: python-testing
description: "Use when writing, fixing, organizing, or reviewing Python tests, including any quick how or why question: pytest fixtures, parametrization, mocks, async tests, flaky or order-dependent tests, coverage gaps, and test configuration. Defer shared conventions to python. Not for an unexplained production failure (python-debug), new project scaffolding (python-project-init), or benchmarks (python-performance)."
license: MIT
compatibility: Requires Python 3. Uses the project's test runner; pytest examples assume pytest 9.
metadata:
  author: DengQi
---

# Python tests that can fail for the right reason

A test earns its place by failing when the behavior breaks and staying green when only the implementation changes. Use the project's existing runner and layout. Do not migrate `unittest` to pytest, add plugins, or raise coverage as a side effect of another change.

## Choose what to test

- Test through the public boundary a caller uses. Assert on returned values, published state, and raised errors, not on private calls.
- For a bug, write the test first and watch it fail for the reported reason. A test first seen green proves nothing.
- Fake what you own or run it for real (`tmp_path`, an in-memory or local service). Mock only slow, paid, or nondeterministic edges such as the network and the clock.
- Use `@pytest.mark.parametrize` when cases share a body. Give each case an `id` when values do not read well.
- Reach for Hypothesis only for invariants over wide input, and only if the project already has it or the user agrees.
- Compare floats with `pytest.approx`, choosing the tolerance from the error model rather than until it passes. Array shape, dtype, and tolerance questions belong to `python-numerics`.

## Gotchas

- `patch` where the name is looked up, not where it is defined: after `from a import f`, module `b` needs `patch("b.f")`. Patching `a.f` leaves `b` untouched and the test silently exercises the real function.
- A plain `Mock` accepts any attribute or argument, so it keeps passing after the real signature changes. Use `create_autospec` or `patch(..., autospec=True)`.
- A mutable default in a session or module fixture leaks state between tests. Widen fixture scope only for measured cost, and treat the shared object as read-only.
- `pytest.raises(Exception)` also passes on an unrelated `TypeError` from a broken test. Name the specific type and add `match=`.
- `async def` tests need a plugin such as pytest-asyncio or anyio, configured the way the project already does it. Without one they fail or skip; they do not quietly run.
- Without `strict`, a misspelled `@pytest.mark.slwo` only warns, and an `xfail` test that now passes stays green. See the settings below.
- 100% line coverage says each line ran, not that anything checked its result. Use coverage to find unexecuted branches, never as evidence of correctness.

## Flaky and order-dependent tests

Reproduce before changing anything. Run the failing test alone, then in the full suite. Passing alone and failing together means shared state: look for module globals, environment variables, the working directory, a cached singleton, or leftover files.

Control the source of randomness instead of retrying: inject the clock, seed the generator and log the seed, and wait on an observable event with a bounded timeout rather than `sleep`. Do not add a rerun plugin to hide a failure; say so if the test must be quarantined, and record why.

## Configuration for a new or requested setup

pytest 9 reads native TOML from `[tool.pytest]`; older versions use `[tool.pytest.ini_options]`, and the two tables cannot coexist.

```toml
[tool.pytest]
minversion = "9.0"
strict = true
addopts = ["--import-mode=importlib"]
testpaths = ["tests"]
```

`strict = true` enables strict config, markers, parametrization IDs, and xfail, so register custom markers under `markers`. With `importlib` mode, tests do not import each other through `sys.path`; shared helpers belong in `conftest.py` or an importable package.

## Report

State the exact command, interpreter, pass, fail and skip counts, and any test you did not run. Report a skip as a skip. Report whether a new regression test was seen failing before the fix.

## References

- [pytest good practices](https://docs.pytest.org/en/stable/explanation/goodpractices.html), [unittest.mock: where to patch](https://docs.python.org/3/library/unittest.mock.html#where-to-patch).
