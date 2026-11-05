# Compilation and device boundaries

## Select a layer because evidence calls for it

Stay in the existing framework when possible. NumPy/SciPy are often sufficient
for a small CPU operation; an accelerator can lose once launch and transfer costs
are counted. A new dependency is justified by a measured hot path and a deployment
path, not by its reputation. No dependency below is required by this skill.

| Evidence | Candidate | Cost or reason to reject |
| --- | --- | --- |
| Python loop around numeric scalars, custom recurrence or branches | Numba CPU JIT | Supported subset, compilation and specialization, deployment requirements |
| Large compound elementwise expression, many temporaries | NumExpr or a fused compiled loop | Supported dtype/operators, thread budget, precision changes, small-array overhead |
| Existing JAX computation repeats compatible shapes | JIT around coherent computation | Compilation/recompilation, tracing semantics, device boundaries |
| Existing PyTorch computation | Framework operations/compiler/batching | Graph breaks, autograd and mutation semantics, backend and precision settings |
| NumPy-like large device-resident computation | CuPy if compatible with deployment | API differences, transfer/initialization cost, GPU memory and optional dependencies |

Do not install these simply to try every row. If an option is unavailable, produce
its bounded experiment and state the missing prerequisite. Keep GPU work here to
library usage, transfer and timing correctness; custom CUDA kernels are out of scope.

## CPU fusion and compilation

A compiled loop can combine operations without materializing intermediate arrays.
Putting `@njit` around an existing sequence of vector expressions may retain the
very memory passes that caused the bottleneck. Conversely, replacing an efficient
BLAS call with hand-written loops can lose. Start from measured Python overhead
or avoidable memory traffic and compare against the original library path.

For Numba, warm each relevant signature before measuring steady-state execution;
record first-call latency separately. Dtype and layout differences can lead to
specializations. Verify the compiled path is supported by the installed version,
not an old blog's object-mode behavior: modern `jit` defaults changed, and explicit
`njit` makes intent clear. `parallel=True` is not proof that a particular loop was
parallelized; inspect diagnostics for the actual function and input regime.
`prange` needs independent iterations or supported reductions. Shared updates
into overlapping indices require redesign, not trust in a decorator.

`fastmath` can permit reassociation and other relaxed floating-point behavior.
Its acceptability follows from the contract, especially for NaN/Inf, signed zero,
thresholds and cancellation. Do not enable it as boilerplate. NumExpr has its own
thread pool and dtype rules; expression rewrites in aggressive optimization may
change precision. For a controlled trial, explicit operand dictionaries and
`optimization='moderate'` make the intended inputs and precision policy clearer.
This still requires output-dtype and error checks; it is not a blanket equivalence
guarantee. Never evaluate arbitrary user-supplied expression text in a generic
example or dump calling-frame locals into diagnostics.

## Make asynchronous timing represent completed work

A CPU clock around a GPU call may measure submission, not completion. Separate:

1. Initialization and compilation (cold path).
2. Input transfer and required preprocessing.
3. Device-resident computation after warm-up.
4. Output transfer/synchronization needed by the caller.
5. Full end-to-end application latency and throughput under intended concurrency.

For JAX, call `.block_until_ready()` on the output when timing a simple array;
for a result tree, wait on all relevant leaves or use the installed API's tree
synchronization helper. Recompilation caused by shape/control-flow
changes belongs to the production result if the workload really varies that way.

For PyTorch on CUDA, synchronized wall-clock timing brackets the measured region
with completion waits on the relevant device. Device events can measure a kernel
region on a stream; they do not automatically measure host preprocessing or work
launched on unrelated streams. Use the framework's benchmark/profiler facility
when available, and state whether training, inference and gradient recording are
included. `inference_mode` or disabling gradients is not valid for a path that
needs gradients. Do not change training semantics in the name of timing.

For CuPy, `cupyx.profiler.benchmark` uses events and synchronization with warm-up.
Know which stream it covers. First context creation and kernel compilation are
real costs even when excluded from steady-state samples. Record the policy rather
than hiding slow first calls. A CPU-only run cannot validate any of these GPU
paths; mark them unexecuted, not passed through simulation.

## Keep data in the right place, without hiding costs

Repeated `.cpu()`, `.numpy()`, `.item()`, printing or NumPy conversions can force
transfers or synchronization. Locate them on the timeline before removing them:
the caller may actually require host results. Batch work and retain intermediates
on the device when ownership and latency permit. A larger batch can improve
throughput but worsen latency and peak memory. Pinned memory and asynchronous
copies are not automatic overlap; stream ordering and host-buffer lifetime must
be correct, and page-locked memory is itself a constrained resource.

GPU allocators may cache memory, so allocated live tensor bytes differ from
reserved pool bytes and driver-visible usage. Model parameters, gradients,
optimizer state, temporary workspace and outputs all matter. Do not treat a
successful small input or a device-kernel-only speedup as evidence that the full
pipeline fits or improves. Revalidate numerical output and device-memory headroom
at representative shapes before recommending the change.
