---
name: cpp-numerics
description: Use when creating or modifying CPU C++ matrix kernels, residuals, solvers, factor graphs or numerical-library adapters for SLAM, reconstruction, calibration or perception, including incorrect, unstable or slow numerical results.
---

# CPU numerical correctness and optimization

Start with the mathematical/data contract, then optimize the measured computation. Apply shared `cpp` policy and `cpp-performance` measurement discipline. Core scope: Eigen, Ceres/GTSAM, SO(3)/SE(3), sparse solvers and CPU BLAS/LAPACK. OpenCV/PCL/Open3D appear at data boundaries, not as complete API guides. CUDA is separate and deferred.


Shared language policy is `cpp`; build/vendor changes use `cpp-project-init` and shared thread/measurement policy uses `cpp-performance`. If a needed named skill is missing, ask the user to install that exact skill from this bundle. Do not globally search, fetch a substitute, automatically install or invent its contents; continue only independent model/data checks.

## Offline supporting materials

- For expression alias/lifetime, Eigen Map/stride and image/point-cloud adapters, read [Eigen and data boundaries](references/eigen-data-boundaries.md).
- For residual/Jacobian, whitening, manifold/quaternion, gauge or nonlinear convergence, read [nonlinear solvers](references/nonlinear-solvers.md).
- For sparse/BLAS phases, backend/thread experiments or numerical acceptance, read [sparse BLAS and validation](references/sparse-blas-validation.md).
- Each reference includes local examples/fixtures and decision criteria. Installed pinned library headers/tools are prerequisites; do not download them when unavailable. External URLs identify sources rather than replace the offline instructions.


## Establish the contract

Record library versions/build options, scalar precision, dimensions, storage/strides, coordinate frames, units, transform direction and pose/tangent conventions. Identify input distribution, reference result and acceptable error/latency/memory budgets. Inspect the actual selected backend and thread runtime rather than infer them from linked-library names.

Before tuning, reproduce incorrect results and check finite inputs, degenerate geometry, scale, rank and conditioning. A lower cost or smaller algebraic residual does not by itself prove physically correct geometry. Keep correctness fixes and performance experiments distinguishable.

## Eigen: evaluate the right expression

| Situation | Check / decision |
| --- | --- |
| Overlapping destination/source | Determine aliasing; use a necessary evaluated temporary or documented in-place operation |
| `noalias()` suggestion | Use only after proving destination does not overlap operands; it is a promise, not a safety check |
| Stored `auto` expression | Check referenced operand/temporary lifetimes; materialize an owning result when it must survive |
| External `Map` or block | Validate scalar type, alignment, row/column-major interpretation, stride, dimensions and buffer lifetime |
| Fixed 3×3/6×6 blocks | Measure local expression/layout choices; a large BLAS backend does not automatically accelerate tiny kernels |
| Linear solve | Choose decomposition for structure/rank/conditioning; verify residual rather than default to explicit inverse |

Example: for an existing square Eigen matrix `A`, `A = A.transpose()` risks aliasing; use `A.transposeInPlace()` when that operation fits, or materialize the transpose before assignment. Do not “optimize” it with `noalias()`. Do not insert `.eval()` everywhere either: unnecessary materialization costs allocation/copy work.

Check alignment rules against the project's Eigen/compiler/C++ versions and allocation path. Do not blindly add legacy aligned-allocation macros to every type; modern aligned allocation changes which paths need intervention. Preserve API/ABI compatibility across translation units with differing vectorization/alignment settings.

## Ceres, GTSAM and geometry

1. Check residual units, measurement covariance/whitening, robust-loss scale and initialization. Validate Jacobians using a suitable analytic/autodiff comparison or finite-difference check with scale-aware steps; a finite-difference discrepancy alone may reflect step size or a singularity.
2. Confirm manifold dimensions, local perturbation side and frame convention. Preserve the project's SO(3)/SE(3) representation; do not silently switch libraries or conventions.
3. Match quaternion **memory layout**, not just constructor syntax. Ceres `QuaternionManifold` uses `[w,x,y,z]`; `EigenQuaternionManifold` matches Eigen quaternion coefficient memory `[x,y,z,w]`. Confirm normalization and parameter-block lifetime. Never copy bytes across representations without proving layout.
4. Resolve gauge freedoms and unobservable/degenerate directions with justified anchoring, priors or appropriate formulation. Monocular scale can remain free after fixing one pose. Do not conceal rank deficiency with arbitrary damping or “fix” observable states without considering bias.
5. Profile residual/Jacobian evaluation separately from factorization/linear solve. Use a Schur strategy for appropriate BA block structure; choose dense/sparse/iterative methods from size, sparsity, conditioning, memory and measured convergence, not a universal solver preset.
6. For GTSAM, inspect variable ordering, elimination fill-in, factor construction and incremental relinearization behavior. Verify iSAM2 parameters against the installed version; do not copy old defaults blindly.

