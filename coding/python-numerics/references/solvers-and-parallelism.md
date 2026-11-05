# Solvers and native parallelism

## Solve the stated problem

A matrix operation can be slow because it solves a larger or harder problem than
needed. Establish whether the task is a square solve, least squares, constrained
optimization, eigenproblem or repeated update. `inv(A) @ b` forms a full inverse
when only a solution may be needed; choose an appropriate solver instead. A
singular or rectangular system needs a rank-aware formulation, not a faster
square solver. Check dimensions and installed-library batching semantics rather
than assuming one right-hand-side axis convention across releases.

Known structure earns specialized algorithms only when it is actually true.
Cholesky requires positive definiteness, not merely a symmetric-looking matrix.
A symmetric/hermitian solver can use only one triangle: inconsistent other entries
may go unnoticed. Validate the model's structure upstream. Do not select
`assume_a` because a benchmark was faster, or switch off finite checks without
an established finite-data boundary. Some native routines do not handle NaN/Inf
safely; a crash or hang is worse than a clean validation error.

## Amortize setup without reusing stale mathematics

For repeated `A x = b` with unchanged A, factor once and solve with new right-hand
sides. Illustrative SciPy pattern, only if SciPy is already available:

```python
from scipy.linalg import lu_factor, lu_solve
# A and B must be finite; caller retains ownership, so do not request overwrite.
factors = lu_factor(A)
X = lu_solve(factors, B)  # B contains multiple RHS columns for this 2-D example.
```

Reusing this factorization after A changes is incorrect even when the shape is
unchanged. Sparse solvers may separately reuse ordering/symbolic analysis when
structure is unchanged, but numeric values still require appropriate refactoring.
Record exactly what is invariant. Benchmark setup and solve separately, then
recombine them according to actual reuse count. Do not claim a single-call win
from an amortized repeated-call result.

For sparse matrices inspect format, index dtype, nonzero count and factorization
fill-in. A sparse input can produce a large factor. Accidental `.toarray()` can
be the real memory bottleneck. Conversion among CSR/CSC/COO costs time and storage;
choose a format for the next operation, not an unconditional favorite. Iterative
methods can save storage but require convergence criteria and a suitable
preconditioner. Compare residual, iteration count and failure frequency alongside
runtime; stopping early is not the same solution quality.

## Observe native teams before multiplying workers

NumPy/SciPy operations are not uniformly parallel. Many NumPy operations release
the GIL; many SciPy routines default to one thread; BLAS/LAPACK often have their
own teams. A Python worker pool around threaded matrix multiplication can create
nested parallelism. Inspect the loaded backend and effective thread configuration;
the package name alone does not identify OpenBLAS versus MKL or another backend.

The process-wide budget and context-switch/cache evidence belong to
`python-performance`. Here ask one numerical question: **which layer should own
parallelism for this workload?** Compare one large native solve with its measured
team versus multiple independent solves with smaller native teams. Tiny problems
may lose to team setup overhead; bandwidth-heavy kernels may stop scaling before
all cores are busy. Do not invent a universal thread count.

With already-installed `threadpoolctl`, a targeted experiment can use:

```python
from threadpoolctl import threadpool_limits, threadpool_info
# Import the numerical backend first, so its library can be discovered.
print(threadpool_info())  # inspect locally; redact absolute library paths before sharing
with threadpool_limits(limits=1, user_api='blas'):
    answer = A @ B
```

This controls supported native libraries, not all processes or arbitrary runtimes.
Environment variables must often be set
before the library initializes; modifying them later is not evidence of a changed
team. Avoid rewriting the user's shell configuration for an experiment.

## Accept numerical and operational improvement together

Compute a scaled residual such as `||A@x-b|| / (||A||*||x|| + ||b||)` with an
explicit zero-denominator convention. This is a useful backward-error indicator,
not a bound on forward solution error for a badly conditioned system. Include
known-solution fixtures and condition-sensitive cases. Factorization warnings,
non-convergence and different failure handling belong in the result table, not
just successful timings. Preserve a baseline and rerun after backend/version or
thread-policy changes; neither faster native code nor smaller residual alone
proves the application's mathematical result is acceptable.
