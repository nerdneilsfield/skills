---
name: python-numerics
description: Use when Python array, matrix, scientific-computing or tensor code is numerically incorrect, memory-heavy or slow, including NumPy/SciPy layout, broadcasting, solvers, BLAS, JIT and existing accelerator-framework boundaries.
---

# Python numerical correctness and performance

Optimize the computation that the application actually needs, not a mathematical
lookalike with easier timing. CPU NumPy/SciPy are the baseline here; Numba,
NumExpr, JAX, PyTorch and CuPy are conditional options, not dependencies to install.
Custom CUDA kernels and framework migrations are separate work.

## Follow the computation from contract to evidence

1. **Define the contract.** Record shapes, dtype/accumulation precision, units,
   missing/non-finite-value policy, ownership and mutation, expected output,
   representative input distribution, error budget and latency/memory limits.
   Changing full distances into only nearest distances is valid only if callers
   need the latter. Changing precision or approximate algorithms needs agreement.
2. **Locate the actual cost.** Separate Python dispatch from native computation,
   allocation/copy, layout conversion, solver setup, threading, compilation and
   host/device transfer. A hot Python line can contain all of these.
3. **Change one evidenced cause.** Prefer a better algorithm or existing library
   routine before additional workers, compilation or a new framework. Account
   for temporaries and the output, not only input sizes.
4. **Revalidate both contracts.** Compare error/residual, failure handling and
   memory as well as comparable end-to-end time. Include conversion and validation
   costs where production pays them. Keep cold and steady-state measurements apart.

## Read only the relevant reference

| Observed problem | Offline reference |
| --- | --- |
| Copies, large broadcasting, strides, vectorization, aliasing | [Arrays and memory](references/arrays-and-memory.md) |
| Solvers, sparse formats, BLAS teams, repeated factorizations | [Solvers and native parallelism](references/solvers-and-parallelism.md) |
| Numba/NumExpr, GPU transfers, JAX/PyTorch/CuPy timing | [Compilation and device boundaries](references/jit-and-device-boundaries.md) |
| Precision changes, unstable results, benchmark acceptance | [Numerical validation](references/numerical-validation.md) |
| Provenance or refreshing a specific claim | [Verified source map](references/sources.md) |

The references are usable without following web links. When interpreting API
behavior, inspect the installed version's signatures/docstrings and local docs;
latest online docs do not authorize an upgrade. Missing optional tools mean
reporting the unavailable experiment, not installing them automatically.

Process-wide profiling and worker budgets belong to `python-performance` if
available; environment selection and package/CUDA compatibility belong to
`python-environments`. This skill remains usable alone for the numerical work;
if another named skill is needed but missing, identify it to the user rather
than globally searching for replacements. Do not duplicate those skills' rules.

## Runnable worked example

Run `python assets/blocked_distances.py` from this skill directory with an
already-installed NumPy. The [asset](assets/blocked_distances.py) computes minimum
squared distances while bounding **explicit arithmetic work arrays**, supports
strided/read-only inputs and rejects non-finite values or arithmetic overflow.
It does not load user data, install packages, benchmark arbitrary code or claim
an RSS cap. Its scalar finite-input validation is deliberately conservative;
include that cost when adapting it. See arrays reference for the derivation,
limitations and acceptance experiments.

## Hand off evidence, not a tool recommendation

Report: original contract → measured limiting stage → isolated change → numerical
and resource results → remaining regimes/risks. Record library/backend versions,
shapes, dtypes, thread counts, device, warm-up and synchronization policy. If no
representative workload or accelerator is available, supply the next bounded
experiment and mark execution unverified; do not invent speedups.
