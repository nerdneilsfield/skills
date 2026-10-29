# Residuals, manifolds and nonlinear solver decisions

Read when implementing a residual/factor, changing a pose representation, diagnosing divergence/rank deficiency, or tuning Ceres/GTSAM. Keep CPU execution and the project's installed APIs; this is not a recommendation to migrate libraries.

## Establish one residual's meaning

Write the observed quantity, prediction, coordinate frame, units and noise model before choosing a solver option. Evaluate a tiny synthetic case with a known zero residual and a perturbed case with a predictable sign/direction. This catches inverse-transform and unit mistakes that an optimizer may otherwise absorb.

If the model supplies covariance, check the whitening transform and its convention. Keep raw physical residuals available for evaluation as well as whitened residuals used for optimization. Robust-loss scale is interpreted in the chosen residual scale; changing units without adjusting the model can alter which observations are treated as outliers. Do not compare total robust costs from different residual definitions as if they were the same metric.

## Jacobian and manifold checks

1. Distinguish ambient parameter dimension from tangent dimension. For a quaternion, four stored coefficients do not imply four independent rotation directions.
2. Record perturbation side (left/right), tangent ordering and frame. For SE(3), the same six numbers can mean different translation/rotation conventions in different codebases.
3. Check derivatives using the same local update as the implementation: compare directional residual changes under `Plus(x, ±h*d)` with the appropriate tangent-space Jacobian action. Sweep a few sensible step sizes; one finite-difference step is not definitive near singularities or cancellation.
4. Exercise identity, a small rotation and a nontrivial rotation/translation. Rotation equivalence must account for quaternion sign; coefficient equality is not the general geometric test.

For Ceres, inspect parameter-buffer memory, not just constructor arguments: `QuaternionManifold` expects `[w,x,y,z]`, while `EigenQuaternionManifold` matches Eigen's `[x,y,z,w]` coefficient memory. Use the matching manifold or an explicit validated conversion. Ensure normalized input, correct block size and buffer lifetime. Confirm whether the installed release uses `Manifold` or an older interface before changing code.

## Gauge and degeneracy are model properties

For BA/SLAM, identify transformations that leave observations unchanged. An unanchored world frame can yield free rigid motion; monocular reconstruction can additionally leave scale free. Fixing one pose does not necessarily fix scale. Choose constraints or priors justified by the physical problem and state their effect on uncertainty/bias.

A larger damping value may make a step computable without resolving unobservability. Check rank/conditioning, initialization and geometry before labeling a failure “solver instability”. Cover cases such as too few observations, nearly collinear/coplanar geometry where relevant, weak parallax and disconnected graph components. Do not claim covariance is meaningful without checking the observable subspace and noise assumptions.

## Choose tuning from the time breakdown

Capture Ceres `Solver::Summary`/`FullReport()` or the corresponding installed-version diagnostics, plus workload identity and options. Separate residual/Jacobian evaluation, preprocessing and linear solve time. Output availability varies by version; do not invent a field that the current API lacks.

| Evidence | Candidate experiment | Recheck |
| --- | --- | --- |
| Residual evaluation dominates | Remove repeated invariant work, inspect copying and safe evaluation parallelism | Same residual/Jacobian and evaluation cost |
| Small dense problem | Compare an appropriate dense solve against current choice | Total runtime, rank behavior, memory |
| BA point/camera block structure | Evaluate an appropriate Schur solver and ordering | Fill-in, linear solve time and convergence |
| Large sparse graph | Inspect sparsity/ordering/backend before more threads | Factorization memory and total solve time |
| iSAM2 update unexpectedly costly | Inspect new factors, ordering, relinearization settings and affected variables | Per-update quality/latency and consistency |

For GTSAM, elimination ordering can change fill-in and work without changing the intended model. Compare appropriate orderings on the same graph, not arbitrary graphs with different constraints. Incremental relinearization thresholds and skip policies trade work against approximation behavior; validate them over a sequence, not one update. Read the pinned release API before tuning.

## Acceptance record

Record termination reason, initial/final comparable cost, iteration/failed-step counts, residual distribution, geometric error and failed cases alongside time/memory. A solver returning “success” is not an application-quality guarantee; a time-budget termination may still produce a useful result under explicit criteria. Evaluate pose errors with the stated alignment/gauge treatment, not an alignment chosen after seeing the result.

## Offline residual/Jacobian fixture

A small two-parameter model exposes parameter-order and residual-sign errors without any external dataset. Let `p = [a,b]`, and use observations `(x,y) = [(0,1),(1,3),(2,5)]`. Define `r_i(p) = a*x_i + b - y_i`. At `[2,1]` all residuals are zero; at `[2,0]` all residuals are `-1`. The analytic Jacobian rows are `[0,1]`, `[1,1]`, `[2,1]`.

