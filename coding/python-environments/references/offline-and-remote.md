# Offline restoration, environment switching and remote execution

## Offline knowledge is not offline artifact availability

All decisions in this skill can be understood without visiting source links. Actually installing packages offline additionally requires the exact target artifacts and tools. A lock contains decisions, not package bytes. A working prefix may depend on caches or system libraries absent from a clean machine.

Separate two authorized stages:

1. **Supply stage:** on an approved connected builder, select supported targets and prepare interpreter, manager, wheels/Conda archives, metadata, build backend/toolchain inputs and local/VCS sources. Record hashes/provenance. Review licenses where redistribution is intended. Do not put credentials into an archive or committed lock.
2. **Recovery stage:** on the target, use the prepared inputs with network acquisition disabled and the manager's lock-consistency mode. Missing data is a failed prerequisite, not permission to turn networking back on.

A wheel cache from macOS arm64 cannot substitute for Linux x86_64 artifacts. Source distributions add compiler/header/backend requirements; editable paths and VCS dependencies need the actual source revision. Cache keys should include lock, platform/architecture, Python ABI, manager/cache format and relevant build configuration. Never assume a CI cache hit means all requested extras are available.

Use a fresh candidate prefix while preserving the working one. Run a minimal representative workload and compare scientific outputs. Record whether network isolation was enforced or merely an offline flag used. If isolation or target hardware was unavailable, label that boundary unverified. Do not advertise a structural manifest check as proof of offline rebuildability.

## Switch the process, not the prompt

The shell prompt is cosmetic. The running process determines interpreter, import paths and inherited loader/thread settings. Conda activation, venv activation, Pixi shells and IDE kernels can be nested accidentally. Opening a fresh shell can remove stacking, but is not a substitute for explicit identity checks.

For a trusted interpreter, this tiny identity command executes no third-party import:

```sh
/explicit/environment/bin/python -I -c "import sys; print(sys.executable); print(sys.prefix); print(sys.base_prefix)"
```

On Windows use the corresponding environment Python path, usually `Scripts/python.exe` for venv. Compare the ordinary application process identity too: isolated mode intentionally hides some site/path behavior. Do not change global PATH to make every command point at one project.

| Execution surface | How mismatch occurs | Correction and validation |
| --- | --- | --- |
| Shell | Nested activation, alias or stale command lookup | Use explicit interpreter; recheck after deliberate shell reset |
| IDE | Interpreter setting differs from terminal | Select target prefix in project settings; execute identity in debugger/test runner |
| Notebook | Kernel stays alive after environment change | Inspect `sys.executable` inside kernel; select registered target kernel and restart |
| Subprocess | Bare `python` resolves a different PATH | Python code should use `sys.executable` for same-environment child; test the child identity |
| Task runner/CI | Different feature/group or manager version | Record explicit selector and pinned tool setup; verify process identity in job |
| SSH | Login shell, modules or scheduler differs from interactive login | Check inside the actual remote job, not on the laptop or login node |

Kernel registration, activation hooks and manager run commands execute code or change state; perform them only when requested and inspect trust first. A venv copy is not a robust deployment artifact: absolute shebangs, native libraries and interpreter layout can break relocation. Restore from declared inputs into a target prefix instead. Conda activation may be required for native loading; bypassing it with a binary path is an identity probe, not a guarantee of equivalent application startup.

## Remote/HPC and containers

Distinguish login node from scheduled compute node, filesystem paths from mounted paths, and host driver from container user-space runtime. Supply artifacts for the execution node's actual architecture and ABI. A shared cache on network storage can be slower or unavailable; changing cache policy requires project/operator agreement, not a global cleanup. Never delete a shared cache to troubleshoot one project.

For a remote problem, request only relevant redacted version/error/config fields. Do not copy the entire home directory, shell history, SSH config or environment. Avoid changing remote startup scripts as a convenience. Document any required activation/module invocation in the workload entrypoint and verify it in a fresh job.

## Failure-to-action checklist

- Missing interpreter: report exact needed implementation/version/target; no hidden download.
- Missing archive or wheel: identify artifact and approved supply stage; no online fallback.
- Hash mismatch: stop, preserve evidence, verify trusted origin; never suppress checking.
- Solver fails offline: distinguish absent metadata/artifacts from inconsistent constraints.
- Installs but cannot import: native/ABI reference, not repeated resolution.
- Import works but workload fails: application/device/precision validation, not an “environment passed” blanket claim.

Sources: [uv cache](https://docs.astral.sh/uv/concepts/cache/), [Pixi install](https://pixi.prefix.dev/latest/reference/cli/pixi/install/), [Conda environment activation](https://docs.conda.io/projects/conda/en/stable/user-guide/tasks/manage-environments.html). Check local command help when exact flags differ.
