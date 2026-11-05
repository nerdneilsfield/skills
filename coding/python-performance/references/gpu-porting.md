# GPU porting from the least invasive option

A port is a hypothesis about speed that must also keep the numerical contract. It is
kept only if it is correct and faster on representative data, end to end.

## Before touching code

Record a representative input, the expected output, the numerical tolerance, and an
end-to-end CPU baseline including input, transfers, compute and output. Record hardware,
library versions, dtypes, shapes, batch size and warm-up policy with every result.
Profile first: the limit may be memory bandwidth, allocation or storage, and a GPU fixes
none of these.

A port is promising when the hot path has much independent work, runs often enough to
repay initialization and transfer, and fits device memory with room for temporaries.
Do not use a row-count threshold as proof; measure the actual shapes. Stay on the CPU
when the work is small, mostly sequential, or needs frequent host-device round trips.

## Order of options

Stop at the first option that meets the target.

1. Already on PyTorch or JAX: stay there. Remove CPU round trips and use the framework's
   batching, compiler and profiler. Do not move to another library for its reputation.
2. Accelerator or backend mode with no rewrite: `cudf.pandas`, `cuml.accel`, `nx-cugraph`.
   Check the logs for silent CPU fallback.
3. A drop-in array library: CuPy for NumPy and SciPy, cuCIM for scikit-image, cuVS for
   vector search. Matching names can still differ in defaults, dtypes and arguments.
4. A maintained framework operation, written natively.
5. A custom kernel, only when profiling shows no suitable library operation.

Library availability moves quickly. Check the installed version; do not assume these
names or their compatibility from memory, and route installation to `python-environments`.

## Keep a verified CPU path

Keep the CPU implementation runnable behind one switch, and keep its tests. It is the
reference for correctness and the fallback on machines without the device. If the
application cannot run without the device, fail early with a clear error rather than
falling back silently. Share one implementation through an array namespace only if that
stays readable; two short verified paths beat one obscure path.

## Verify numerics before speed

Compare CPU and GPU outputs on small fixed fixtures and on representative data, with an
explicit absolute and relative tolerance derived from the contract and the precision.
Assert shape and dtype separately, and test edge cases, NaN and Inf, ordering and ties.

Expect more than roundoff from changed precision, reduction order, random streams and
algorithm. A different random generator is not a bug in itself; compare distributions or
inject the same draws. An approximate index is not an exact search: report recall@k
against exact results. Do not change `float64` to `float32` unless the contract allows
it, and record that change in the deviation record when the code implements a paper.

## Measure the win

Follow the timing rules in `python-numerics` (asynchronous timing and device boundaries).
Report synchronized region time and end-to-end latency, include the transfers production
pays, keep first-call compile time apart, and record peak device memory, separating live
allocations from memory the allocator retains.

Keep the port only if correctness passes and the agreed metric improves. Otherwise say
what limited it: problem size, transfers, fallback, memory pressure or the algorithm.
Without a device, mark the port unexecuted; a CPU-only run validates none of it.
