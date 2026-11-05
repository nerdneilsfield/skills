---
name: python
description: "Use when writing, reviewing, or maintaining Python code, including alongside a Python specialist: data contracts, mutation, resource lifetime, failure behavior, and verification."
---

# Python: make the work and its boundaries explicit

This hub is the shared contract for ordinary Python: what an operation means, what it may mutate, what success or failure publishes, and which interpreter executes it. Measure that same work before changing how it runs. Specialists build on this hub. It is not a second copy of performance, numerics, environment, ML, or analysis procedures, and it is not permission to replace an existing environment.

## Choose the question, not a tool inventory

| Current task | Skill or reference |
| --- | --- |
| Data contract, mutation, resource lifetime, expected failure, or verification | [Engineering contract](references/engineering-contract.md) |
| Hotspots, Python versus native CPU, waiting, memory growth, event-loop stalls, or application scaling | [python-performance](../python-performance/SKILL.md) |
| Array or tensor shape, dtype, layout, broadcasting, numerical accuracy, solvers, BLAS, or JIT/device boundaries | [python-numerics](../python-numerics/SKILL.md) |
| Interpreter, uv, venv, Conda, Pixi, mirrors, locks, offline artifacts, or CUDA/native ABI | [python-environments](../python-environments/SKILL.md) |
| Classical ML or deep-learning splits, training, evaluation, checkpoints, or training-loop performance | [python-ml](../python-ml/SKILL.md) |
| Tabular, time, or missing data, join and group meaning, statistical summaries, or charts | [python-data-analysis](../python-data-analysis/SKILL.md) |

When a specialist row matches, load that skill alongside this hub's contract rules. Start with one specialist. Load another only when the evidence crosses its boundary. An ordinary Python change loads this hub or one specialist, not every skill. If a required named skill is missing, tell the user that exact name to install from this bundle; do not globally search, fetch a substitute, auto-install or invent its content. Continue independent work only.

## One connected operation

The running idea is a finite batch of records: establish units/IDs/missingness → preserve required ownership → transform/compute → check the result → publish or retain the previous good state. Numerical code adds shape/dtype/error tolerances; ML adds train/validation/test separation **before learning preprocessing**; analysis adds grouping/join/denominator semantics. These are additions to the same contract, not reasons to paste every workflow into every task.

- Preserve the selected project interpreter and supported versions. The helpers/examples state their own minima; this is not a mandate to migrate the application to the newest Python.
- Prefer straightforward functions, explicit data boundaries and existing project error models. Do not add Pydantic, a workflow engine, decorator framework or dependency injection container merely because examples mention validation.
- A copied outer list can still share inner arrays/dicts. Views and asynchronous closures do not create independent snapshots. Explain the needed mutation/lifetime guarantee before copying everything or removing a measured copy.
- Use context managers for resources and explicit cancellation/close protocols for concurrent work. Garbage collection is not a portable timing guarantee for external resources.
- Expected data errors, programmer bugs, cancellation and dependency failures are different outcomes. Do not silence all exceptions and label a partial output successful.

See the [original record example](assets/record-contract/README.md) for a self-contained, bounded illustration. Its Python-only checks do not validate NumPy, models, GPU execution or a production data schema.

## Verification and honest handoff

Reuse the project's existing test/lint/type tools when available; missing tools are not permission to install them. Tests preserve dataset identity, expected behavior and relevant numerical tolerances. Separate functional correctness from speed, memory and statistical claims. Profile only authorized programs/processes; keep private data out of shared traces and reports.

State the actual interpreter, checked behavior, measurement boundary, changed assumption, tradeoff and remaining uncertainty. Runtime guides and fixtures are readable offline; rebuilding an environment offline still needs compatible artifacts already present. Environment acquisition and source trust belong to `python-environments`, not duplicated installer commands here. CUDA kernels are outside this bundle's implementation scope; environment/device/measurement boundaries remain explicit.
