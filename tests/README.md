# Offline support-tool tests

Prerequisite: already installed Python 3.9+ standard library. From the repository root:

```sh
python3 -m unittest discover -s tests -v
```

On Windows use `py -3` or an explicit Python 3 executable; no assumption is made about the `python` alias. No packages, network, external profilers or C++ libraries are required. Tests use temporary directories, local fixtures and subprocesses only to invoke these authored Python scripts with `--help`/invalid-input arguments. A symlink regression is skipped only when the OS explicitly cannot create symlinks; other failures are not hidden.

The suite covers sample distributions, direction/units, correctness failures, metadata type/mismatch/explicit deliberate variable, zero baseline and overflow, bounded JSON reads, vendor path confinement/empty license records, and allowlisted snapshot fields. Passing these tests is not statistical validation of benchmarks, legal license validation, offline CMake proof or execution of the debugger/numeric documentation examples.

The original self-authored C++ fixture lives at `coding/cpp-project-init/assets/minimal-project/`. Its README and the init references document separate CMake and compiler-only smoke commands. Those require locally installed tools; do not silently download prerequisites.

`test_proc_sampler.py` additionally validates read-only Linux proc sampling using original temporary files: PID/TID reuse, counter decreases, thread truncation, ancestor CPU quotas, permission/disappearance handling, parsing and output bounds. These tests do not require Linux proc access; an actual runtime smoke requires Linux and an owned/authorized PID. See the performance skill's proc-sampler guide for limits and attribution rules.

`test_remediation_examples.py` compiles the original C++20 remediation fixture in Debug and Release using an already installed Unix-style `c++`, then checks output. It uses temporary binaries and explicit checks active under NDEBUG. Without the suitable compiler/platform it skips with an explicit reason; no toolchain is installed. These are correctness examples, not performance benchmarks.
