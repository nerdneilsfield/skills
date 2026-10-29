# Sparse/BLAS experiments and numerical acceptance

Read for backend changes, sparse factorization cost, nested parallelism, precision changes or a claimed numerical-kernel speedup. Use the existing `cpp-performance` measurement workflow; this adds the numerical contract, not another benchmark framework.

## Verify the operation before the backend

Record matrix dimensions, scalar type, sparsity pattern, index width, symmetry/storage convention and expected rank. Confirm that the selected decomposition's assumptions hold: “symmetric” is not “positive definite”, and a solver completing does not prove a well-conditioned problem. Prefer solving the requested system over explicitly forming an inverse unless the inverse itself is the required output.

Separate matrix assembly, conversion, symbolic analysis, numeric factorization and solve time. If only right-hand sides change, factorization reuse may be possible. If values change, numeric factorization usually needs updating; if the sparsity pattern changes, symbolic reuse needs a backend-supported contract. Reuse is conditional, not permission to retain stale factors.

Inspect fill-in and peak memory as well as arithmetic time. Include format conversion and adapter copies in end-to-end comparison. For SuiteSparse, verify the actual components and their build options/licenses; one component's permission or threading model does not describe the entire collection.

## When thread ownership is implicated

Use the single [CPU parallelism/BLAS policy](../../cpp-performance/references/parallelism-and-blas.md) for budgets, controlled outer/inner comparisons, startup/global/local controls and runtime verification. This file owns numerical acceptance, not a second thread-control recipe. Measure small fixed matrices separately from large kernels; preserve phase boundaries and the same quality budget when applying that experiment.

## Numerical acceptance before timing acceptance

Define tolerance from the problem's error budget before comparing results. For scalar values, a useful form is `abs(actual-reference) <= atol + rtol*abs(reference)`; choose `atol` for near-zero quantities and units, not a universal magic constant. Use a stated norm and scale for vectors/matrices. Handle non-finite values separately: ordinary tolerance arithmetic is not a valid NaN policy.

For a linear solve, report residual and, when a trusted reference solution exists, solution error. A scaled residual such as `||Ax-b|| / (||A||*||x|| + ||b||)` needs consistent norms and explicit zero-denominator handling; a small backward residual can coexist with large solution error for an ill-conditioned system.

Select relevant fixtures rather than every possible matrix:

- Nominal dimensions and realistic data distribution.
- Empty/boundary dimensions only where the API permits them; odd/non-vector-width sizes for changed SIMD paths.
- Rank-deficient or ill-conditioned input with documented rejection or supported solution behavior.
- Large/small scales, outliers, noisy inputs and non-finite data that reach this interface.
- Repeated runs/seeds and representative thread counts for reductions or parallel solvers.

A double-precision result can be a useful comparison for a float experiment, but it is not automatically ground truth. Prefer analytic small cases, trusted independent computation or conserved/geometric invariants as appropriate. State which reference was used and why it is trustworthy.

If precision, reduction ordering, FMA contraction, fast-math, compiler flags or the backend changes, repeat both numerical and application-quality checks. Do not promise bitwise equality across thread counts/backends. Do not waive a quality failure because runtime improved.

## Small report contract

Record: input/seed and model → library/build/backend/thread configuration → phase timings and repeated-run spread → residual/error/quality metrics → memory and failures → acceptance budget/result. Retain the baseline configuration so a claimed gain can be reproduced. Missing hardware, workload or reference results means a proposed experiment, not measured improvement.

## Offline experiment worksheet

Do not need a new benchmark package to start. Use the project's existing executable/test target with fixed input and a local monotonic timer, or its already-supported benchmark harness. Keep fixture creation and source acquisition outside the timed operation. Capture at least:

```text
input_id / seed:
shape / nnz / scalar / index width:
backend / version / threading build:
outer threads / effective inner threads:
compiler / flags / revision:
assembly / conversion / analysis / factorization / solve times:
repetitions / warmup policy / timing spread:
scaled residual / reference error / finite check:
application quality / failed cases / peak memory:
```

