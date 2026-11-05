# From a record boundary to a trustworthy result

Python makes it easy to write a short computation. The difficult part is proving that the computation still means the same thing after data, environments and execution strategy change. Follow one operation through its lifetime: read a batch, establish its meaning, compute a candidate, verify it, then publish. Read just the section relevant to the current task; this is not a compulsory rewrite checklist.

## 1. Establish meaning before representation

A point record is not merely three numbers. Are coordinates metres or millimetres? Can missing values occur? Are IDs exact strings or quantities? Is the order meaningful? Is an empty batch valid? If the input is a table, what does one row represent, and what are the join/grouping keys? A fast calculation on the wrong unit or duplicated rows is still wrong.

A weak boundary takes whatever object arrives and lets errors emerge deep in the pipeline:

```python
# Ambiguous: may mutate shared inputs, silently coerce IDs, or mix units.
for row in rows:
    row['xyz'] = [float(v) for v in row['xyz']]
    published.append(row)
```

An explicit small boundary returns a prepared value before publication:

```python
candidate = prepare_records(rows, unit='mm')  # validates and owns a finite batch
published = candidate                       # after complete preparation succeeds
```

The [original executable](../assets/record-contract/records.py) implements that precise boundary with only stdlib and active self-checks. It rejects malformed/duplicate/nonfinite rows, preserves IDs and produces owned coordinate tuples. The [asset README](../assets/record-contract/README.md) explains the accepted sizes and accuracy limits. This does not mean every application should convert coordinates to Python float or reject extra fields. Reuse an existing validated schema; validate at the trust boundary rather than repeatedly in an inner loop.

For arrays, validation also includes shape, dtype, strides/contiguity, mutation/aliasing, device and precision budget. The numerical specialist owns those details. For ML, fit scalers, imputers, feature selection and other learned transformations using training data only; evaluating the final model on data already used to choose its transformation is not a clean test. For analysis, row counts alone do not expose an unintended many-to-many join. Those domain contracts are not replaced by generic type hints.

**Check:** empty and malformed input, duplicate IDs, unit mismatch, invalid tail and boundary sizes. Include the case most likely to be silently coerced: a boolean is an `int` subclass, but may not be a meaningful numeric observation. IDs with leading zeros must not accidentally become numbers.

## 2. Mutation is the ownership question Python does not hide

Passing an object passes a reference. Assignment does not clone it, and `list(existing)` copies only the outer list. That can be exactly what you want for immutable shared data, or a race/logic bug for mutable records.

```python
# Bad if deferred work needs the state as it was at submission.
pending = lambda: compute(rows)
rows.clear()
```

Choose the smallest ownership guarantee that actually matches the work:

- Immediate read-only work can borrow caller data during the call.
- Deferred work can take ownership of a freshly created value or retain a documented immutable snapshot.
- A stable snapshot may require copying nested mutable contents, but copying every object can create a memory spike and unnecessary serialization.
- An array view can avoid copying yet retain an enormous base allocation or reflect later mutations. “No copy” is a semantic decision as well as a performance one.

Do not solve every problem with `deepcopy`: some objects represent handles, shared caches or native allocations with their own copy rules. Prefer explicit data transfer at the boundary. Frozen containers/dataclasses do not necessarily freeze objects nested inside them. A reference count reaching zero is not an application protocol for closing sockets, device buffers, worker processes or figures.

**Check:** mutate/destroy caller-owned containers after scheduling; ensure the intended result remains stable. For a deliberately shared object, check the synchronization and ownership lifetime instead of asserting a snapshot. Inspect memory retained by views/closures when a supposedly freed batch remains reachable.

## 3. Failure defines what publication means

Preparing into a candidate gives a clear all-or-nothing boundary for a finite batch. If parsing the final record fails, prior published state remains intact. It costs extra peak memory and does not roll back external side effects already performed.

For large streams, buffering everything may be unacceptable. Make the policy explicit instead:

- A chunk can be its own transaction with an acknowledged ID/checkpoint.
- A partial output can be useful if it is clearly marked incomplete and consumers understand that status.
- Retrying requires a policy for duplicate writes and partially completed effects; a retry loop alone is not idempotence.

```python
# Bad: invalid data, programming errors and unavailable storage all look successful.
try:
    result = build_result(records)
except Exception:
    result = []
```

