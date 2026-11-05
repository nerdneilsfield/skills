---
name: python-debug
description: "Use when Python crashes, hangs, deadlocks, leaks tasks, raises an unexplained exception, or gives a wrong result that the first traceback and nearby diff did not explain, including any quick how or why question: tracebacks, pdb, faulthandler, stuck asyncio tasks, segfaults in native extensions, and import errors. Defer shared conventions to python. Not for an obvious failing test (python-testing), measured slowness (python-performance), broken installs (python-environments), or NaN and solver failures (python-numerics)."
license: MIT
compatibility: Requires Python 3. Attaching to a live process needs Python 3.14 or later, or py-spy, plus ptrace permission.
metadata:
  author: DengQi
---

# Python diagnosis from evidence

Find the first violated contract, not a patch that hides the symptom. A routine failure does not need this workflow: read the traceback from the bottom up, check the nearby diff, fix, and rerun. Continue here when the cause stays uncertain or the failure is a hang, a native crash, or intermittent.

## Build a loop first

1. Find one command that fails on this bug: a test, a script with a fixture input, or a replayed request. Run it and see it fail.
2. Make it faster and more deterministic. Pin the seed and clock, and narrow the input.
3. For an intermittent failure, loop it and record the rate. A fix claim needs the same exposure as the failure rate.
4. Record the interpreter, dependency versions, and exact invocation. Confirm that code is what runs: `python -c "import pkg; print(pkg.__file__)"`.

If no loop is possible, say so, list what you tried, and ask for the smallest missing artifact. Never call a speculative change a fix.

## Choose the next experiment

| Symptom | First move |
| --- | --- |
| Exception, wrong value | `python -m pdb -c continue script.py`, or `breakpoint()` at the first bad state; check `__cause__` and `__context__` |
| Hang in a live process | `py-spy dump --pid PID`; on 3.14+, `python -m pdb -p PID` |
| Hang you can restart | `faulthandler.dump_traceback_later(30, repeat=True)` near startup |
| Stuck asyncio | On 3.14+, `python -m asyncio ps PID` or `pstree PID`; otherwise `PYTHONASYNCIODEBUG=1` |
| Segfault, abort | `python -X faulthandler script.py`; then `cpp-debug` if the native frame is yours |
| `ImportError`, wrong module | `python -v`, `sys.path`, and a local file shadowing the package |
| Regression between versions | `git bisect run` with the loop command |
| Memory growth | `python-performance` |

## Gotchas

- `python -O` strips every `assert`, so a guard written with `assert` can vanish in production. Check how the failing deployment starts Python.
- A local `random.py`, `json.py`, or `test.py` shadows the standard module, and the error appears deep in an unrelated import. Check the module's `__file__` first.
- `except Exception` does not catch `asyncio.CancelledError` or `KeyboardInterrupt`, while a bare `except:` does and can swallow cancellation. Treat both as different outcomes.
- A task created with `create_task` and not stored can be garbage-collected mid-run, and an unawaited task's exception appears only at collection, if at all. Keep a reference and await it; prefer `TaskGroup`.
- A forked child inherits locks held by other threads and can deadlock on first use. Suspect this when a hang appears only with `fork`, threads, and `multiprocessing` together.
- An exception raised in a `multiprocessing` worker or a `Future` stays silent until `.result()` is called. A pipeline that never collects results reports success.
- `pdb` and `breakpoint()` hang under anything without a terminal. Set `PYTHONBREAKPOINT=0` in CI so a forgotten call cannot stall a run.
- `py-spy` and `pdb -p` need ptrace access and may be blocked by `kernel.yama.ptrace_scope` or a container. Report the block; do not change kernel settings without authorization.

## Isolate and repair

Trace back from the earliest bad state. State one falsifiable hypothesis, run the cheapest experiment that separates it from the alternatives, and change one thing at a time. Keep the failing evidence before editing. Remove temporary logging and `breakpoint()` calls before finishing.

Fix the responsible contract. A `sleep`, a broader `except`, or a retry does not establish a cause. Add a regression test through `python-testing`, then run the original loop and nearby tests.

Traces, heap dumps, and pdb sessions can contain secrets and user data. Keep them local and redact before sharing. Attach only to processes you are authorized to inspect.

## Report

Symptom and loop, evidence, supported cause or remaining hypotheses, the change, and exact checks. Distinguish a verified fix from an unconfirmed mitigation.

## References

- [faulthandler](https://docs.python.org/3/library/faulthandler.html), [pdb](https://docs.python.org/3/library/pdb.html), [asyncio debugging](https://docs.python.org/3/library/asyncio-dev.html), [Python development mode](https://docs.python.org/3/library/devmode.html), [py-spy](https://github.com/benfred/py-spy).
