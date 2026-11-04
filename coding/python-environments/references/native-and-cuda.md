# Native and CUDA compatibility: separate four layers

Use this when a package resolves yet cannot import, link, compile or run on the intended device. Do not treat every such failure as a dependency solver bug. Preserve the exact error and relevant version/build identities, without dumping full process environment or credentials.

## Layer 1: host capabilities

The OS, CPU architecture/instruction support, kernel, GPU model and installed driver constrain execution. A container or environment can supply user-space libraries, not automatically a compatible host driver or device access. NVIDIA compatibility models have supported platform/GPU/version boundaries; neither minor compatibility nor forward-compatibility packages are universal escape hatches.

A targeted `nvidia-smi` invocation, if installed and authorized, helps observe driver/device visibility. Its CUDA version display describes driver support, not proof that nvcc or a toolkit of that version is installed. Driver changes require a separate administrative operation; do not perform one as an environment repair.

## Layer 2: framework runtime build

A Python package can be a CPU build or an accelerator build. Precompiled torch packages may provide runtime dependencies without a CUDA compiler. Record the actual framework version and build/source, not just the requested name. A plain successful `import torch` tests loading, not device execution.

A missing GPU can mean a CPU-only wheel, incompatible runtime/driver, inaccessible device in the container, unsupported GPU architecture, or deliberate device visibility restrictions. Investigate these separately. Do not reinstall the entire stack before distinguishing them.

## Layer 3: extension toolchain

Compiling a C++/CUDA extension requires compatible compiler, headers and libraries. Installing torch alone does not include that toolchain. `nvcc --version` observes the compiler selected by PATH; it says nothing about which toolkit another build system selected. Record resolved compiler/toolkit paths and the build's actual configuration. A build-isolation environment may lack a required backend or framework package even though the application environment contains it.

Inspect the project's established build requirements before proposing a repair. Disabling build isolation can mask an undeclared dependency and contaminate builds; use it only as an explained controlled experiment, not a universal fix. Limit build parallelism to available resources; a failed build killed by memory pressure is not necessarily an ABI error.

## Layer 4: ABI and dispatch

Python implementation/version/ABI, machine architecture, libc, C++ runtime, framework ABI and compiled GPU targets all matter. A wheel for the wrong Python ABI cannot be fixed by changing PATH. An undefined symbol often points to mixed binary builds or an incompatible loaded library. Rebuild against the intended stack or restore a coherent compatible set rather than symlinking unrelated libraries or globally modifying loader paths.

| Symptom | Evidence to distinguish | Repair and prevention |
| --- | --- | --- |
| No matching distribution | Python/platform tags and package release support | Choose supported target/artifact; avoid forced incompatible wheel |
| Missing shared library | Package provenance and actual native requirement | Supply compatible declared dependency; avoid global loader hacks |
| Undefined symbol | Framework/native build identity and extension build inputs | Rebuild extension or restore matched packages |
| GPU absent | Build variant, driver/device visibility, target support | Fix the identified layer, not every layer |
| No kernel image / unsupported architecture | GPU capability and package compiled targets | Use supported build or explicitly rebuild for target |
| nvcc missing during build | Whether compilation is actually required | Supply toolkit in authorized build environment; not required for every wheel use |
| Package installed but Jupyter differs | Kernel executable/prefix | Select correct kernel; see remote reference |

## Explicit runtime check, not inventory

Only after trusting the environment and authorizing execution, a small diagnostic can inspect framework state and perform a tiny device operation. This imports native code and initializes a device; it is not performed by the read-only snapshot:

```python
import torch
print("framework", torch.__version__)
print("runtime build", torch.version.cuda)
print("device available", torch.cuda.is_available())
if torch.cuda.is_available():
    x = torch.tensor([1.0, 2.0], device="cuda")
    y = (x * 2).cpu()  # transfer provides completion for this tiny check
    assert y.tolist() == [2.0, 4.0]
```

Do not label a CPU-only branch as a passed GPU test. This check does not validate the user's operators, extension, memory demand or full numerical workload. Record device availability separately and then test the smallest representative application case. CUDA kernel tuning belongs elsewhere.

Sources checked 2026-10-29: [NVIDIA CUDA compatibility](https://docs.nvidia.com/deploy/cuda-compatibility/latest/), [PyTorch extension toolchains](https://docs.pytorch.org/docs/2.15/cpp_extension.html), [uv accelerator packaging](https://docs.astral.sh/uv/guides/integration/pytorch/). Match compatibility tables to the actual deployment rather than assuming current documentation means the newest version is required.