For existing Sophus projects, preserve the supported API/version and conventions. Maintenance status is not automatic authorization for a Sophus2 migration.

## Sparse and BLAS backends

- Inspect sparse format, index width, symmetry assumptions and ordering. Reuse symbolic analysis/factorization only when the corresponding sparsity/value invariants permit it; record what changed between solves.
- Compare backend changes on representative sizes including small fixed matrices. Include conversion/setup costs and memory, not just the backend kernel time.
- Thread budgets, nested application/solver/BLAS teams and backend control selection are owned by [cpp-performance parallelism/BLAS](../cpp-performance/references/parallelism-and-blas.md). Read that only when threading is implicated; keep numerical quality gates here. If unavailable, ask the user to install **`cpp-performance`** from this bundle, not search globally.
- New source/backend integration uses [cpp-project-init](../cpp-project-init/SKILL.md), the sole vendor/legal/offline owner. SuiteSparse licensing remains component-specific; identify the actual retained components when applying that policy.

## Image and point-cloud boundaries

Before zero-copy mapping, establish ownership and lifetime, layout, dtype, stride and alignment:

- OpenCV `Mat`: ROI/step may be non-contiguous; copies can share storage. Do not treat every image as packed owned bytes.
- PCL: point records may contain padding/alignment; an XYZ-looking struct is not automatically a tightly packed scalar array.
- Open3D: tensor dtype/strides and conversions may allocate. Measure boundary conversion/copy costs and keep this workflow CPU-only.

An explicit validated copy can be safer and faster overall than a fragile “zero-copy” adapter. State why a mapping is valid and what invalidates it.

## Acceptance evidence

Use a trusted reference or known invariants with absolute/relative tolerances appropriate near zero and across scales. Include nominal, noisy, degenerate, ill-conditioned and non-finite inputs relevant to the change; record seeds and failure handling. Validate derivatives/manifold updates when modified.

Report before/after time and memory **alongside** residual/error, convergence/iteration counts, failed cases and application quality (for example reprojection error, pose error with stated alignment/gauge, or reconstruction consistency). Lower precision, changed reduction order, fast-math or backend replacement must meet the accuracy budget; do not promise bitwise equality across backends or thread counts without testing it.

Hand off: model/data contract → observed error or bottleneck → isolated change → comparable numerical/performance results → unresolved regimes. If no project workload is available, provide the next experiment, not fabricated solver results.

## Version-matched references

Read only the applicable official material; the Eigen links use the versioned 3.4 documentation branch, and oneMKL uses Linux 2025.1. These are source references, not required project versions; use local pinned-version evidence when it differs.

- Eigen [aliasing](https://libeigen.gitlab.io/eigen/docs-3.4/group__TopicAliasing.html), [BLAS/LAPACK](https://libeigen.gitlab.io/eigen/docs-3.4/TopicUsingBlasLapack.html), [alignment](https://libeigen.gitlab.io/eigen/docs-3.4/group__TopicUnalignedArrayAssert.html).
- Ceres [modeling](https://ceres-solver.readthedocs.io/latest/nnls_modeling.html), [modeling FAQ](https://ceres-solver.readthedocs.io/latest/modeling_faqs.html), [solving](https://ceres-solver.readthedocs.io/latest/nnls_solving.html), [rank/covariance](https://ceres-solver.readthedocs.io/latest/nnls_covariance.html).
- GTSAM [ordering](https://borglab.github.io/gtsam/ordering/), [Sophus](https://github.com/strasdat/Sophus), [SuiteSparse](https://github.com/DrTimothyAldenDavis/SuiteSparse), [OpenBLAS](https://github.com/OpenMathLib/OpenBLAS), [oneMKL threading](https://www.intel.com/content/www/us/en/docs/onemkl/developer-guide-linux/2025-1/improving-performance-with-threading.html).
- [OpenCV Mat](https://docs.opencv.org/4.x/d3/d63/classcv_1_1Mat.html), [PCL](https://pointclouds.org/documentation/namespacepcl.html), [Open3D Tensor](https://github.com/isl-org/Open3D/blob/main/cpp/open3d/core/Tensor.h).
