# Training and inference performance: follow the batch, not GPU utilization

## A comparable measurement

Trace a representative batch through **storage → decode/augment → collation → host/device transfer → forward → loss/backward → optimizer → metrics/output**. Define whether the requirement is cold-start latency, single-request latency, steady-state throughput, tail latency, peak memory or time to a quality target. Faster steps with slower convergence may lose the actual objective.

Warm-up excludes import, allocation and compilation transients only when measuring steady state; report those transients separately. Accelerators are asynchronous. A host stopwatch around a launch measures enqueue time unless completion is awaited. For an end-to-end CUDA measurement, synchronize before starting and after the bounded workload on the relevant device, then divide real processed samples by elapsed time. CUDA events measure device-stream intervals, not storage or CPU preprocessing. Synchronizing every operation changes overlap and is not the production throughput measurement. For JAX, complete the result with `block_until_ready()` and account separately for compilation and host/device transfers.

Collect repeated unprofiled measurements with fixed workload/quality settings. For inference, declare batch and concurrency, include preprocessing and output transfer if the caller needs them, and measure queueing/tails under representative load. A batched throughput improvement is not automatically a single-request latency improvement.

### Concrete completed-work timer (adapt inside a trusted application)

This function times an already constructed trusted callable. It does not load a project or accept a shell command. The caller controls the input/device contract and chooses a finite repeat count. Keep profiler instrumentation disabled for the acceptance run.

```python
import time
import torch

def completed_cuda_seconds(step, device, repeats=20):
    if not isinstance(repeats, int) or isinstance(repeats, bool) or not 1 <= repeats <= 1000:
        raise ValueError("repeats must be 1..1000")
    device = torch.device(device)
    if device.type != "cuda":
        raise ValueError("this timing recipe is CUDA-specific")
    torch.cuda.synchronize(device)
    start = time.perf_counter()
    for _ in range(repeats):
        step()  # Include the stages whose end-to-end cost is the requirement.
    torch.cuda.synchronize(device)
    return (time.perf_counter() - start) / repeats
```

Perform a separately reported warm-up before steady-state use. Training steps mutate weights, so reproduce the same initial state/order for comparable runs rather than timing a later training phase against an earlier one. Inference requires declared `eval` and graph modes. This snippet is source-reviewed, not executed by the CPU fixture; it requires a compatible actual CUDA runtime/device. For multiple devices, synchronization must cover all devices participating in the measured operation, not merely the default one.

## Capture the smallest useful trace

Use `torch.profiler` with CPU and available device activities, a bounded wait/warm-up/active schedule, and `prof.step()` once per logical step. Name stages with `record_function`. First inspect coarse timing; add shapes, stacks or memory attribution only when needed because tracing changes overhead and may retain tensors. Save traces only to an intentional local path and review them for paths, shapes and sensitive metadata before sharing. Confirm the proposed improvement with profiling disabled.

A GPU timeline gap is a hypothesis, not proof of “Python is slow.” Correlate it with data wait, host work, transfers, synchronizing logging and collectives. Generic process CPU/native waits, page faults and thread oversubscription belong to `python-performance`; array copies and operation-level dtype/layout/JIT belong to `python-numerics`.

## Symptom → evidence → remedy → verification

| Symptom | Discriminating evidence | Minimal remedy and tradeoff | Verification/prevention |
| --- | --- | --- | --- |
| Accelerator idle before each batch | Loader-only time versus compute on already-resident batches; CPU/storage trace | Cache/decode efficiently, batch reads, reduce costly transforms; cache validity and RAM are costs | Re-run full pipeline, not only synthetic-resident compute |
| More workers make it slower | Sweep 0, 1, 2, 4 within core/RAM budget; inspect process count, native threads, I/O | Reduce workers; bound native threads; avoid nested parallel layers | Include startup, epoch boundaries and steady state; no “workers = cores” rule |
| Host memory grows with workers | Parent Python object footprint, queue/prefetch size, resident memory | Compact metadata, avoid replicated huge Python lists, reduce prefetch/workers | Check memory after several iterations, not just constructor |
| Slow transfer | Transfer intervals, source layout, payload size | Batch transfers; test pinned loader memory with compatible async copy | Pinning consumes host resources; `non_blocking=True` alone does not prove overlap |
| High overhead for small device operations | Trace launch density and CPU gaps | Fuse/batch work or evaluate compilation after correctness | Count compile cost, graph breaks, shape specialization and recompilation |
| OOM during forward/backward | Peak allocated/reserved memory and tensor lifetimes | Smaller microbatch, bounded shapes, precision with quality gate, activation checkpointing | Checkpointing recomputes; verify gradients/RNG-sensitive behavior and time-to-quality |
| Memory climbs each step | Live graph retention, accumulated logits/loss tensors | Store detached summaries, bounded outputs; remove unintended `retain_graph=True` | Detached GPU tensors still occupy GPU memory; move only needed bounded results |
| Slow distributed steps | Per-rank data times, collective overlap, imbalance | Equalize valid work or tune the proven bottleneck | Global quality/sample accounting and multi-rank tests, not rank-zero timing alone |

Loader workers often launch native numerical/augmentation threads too. Budget total runnable threads/processes and RAM across ranks, workers and libraries; a node with eight devices can multiply a seemingly modest per-rank worker setting. Persistent workers reduce restart overhead but retain dataset state; changing an epoch field in the parent may not update worker copies. Seed/data-epoch propagation needs an explicit mechanism. Spawn-based platforms require import-safe entrypoints and serializable worker definitions; begin with zero workers to obtain useful error traces.

Pinned host buffers must remain valid and unmodified until asynchronous use completes. Device-to-host results must be ready before CPU code consumes them. Overlap additionally depends on streams, hardware and actual operation schedule; never infer it solely from a flag. Use local framework guidance when adding custom stream coordination rather than guessing buffer lifetime.

`empty_cache()` does not free live tensor storage and is not a per-step leak fix. Distinguish live allocated memory from allocator reservation and other processes; examine peak demand and lifetime before tuning allocator knobs. Reserved memory exceeding allocated memory alone does not prove harmful fragmentation. Do not respond to an OOM by repeatedly retrying the same unbounded workload.

## Optimization acceptance

Preserve data IDs, transforms, sample weighting, metric reduction and optimizer-step semantics. Report absolute timing, variation, processed samples, peak host/device memory and quality. Compare both ordinary and difficult shapes. A proposed AMP/compiler/export/PTQ/QAT path must be tested on representative held-out data, hardware and runtime; calibration data selection is part of that contract and must not consume the final test labels. This skill does not provide low-level CUDA kernel engineering or claim every quantization backend supports the same operators.
