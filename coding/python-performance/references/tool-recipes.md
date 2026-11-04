# Local tools: prerequisites, interpretation and limits

These recipes run an authorized local `app.py`, including its application side effects.
Inspect the target and arguments first; do not run all tools together. Use a bounded workload
or duration, fresh output paths and installed versions' help. Missing tools remain unavailable;
no automatic network install, system tuning or privilege changes. Profile files can expose
source paths/data. Keep them local; don't upload or enable cloud AI optimization.

## Standard library: function calls and Python allocations

```sh
python -m cProfile -s cumulative app.py
python -X tracemalloc=10 app.py
```

cProfile prints a call summary. The second command only enables allocation tracing; it does
not print a report. At existing owned harness boundaries, take a snapshot after warmup,
another after fixed work and normal cleanup, and compare them:

```python
before = tracemalloc.take_snapshot()
# Fixed work followed by normal cleanup belongs here.
after = tracemalloc.take_snapshot()
for change in after.compare_to(before, "lineno")[:10]:
    print(change)
```

Import `tracemalloc` and start tracing before these boundaries (`-X` does that at startup).
This is an integration fragment, not a complete workload; the batch fixture is runnable.
Don't load `.prof`, `.lprof`, pickle or snapshots from untrusted sources. The bounded JSON
helper accepts its own documented schema, not serialized profiler objects.

## py-spy: sample first

```sh
py-spy record --duration 15 --output profile.svg -- python app.py
```

For an authorized running process, `--pid PID` replaces launching a target. Confirm identity
and permissions first. Linux child-launch may avoid elevated attach rights; macOS restrictions
differ. Permission denial means report/stop, not sudo, altered ptrace_scope, disabled SIP or
broader container capabilities. `--subprocesses` adds child scope where needed. `--native`
needs a supported platform and useful symbols. `--gil` misses active native work that releases
the GIL; do not use it as the only view. Avoid `dump --locals` by default. Samples are not
exact call counts and SVG width is not a chronological timeline.

## line_profiler: narrow to the implicated function

```python
from line_profiler import profile

@profile
def transform(records):
    return [record["value"] * 2 for record in records]
```

Enable with process environment `LINE_PROFILE=1` for a compatible installed release. Legacy
`kernprof -l -v app.py` remains another workflow. Don't leave undefined bare `@profile` in
ordinary code. One hot line containing a native call still does not expose native internals.

## Memray: native and Python allocations

```sh
python -m memray run -o memory.bin app.py
python -m memray summary memory.bin
```

Use a fresh destination. `run --native` adds native stacks when needed;
`--trace-python-allocators` changes allocation granularity and overhead. Missing symbols
limit attribution. CPython Linux/macOS are supported targets; WSL is Linux, not native Windows
support. Native stacks on macOS distributions can be incomplete. Host allocation reports are
not complete GPU memory reports. Treat binary artifacts as trusted local files.

## Scalene and Pyinstrument: discriminating additional views

Scalene separates Python/native/system activity and allocation/copy evidence. CLI changed
between major versions. For an installed verb-based CLI confirmed by `--help`:

```sh
python -m scalene run -o profile.json app.py
python -m scalene view --cli profile.json
```

Verify local `run --help` and `view --help` before use. Do not substitute a remote GUI or
AI provider. Never enable API-key forwarding during offline profiling. Scalene 2.x documents
Windows memory support; older CPU-only advice is not universal. Its own main README has
legacy snippets mixed with new syntax, another reason to check the installed CLI.

`python -m pyinstrument app.py` provides a local elapsed call-tree report when installed.
For async API integrations choose context mode deliberately: enabled attributes suspension
to the await context; strict filters other contexts; disabled interleaves observations.
That elapsed waiting is not CPU consumed by the coroutine.

## Optional new standard-library sampling

Versioned docs mark `profiling.sampling` added in 3.15. Only use if the target has the module
and CLI; a web documentation version does not prove runtime capability. Check
`python -m profiling.sampling --help` and its `run` help. Documented syntax includes
`python -m profiling.sampling run app.py`. Build/platform and async/native combinations have
restrictions. Do not combine all modes or assume compatibility across GIL/free-threaded builds.
Older environments retain cProfile or an already installed sampling tool.

## Provenance and version gates

Reviewed 2026-10-29; main/latest is not a pinned compatibility guarantee. No upstream code is vendored.
- CPython (PSF): https://docs.python.org/3.14/library/profile.html
- Sampling: https://docs.python.org/3.15/library/profiling.sampling.html
- py-spy (MIT): https://github.com/benfred/py-spy
- line_profiler (BSD): https://github.com/pyutils/line_profiler
- Memray (Apache-2.0): https://bloomberg.github.io/memray/supported_environments.html
- Scalene (Apache-2.0): https://github.com/plasma-umass/scalene
- Pyinstrument: https://github.com/joerick/pyinstrument/blob/main/docs/how-it-works.md
