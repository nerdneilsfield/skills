# CUDA spikes

Prove a kernel is correct against a trusted reference before any build system. Prefer a path that compiles from Python in the shared experiments env. Add one `.cu` plus the repo Makefile only when you must see raw nvcc.

## Preferred order

1. **Triton** — if the kernel is a block-level PyTorch op. Official pattern: write the kernel, compare to a torch reference with `torch.allclose`, then optionally bench. Tutorial: [Triton vector add](https://triton-lang.org/main/getting-started/tutorials/01-vector-add.html).
2. **`torch.utils.cpp_extension.load_inline`** — paste a small CUDA/C++ snippet, compile in-process, call it on tensors. Docs: [torch.utils.cpp_extension](https://docs.pytorch.org/docs/2.15/cpp_extension.html) (`load_inline`). Good when the question is "does this CUDA I intend to ship as a PyTorch op work?" First compile can be slow; iterate on the same process.
3. **CuPy `RawKernel` or `numba.cuda`** — when the work is array-level and not tied to autograd. [CuPy user-defined kernels](https://docs.cupy.dev/en/stable/user_guide/kernel.html), [Numba CUDA](https://numba.readthedocs.io/en/stable/cuda/overview.html).
4. **One `.cu` + nvcc** — only when the question is the standalone CUDA program itself.

## Shared Makefile (experiments repo)

Do not add a CMake project per idea. Reuse a top-level pattern rule:

```make
CXX ?= g++
CXXFLAGS ?= -O2 -std=c++20
NVCC ?= nvcc
NVCCFLAGS ?= -O2 --std=c++17

%: %.cu
	$(NVCC) $(NVCCFLAGS) $< -o $@

# usage: make saxpy && ./saxpy
```

```sh
nvcc -O2 saxpy.cu -o saxpy && ./saxpy
```

## Correctness

Always compare against a CPU or PyTorch reference on a modest size:

```python
torch.cuda.synchronize()
err = (out_kernel - out_ref).abs().max().item()
print("max_abs", err)
assert err < 1e-4
```

Set `CUDA_LAUNCH_BLOCKING=1` when the first launch fails. Time only after a correctness pass, with warmup and `synchronize()`.

## Skip

`cpp-project-init`, CMake presets, standalone CMake CUDA projects, Docker images, Nsight as a first step, autotune sweeps, `torch.compile` as a substitute for the kernel under test.
