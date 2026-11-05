---
name: python-environments
description: "Use when creating, reproducing, or diagnosing a Python environment with uv, venv, Conda, or Pixi, including locks, mirrors, offline artifacts, native ABI, and CUDA package compatibility. Defer shared contracts to python. Not for CUDA kernel authoring, numerical algorithms (python-numerics), profiling code that already runs (python-performance), or model quality (python-ml)."
---

# Reproducible Python environments

Make the intended workload run in an identifiable environment, without replacing a working workflow merely to standardize tools. Run this skill for interpreter, uv, venv, Conda, Pixi, lock, mirror, offline-artifact, native ABI, or CUDA package failures. This skill owns that packaging policy. C++ vendoring restrictions do not prohibit Python package managers. CUDA kernel authoring is outside this skill.

## Select only the relevant reference

| Situation | Read |
| --- | --- |
| Unsure which environment runs, migrating or recovering | [Ownership and recovery](references/ownership-and-recovery.md) |
| uv project, pip interface, or existing venv | [uv and venv workflows](references/uv-and-venv.md) |
| Conda/Pixi channels, solver, platforms or mixed packages | [Conda and Pixi](references/conda-and-pixi.md) |
| Import/link failure, CPU wheel instead of GPU, extension build | [Native and CUDA compatibility](references/native-and-cuda.md) |
| Slow/wrong source, mirror/default confusion, dependency conflicts | [Sources and dependency chains](references/sources-and-dependencies.md) |
| Offline restoration, CI, SSH or notebook disagreement | [Offline and remote](references/offline-and-remote.md) |

References explain procedures locally; web links are provenance, not required reading. Do not load every reference for a routine interpreter mismatch.

## Contract before changing state

1. Identify the requested workload, project root, supported OS/architecture/Python, existing manager and environment path. Keep existing constraints unless migration is requested.
2. Separate **dependency intent**, **resolved lock**, **materialized prefix**, and **machine capability**. None substitutes for the other three.
3. Start with read-only evidence. From a trusted local interpreter, run `python -I -B /absolute/path/to/scripts/environment_snapshot.py --help`; the helper reports current interpreter/ABI, not package usability. It neither installs dependencies nor executes project code. Explicit metadata input is optional (at most 16 ordinary UTF-8 files, 1 MiB each; only bounded Name/Version fields). Paths require `--include-paths`. Metadata need not belong to the active prefix; the venv flag does not identify Conda/Pixi ownership, and CUDA is not detected.
4. Choose one owner for dependency changes. uv, Conda and Pixi need not all be present. A package manager invocation can modify an environment, download software, run build hooks or activation scripts; it is not automatically a diagnostic.
5. Explain the smallest repair, destination prefix, required artifacts and validation before performing authorized changes. Do not delete the only working environment or modify system Python, drivers, shell startup files or global configuration.
6. Validate interpreter identity, intended dependencies, then an explicitly selected minimal workload. Imports can execute code and load native libraries; metadata inspection alone is not a runtime health check.

After the environment runs the intended workload, stop. Defer numerical correctness to `python-numerics`, process profiling to `python-performance`, model quality to `python-ml`, and tabular analysis to `python-data-analysis`. Defer shared data contracts to `python`. If a needed named specialist is absent, tell the user that exact skill name to install; do not globally search, fetch a substitute or auto-install it. This environment workflow remains independently usable.

## Completion evidence

Use [environment record](assets/environment-record.md) to record exact commands, manager/interpreter identity, lock and target, observed result, rollback and unverified boundaries. A successful solver does not prove imports; a successful import does not prove GPU execution; a warm environment does not prove offline restoration. Missing tools/artifacts are actionable gaps, not permission to install them implicitly.
