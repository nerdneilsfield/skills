# Arrays and memory: remove work before adding hardware

## Start with representation, not syntax

A Python loop over scalar objects repeatedly pays dispatch and object handling.
A NumPy ufunc moves iteration into native code, but this alone says nothing about
SIMD, multiple cores, or the number of memory passes. `np.vectorize` wraps repeated
Python calls for convenience; replacing a loop with it is not a performance fix.
`dtype=object` is also not a packed numeric buffer. Establish intended numeric
semantics before converting it; silently converting missing strings or arbitrary
precision integers can change results.

Record `a.shape`, `a.dtype`, `a.strides`, `a.flags.c_contiguous`,
`a.flags.f_contiguous`, `a.flags.writeable` and `a.nbytes` for relevant operands.
Strides say how far the next element along each axis lies in memory. Negative
strides and non-contiguous views can be valid inputs; a transpose need not copy.
Basic slices share storage; advanced indexing usually allocates when retrieving
values. `reshape` may need a copy, while `flatten` always allocates. Trace the
actual expression rather than infer allocation from the variable name.

`nbytes` is logical element storage, not unique retained memory or RSS. A tiny
view can keep a large base allocation alive, and multiple views can count the
same bytes repeatedly. A broadcast view can describe many logical elements using
few stored values. `.base` alone cannot establish whether two arbitrary arrays
overlap. For small relevant inputs use `np.shares_memory`; exact overlap analysis
can be expensive for pathological strides, so avoid unbounded forensic searches.

## Make copies pay for themselves

Suppose a strided view enters the same solver many times. An explicit contiguous
copy once may outperform repeated hidden conversions. Compare the entire path:
conversion + repeated kernels versus strided kernels. Keep the layout required
by the actual API; C order is not universally better than F order. For one tiny
operation, conversion overhead may dominate. Retain the copy only if its cost,
extra memory and ownership semantics are acceptable.

For `a * scale + bias`, separate eager operations commonly create intermediates.
A reusable destination can remove an allocation, but it is not automatic fusion:

```python
# Preconditions: x, scale, bias are compatible numeric inputs; out has correct
# shape/dtype and does not overlap any operand needed after the first step.
np.multiply(x, scale, out=out)
np.add(out, bias, out=out)
```

There are still two array passes. If `bias` is a view into `out`, the first step
may overwrite values the second step needs. A single ufunc's overlap handling
does not make a sequence of operations alias-safe. Prefer an owned temporary
when that invariant is difficult to establish. Keep input mutation explicit in
API contracts and tests. Shared read-only arrays are easier to parallelize than
shared mutable views.

## Worked example: broadcasting produces a huge result

For queries `X` with shape `(N,D)` and targets `Y` with shape `(M,D)`,
`X[:,None,:] - Y[None,:,:]` materializes `(N,M,D)`. Broadcasting the inputs is
cheap; materializing differences is not. Squaring the differences without `out=`
may create another array of that size; a reduction adds `(N,M)`. With element
size `s`, account for input storage, simultaneous temporaries and the required
output separately. Do not present one formula as a universal allocator peak:
expression lifetime and the chosen implementation affect overlap.

If callers need only one minimum per query, retaining the full pairwise matrix
is unnecessary. The bundled `assets/blocked_distances.py` keeps one query and a
block of `B` targets active:

- Difference work buffer: `B*D*s`; squaring happens in place.
- Sum buffer: `B*s`; accumulate a scalar minimum over target blocks.
- Final output: `N*s`.
- Explicit arithmetic allocations: `N*s + B*(D+1)*s`.

The budget determines `B`; a budget too small for one target row is rejected
before these arrays are allocated. Inputs, Python/NumPy runtime, allocator
metadata and internal iterator buffers are **not** included: this is a planning
bound, not enforcement of physical memory. Input validation uses scalar iteration
instead of another input-sized boolean array; that conservative choice can be a
large part of latency. A production pipeline may validate once at a trusted
boundary, but it must preserve the finite-input guarantee and report that change.

The example preserves input precision, checks float32/float64 agreement and
supports negative strides/read-only inputs without an eager layout copy. It
returns squared distance, not distance or nearest index. It does not define tie
indices because it does not return any. Empty queries return empty output; empty
targets and zero feature count are rejected. Overflow raises rather than silently
allowing an invalid minimum. The algorithm is still O(N*M*D): chunking fixes
working memory, not computational complexity.

A tree/index may reduce work for suitable dimensions and repeated queries;
include build costs, exact/approximate semantics and distribution. Do not silently
replace direct differences with `||x||² + ||y||² - 2*x@y`: close points at large
coordinates can suffer severe cancellation. Clipping negatives to zero hides
that error rather than proving equivalence.

## Diagnose → fix → verify → prevent

- Memory jumps: derive intermediate shapes, then block/fuse/reduce early; verify
  output parity and explicit peak plan, then measure real process peak separately.
- Low utilization with large arrays: investigate bandwidth, access pattern and
  passes before adding threads. CPU utilization alone cannot prove bandwidth.
- Repeated conversion: move conversion to a justified boundary; benchmark its
  amortization and test aliasing/lifetime after the move.
- Permanent prevention: retain non-contiguous, read-only, shared-input, extreme
  magnitude and budget-too-small regression cases. Keep small known-good reference
  calculations even when production uses a more complicated blocked algorithm.