Store samples per repetition, not just the fastest time. Use the configurations selected by the [shared parallelism policy](../../cpp-performance/references/parallelism-and-blas.md), while retaining the phase/quality fields above. A setup phase moved outside only one timer invalidates the comparison; overlapping timings require uncertainty rather than an automatic speed claim.

## Small local numerical fixtures

These fixtures can be encoded in existing Eigen/solver tests without network datasets. They are intended to check distinct contracts, not benchmark realistic SLAM performance.

| Fixture | Input | Expected observation |
| --- | --- | --- |
| Unique SPD solve | `A=[[4,1],[1,3]]`, `b=[6,7]` | `x=[1,2]`; finite result, near-zero residual |
| Exact zero case | `A=I`, `b=[0,0]` | `x=[0,0]`; scaled-residual denominator may be zero and must be handled explicitly |
| Singular inconsistent system | `A=[[1,1],[2,2]]`, `b=[1,3]` | No exact solution; declared rank-deficient/least-squares behavior, never an invented unique exact solution |
| Same sparsity, changed values | Change SPD diagonal from `[4,3]` to `[5,4]` | Old numeric factors invalid; a fresh solve must use new values |
| Changed sparsity | Add a formerly absent off-diagonal entry in a larger sparse fixture | Revalidate symbolic-analysis reuse contract |
| Non-finite input | Insert NaN into one coefficient | Explicit rejection or documented propagation; tolerance comparison must not silently pass |

For the SPD example, manually compute `A*[1,2]=[6,7]` to establish an independent reference. Compare a solve result with `atol + rtol*|reference|` component-wise or an explicitly documented norm. For a general well-scaled double toy, tight tolerances may be reasonable, but derive production tolerances from measurement noise, accumulated computation and the downstream quality budget.

For the singular example, a generic LU/Cholesky “success” flag is not enough: inspect rank/support and residual. A least-squares solver may return one minimizer or a minimum-norm result depending on its contract. Tests must assert that declared contract rather than demand `[1,2]` from an underdetermined model.

### Minimum quality gates for a backend experiment

1. The supported input contract and failure behavior remain unchanged, or an intentional change is documented.
2. Every relevant fixture passes finite/rank/error checks with the predeclared criteria.
3. Representative application cases preserve the numerical quality budget, including failures and outliers, not only average cost.
4. Timings use comparable complete phase boundaries and repeated samples; speed claims include spread and environment.
5. New source/backend integration follows the sole [cpp-project-init vendor/offline policy](../../cpp-project-init/references/vendor-and-offline.md). A faster system-installed BLAS is an experiment result, not authorization to silently change distribution policy.

These checks require no external documentation at runtime. When the exact installed backend cannot be identified, report that uncertainty and stop short of selecting backend-specific thread/API settings.

## Sources to consult

- Eigen [BLAS/LAPACK integration](https://libeigen.gitlab.io/eigen/docs-3.4/TopicUsingBlasLapack.html) and [sparse solver tutorial](https://libeigen.gitlab.io/eigen/docs-3.4/group__TopicSparseSystems.html): versioned Eigen 3.4 documentation; check against the project's pinned headers/build, rather than upgrading to match a link.
- [OpenBLAS README](https://github.com/OpenMathLib/OpenBLAS) and [runtime settings](https://www.openmathlib.org/OpenBLAS/docs/runtime_variables/): inspect the actual build type and release.
- [oneMKL threading guide](https://www.intel.com/content/www/us/en/docs/onemkl/developer-guide-linux/2025-1/improving-performance-with-threading.html): versioned Linux 2025.1 reference; actual threading controls are owned by the shared performance parallelism policy and must match the installed platform/build.
- [SuiteSparse](https://github.com/DrTimothyAldenDavis/SuiteSparse): follow the selected component's documentation and license, not collection-wide assumptions.