Use this fixture before a complex geometric factor:

1. Confirm the residual sign and parameter ordering with the two states above.
2. For each basis direction `d`, calculate `(r(p+h*d)-r(p-h*d))/(2*h)` and compare to `J*d`.
3. Sweep `h` over several orders, for example `1e-3`, `1e-5`, `1e-7` for this dimensionless double-precision toy. These are fixture settings, not universal geometry settings.
4. If every step has a large discrepancy, inspect the implementation/sign/order first. If only very small steps degrade, examine cancellation; if large steps disagree only in nonlinear cases, examine truncation and local-model validity.
5. Add the smallest real residual next, preserving its units and update rule. A toy linear check does not validate a camera model or distortion Jacobian.

For a manifold parameter, replace `p±h*d` by the implementation's actual local `Plus(p, ±h*d)`. If the API returns an ambient Jacobian, compare after applying the correct local update Jacobian; do not compare matrices of different meaning just because their sizes can be made to match.

### Whitening fixture

For independent two-axis measurement noise with standard deviations `sigma = [2, 0.5]`, a raw residual `[2, 0.5]` should whiten to `[1,1]`. The whitened squared norm is 2, while the raw squared norm is 4.25. This checks that standard deviation, rather than variance, divides the residual and that row-wise Jacobians receive the same scaling.

For correlated SPD covariance `S = L*L^T`, solve the lower-triangular system `L * whitened = raw`; do not form an explicit inverse merely to whiten. Reject or explicitly handle a covariance that fails the chosen positive-definite factorization. Apply the same transform to Jacobian rows. For semidefinite measurement models, decide the supported subspace rather than silently forcing an SPD routine through jitter.

### Quaternion boundary fixture

With Ceres versions providing `Manifold`, a stable Eigen quaternion parameter block can be associated with the matching manifold as follows. This is integration context, not a complete optimization problem:

```cpp
Eigen::Quaterniond q = Eigen::Quaterniond::Identity();
ceres::Problem problem;
problem.AddParameterBlock(q.coeffs().data(), 4);
problem.SetManifold(q.coeffs().data(), new ceres::EigenQuaternionManifold);
// Add compatible residual blocks and solve while q's coefficient storage stays valid.
```

This snippet assumes the default Problem ownership behavior for the allocated manifold. If the existing project changes ownership options, honor its corresponding destruction contract. Do not put `q` in a container that can reallocate while Problem retains its pointer. Inspect installed headers if the API is absent; that is not permission to fetch a new solver version.

Use identity and a 90-degree rotation about a chosen axis. Confirm the expected rotated basis vector through the project's transform convention. Explicitly test converting the same rotation through each boundary: Eigen coefficient memory, any serialized `[w,x,y,z]` representation, and the solver parameter block. This detects a byte-layout error that normalizing the wrong coefficients will not repair.

## Offline failure triage

| Observation | Next local check | Not a valid shortcut |
| --- | --- | --- |
| Cost changes when changing world origin | Check expected gauge invariance and transform convention | Add a stronger arbitrary prior immediately |
| Cost falls but reprojection worsens | Verify residual set, whitening/loss and evaluation dataset | Treat solver termination as quality proof |
| NaN on first iteration | Evaluate each residual/Jacobian at initial parameters; locate first non-finite value | Increase iteration limit |
| Huge update from plausible input | Inspect rank, scaling, manifold Jacobian and initialization | Turn on all solver tolerances at once |
| Only incremental sequence drifts | Replay the same factor sequence and inspect update/relinearization behavior | Validate only the final batch solve |

If installed library diagnostics or headers are unavailable, retain the failing input/model contract, use the analytic fixtures above to test adapter logic where possible, and label library integration unverified. Offline means using available evidence honestly, not guessing undocumented APIs.

## Sources to consult

- Ceres [modeling](https://ceres-solver.readthedocs.io/latest/nnls_modeling.html), [modeling FAQ](https://ceres-solver.readthedocs.io/latest/modeling_faqs.html), [solving](https://ceres-solver.readthedocs.io/latest/nnls_solving.html), [covariance/gauge](https://ceres-solver.readthedocs.io/latest/nnls_covariance.html). `latest` is not a substitute for the installed version's API.
- GTSAM [ordering](https://borglab.github.io/gtsam/ordering/) and [C++ API documentation](https://gtsam.org/doxygen/); match version-specific iSAM2 parameters. [Sophus source](https://github.com/strasdat/Sophus) is a convention/API reference for existing users, not an automatic migration target.