Catch a specific expected error at the layer that can decide what to do. Preserve the original exception when it is useful for debugging, and avoid leaking private records/tokens in logs. Cleanup belongs in a context manager or `finally`; cancellation should not be swallowed as a generic recoverable data error. In asynchronous code, use the selected Python/runtime library's cancellation semantics, and release resources before propagating cancellation.

```python
with open(local_input, 'r', encoding='utf-8') as source:
    candidate = parse_known_format(source)
# File is closed even if parsing fails. Publishing remains an explicit next step.
```

This is a resource pattern, not permission to read arbitrary paths. Local files and profiler traces still require the user's task scope. Never load untrusted pickle/joblib/checkpoint/profile objects merely to inspect them; many deserialization formats can execute code or are unsafe to parse as trusted state. Use bounded simple evidence formats for portable inspection, and follow the ML specialist's artifact trust boundary for actual model loading.

**Check:** malformed final item, expected dependency failure, cancellation at a publication boundary, and retry after a partially completed external operation. A self-check that prints PASS is not evidence that an unexecuted error path is covered.

## 4. Choose concurrency after identifying where time goes

A slow wall-clock operation may spend time in Python execution, native kernels, I/O, locks, child processes, accelerator execution or a queue. A single CPU percentage or a Python line with high elapsed time does not identify the cause. Performance guidance (the `python-performance` skill) owns profiler choice and attribution.

Keep these distinctions while designing a minimal repair:

- `async` helps overlap supported waiting; putting a long CPU loop in a coroutine still blocks its event loop.
- Threads can help when blocking/native work permits concurrency. Do not assume every extension releases the GIL, that every build has one, or that free-threaded Python removes application data races.
- Processes isolate interpreter state but add startup, serialization, memory and lifecycle costs. Inspect the actual supported start method and use an import-safe entrypoint; do not assume Linux/fork behavior on all versions/platforms.
- A native library may have its own thread pool. Outer workers multiplied by inner BLAS/OpenMP teams can increase contention and memory without doing more useful work.

Use bounded in-flight work and stop producing obsolete results. Closing the UI/service/notebook must not abandon workers still holding application state. Await/join/cancel using the existing facility's documented protocol; cancellation does not guarantee interruption of arbitrary blocking native code. When a newer request supersedes an older one, validate freshness at publication even if the old computation cannot stop immediately.

**Check:** workload equivalence, worker startup/teardown, failure propagation, queued memory and actual useful concurrency. Do not introduce a new pool or scheduler just because the language has one.

## 5. Verification connects correctness and performance

Record a compact experiment contract: input identity/size, work completed, interpreter and relevant packages, thread/device settings, timing boundary, correctness metric and memory measure. Changing any of these may create a different experiment. A microbenchmark can help isolate an operation but does not prove an end-to-end pipeline improves.

- Run an ordinary correctness baseline first. For floating output, justify tolerances using units, scale, conditioning and expected precision; “it looks close” is not a criterion.
- Separate warm-up/import/compilation/startup from steady state if the application makes that distinction, but do not silently discard latency users actually experience.
- Use repeated samples under comparable conditions. Medians/tails and allocator/RSS/device measures answer different questions; do not replace one with another.
- Follow the least complex supported repair. Confirm that it improves the actual target while preserving accuracy, memory budget, cancellation and error behavior.

A vectorized operation can remove Python overhead while creating a huge broadcast temporary. A different dtype can be faster while losing required precision. More workers can increase CPU usage while reducing throughput. A GPU timer without the relevant synchronization can time only command submission. Each is a contract change to examine, not an automatic optimization.

The environment specialist supplies interpreter/ABI and artifact evidence, numerical guidance checks mathematical equivalence, ML checks leakage and evaluation, and analysis checks statistical meaning. Load these additional references when the current evidence needs them; do not require all six specialists for a small local function.

## Provenance and version boundaries

Original explanations and examples, prepared 2026-10-29. Python helpers declare Python 3.9+ and do not force that version on existing applications. Newer profiler/free-threading/package-manager capabilities are gated in their owning specialist references. External links are provenance, not steps required to understand this document:

- Python data model and object semantics: https://docs.python.org/3/reference/datamodel.html
- Context managers and compound statements: https://docs.python.org/3/reference/compound_stmts.html#the-with-statement
- asyncio cancellation/task contracts: https://docs.python.org/3/library/asyncio-task.html
- multiprocessing programming guidance: https://docs.python.org/3/library/multiprocessing.html#programming-guidelines
