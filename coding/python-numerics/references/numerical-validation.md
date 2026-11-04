# Numerical validation: speed is conditional on the answer

## Write a testable contract before choosing precision

Record storage dtype, accumulation dtype, shape and axis semantics, coordinate
scale/units, missing values and allowed mutation. Establish a trustworthy baseline:
a small simple implementation, analytic fixture, higher-precision calculation or
independent solver. Using the same optimized expression twice does not provide
independence. Random seeds aid reproduction but do not replace deliberately
constructed edge cases.

Choose tolerances based on application scale and acceptable error. An absolute
bound handles near-zero values; a relative bound addresses scale. Default
`allclose` can be too permissive near zero and its broadcasting can conceal an
incorrect shape, so assert shape and intended dtype separately first. Decide
whether NaNs are allowed; treating matching NaNs as equal can conceal two failed
computations. Check counts and locations of non-finite outputs separately.

For changed reductions, batch order, backend or parallelism, bitwise equality may
not be realistic. Floating-point operations are not associative: reordering can
change cancellation and rounding. Decide whether the contract requires exact
reproducibility, bounded error or a downstream metric. Do not weaken a failed
tolerance until the change passes without understanding the error.

## Challenge the optimization, not just nominal inputs

- Dtype reduction: include large and tiny magnitudes, sums with cancellation and
  range boundaries. Integer overflow and floating overflow have different
  behavior; input conversion may already lose information before computation.
- Reused buffers: include overlapping views, read-only inputs and a check that
  callers' arrays remain unchanged. One correct output can coexist with corrupted
  input for the next iteration.
- Layout changes: use C/F contiguous, sliced and negative-stride arrays. Include
  the conversion in end-to-end timing if performed for each call.
- Solver changes: include rank deficiency, near singularity and inconsistent
  structural assumptions. A tiny residual does not guarantee small forward error
  when the problem is ill-conditioned.
- Approximation: evaluate worst-case or meaningful quantiles of error as well as
  mean error, and document missed neighbors/convergence failures if relevant.
- Device/backend changes: use the same dtype and precision policy, finite-input
  checks and domain metrics. Float64 may help but cannot fix the mathematical
  conditioning of a problem.

For example, two points close to `1e8` can have squared distance 5 in float64 by
subtracting coordinates first, while a norm/inner-product identity subtracts
large nearly equal numbers. A speedup using the second identity must survive this
case or state an input-domain restriction. Replacing negative distances by zero
is not a general numerical proof.

## Make the benchmark comparable

Use the performance skill's measurement machinery rather than creating a second
benchmark framework. Numerical-specific metadata includes shape/distribution,
strides, dtype, backend, native thread count, optional compilation signatures,
device and synchronization policy. Include allocation, conversion and validation
according to the real caller. Separate one-time setup from repeated computation,
then report an end-to-end total with the actual reuse count.

Each repetition needs logically equivalent inputs. In-place kernels can otherwise
benchmark progressively transformed data. Reinitialize outside the measured
kernel only if production likewise supplies fresh input without paying that cost;
report both views where helpful. Consume/check results outside kernel timing but
ensure required device work has actually completed inside the intended interval.
Use repeated samples and compare their distribution, not one lucky minimum.

A performance regression test should not assert that a tiny synthetic example is
always faster on every host. Assert deterministic output/ownership/budget
invariants; maintain performance measurements separately with uncertainty and
representative hardware. Memory-plan arithmetic is not a measured RSS peak.
Likewise a compiler import test does not execute the optimized kernel, and CPU
tests do not establish CUDA correctness.

## Acceptance record

For each retained change, record:

- Problem and data contract, including where data validation happens.
- Baseline and candidate algorithms, versions and input fixture/seed.
- Numerical result: maximum/typical relevant error, residual or domain metric,
  non-finite results, convergence/failure counts and tested edge cases.
- Resource result: repeated cold/warm timing as applicable, actual memory method,
  and explicit statements of omitted setup or transfer costs.
- Decision: keep/reject, reason, unsupported regimes and missing execution.

The bundled blocked-distance asset has CPU NumPy tests for shape/dtype, negative
strides/read-only arrays, aliasing, budget rejection, non-finite inputs, arithmetic
overflow and large-offset close points. Those tests do not validate SciPy solver,
Numba, NumExpr, JAX, PyTorch or CuPy examples. Missing dependencies should yield
an explicit skip with a reason, never an automatic download or a fabricated pass.
