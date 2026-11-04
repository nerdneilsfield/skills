# uv and existing venv workflows

## Choose the interface deliberately

A uv **project** uses project intent and `uv.lock`; `uv add` changes dependencies and `uv sync` materializes them. The **pip interface** works against an environment without making it a uv project. A standalone script with PEP 723 metadata is a third workflow. Do not convert between them just to run a profiler. Preserve a working venv/requirements workflow when the task is only diagnosis.

Before mutation, inspect the installed `uv --version` and relevant `--help` from the known tool path. This does not authorize bootstrapping uv. Tool absence is a prerequisite gap. Avoid `uvx` or `uv run --with ...` as hidden tool installers; they may resolve/download packages outside the committed project intent.

## Project identity and lock contract

Record Python implementation, supported version range, target platform/architecture, selected dependency groups/extras and manager version. `.python-version` selects an interpreter but is not a portable installed interpreter. A range such as `>=3.11` is not an exact reproduction record. uv can download managed Python; use already supplied interpreters for offline recovery and report missing ones instead of silently fetching.

Commands below are examples for an authorized project environment operation, not read-only inspection:

```sh
uv sync --locked --offline
```

`--locked` requires the lock to agree with project intent. `--frozen` instead uses the lock without checking that agreement; it is not a stronger consistency check. Plain `uv run` may synchronize before running, so a diagnostic executed through it can change the environment. To examine an existing prefix without syncing, use its explicit trusted Python executable. To execute application code, choose that operation separately.

Synchronizing may remove packages outside the selected dependency set. Do not synchronize a shared or unidentified prefix. Make dev/test groups and optional CPU/GPU extras explicit in the command record, because two valid sync invocations can produce different environments. Commit application lock files under the team's existing policy; do not turn a reusable library's supported dependency range into one universal downstream pin.

## CPU/GPU package sources

An accelerator-specific index is not a replacement source for unrelated packages. The illustrative fragment below shows the mapping, not a universal torch version/CUDA choice:

```toml
[[tool.uv.index]]
name = "pytorch-cuda"
url = "https://download.pytorch.org/whl/cu124"
explicit = true

[tool.uv.sources]
torch = [{ index = "pytorch-cuda", marker = "sys_platform == 'linux'" }]
```

Select a release-supported index and compatible Python/platform before using this. Pin or constrain torch and related torchvision/torchaudio consistently with the project's actual requirements; do not assume the example index has every version. Declare corresponding sources for those packages when needed. Restrict unsupported platform combinations rather than pretending macOS has CUDA wheels. Keep mutually exclusive CPU/GPU configurations explicit; inspect installed uv support before using conflict-group features.

Automatic backend detection is useful for an interactive installation but derives intent from the current host. It does not define a portable CPU/GPU deployment contract. Version-specific/preview flags must be checked locally; project sync and pip-interface options are not interchangeable.

## Existing venv and requirements

Use the environment's explicit interpreter for pip commands (`/path/to/venv/bin/python -m pip ...`, Windows equivalent `Scripts/python.exe`). Do not assume a bare `pip` matches the selected Python, and do not install into system Python or bypass an externally managed environment marker.

A pinned requirement list may still omit hashes, indexes, environment markers, build dependencies and platform differences. For an authorized offline wheelhouse workflow, a typical materialization command is:

```sh
/path/to/venv/bin/python -m pip install --no-index --find-links=/approved/wheelhouse --require-hashes -r requirements.lock.txt
```

This requires an existing hash-complete requirements file and all compatible transitive artifacts. It is not a recipe for inventing a lock from an arbitrary `pip freeze`. Builds from source may need backend packages, compilers and system headers; a wheelhouse made on another architecture may be unusable. Never solve this by disabling hashes or adding an online fallback without agreement.

## Prevention and validation

Keep manager/prefix ownership explicit in developer and CI commands. Validate a clean candidate rather than a dirty shell with nested activation. Check application identity and a minimal scientific operation after a change. Cache presence is only a clue: interrupted/incomplete cache entries and missing target artifacts can still block offline restoration.

Sources checked 2026-10-29: [uv sync semantics](https://docs.astral.sh/uv/concepts/projects/sync/), [Python versions](https://docs.astral.sh/uv/concepts/python-versions/), [PyTorch integration](https://docs.astral.sh/uv/guides/integration/pytorch/), [indexes](https://docs.astral.sh/uv/concepts/indexes/), [cache](https://docs.astral.sh/uv/concepts/cache/). Installed-version help takes precedence over assumed feature availability.
