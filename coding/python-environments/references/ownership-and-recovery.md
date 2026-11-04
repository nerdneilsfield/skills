# Ownership, identity and safe recovery

## Start with the four-layer model

A point-cloud registration experiment may have a `pyproject.toml`, an `uv.lock`, a `.venv`, and a Linux GPU machine. The manifest expresses allowable dependencies; the lock chooses artifacts within those constraints; the prefix contains actual files; the machine supplies the CPU, kernel, driver and other external capabilities. Editing one layer does not repair the others automatically.

Suppose a notebook imports an older SciPy even though the lock changed. First ask which interpreter the notebook kernel runs. Re-resolving dependencies cannot fix a kernel still attached to a different prefix. Conversely, the right interpreter path does not prove that its native extension matches the system ABI.

## Identify without executing the project

Inspect only the supplied project root and explicitly identified manifests: `pyproject.toml`, `uv.lock`, `pixi.toml`, `pixi.lock`, `environment.yml`, pinned requirements, `.python-version`, and relevant CI commands. A `pyproject.toml` alone does not prove uv owns the environment. Several lock files may represent different subprojects or migration history; inspect callers before choosing. Do not recursively search the home directory or print credential-bearing manager configuration.

The bundled snapshot is intended to run with the trusted interpreter under investigation, not whichever `python` happens to be first on PATH. `-I -B` avoids bytecode writes and current-directory and user-site import injection; it deliberately does not reproduce all normal startup settings. It is an identity probe, not the final application test. Even Python startup may run trusted environment site customization: do not execute an untrusted interpreter/prefix merely because its path is known.

Record executable, implementation/version, architecture, prefix and ABI. An explicit METADATA file can tell you a package's recorded name/version without importing it. Do not infer loadability, provenance or complete dependency consistency from that file. Avoid dumping `direct_url.json`, index credentials, shell environment, process arguments, notebook contents or private paths into shared reports.

## Choose the owner

- Existing managed scientific project: preserve its manager and version policy.
- Mostly PyPI wheels with Python project metadata: uv is a reasonable new-project choice.
- Existing Conda distribution or institutional scientific environment: keep Conda unless migration solves an identified problem.
- Python plus non-Python libraries, compilers or R with a unified project workflow: consider Pixi.
- A small existing venv with pinned requirements remains valid. Tool novelty is not a migration requirement.

CPU/GPU needs alone do not choose the manager. Prebuilt PyTorch wheels can work with uv; a compiler/native-library stack may benefit from Conda/Pixi. Containers can fix a user-space stack but do not supply a working host GPU driver automatically.

## Repair with a reversible experiment

Classify the failure before changing anything:

| Evidence | Likely layer | First discriminating check |
| --- | --- | --- |
| Package found in terminal, missing in notebook | Identity | Compare `sys.executable` in both processes |
| Solver cannot choose versions | Intent/resolution | Check Python/platform/extras/channel constraints |
| Lock resolves but install fails offline | Artifacts | Identify the exact absent wheel/archive/interpreter/build input |
| Import says undefined symbol or missing DLL | Native ABI | Inspect package source/build and platform compatibility |
| torch imports but CUDA unavailable | GPU capability/build | Follow native/CUDA reference, not a wholesale reinstall |

Preserve old manifest/lock and prefix. Create a separate candidate prefix through the chosen manager when changes are authorized. Reproduce the smallest failing operation with known input; compare output tolerances as well as exit status. Switch the actual entrypoint/kernel/CI configuration only after the candidate passes. If it fails, restore the previous selection; do not repeatedly overwrite the old prefix while guessing.

A migration must account for direct dependencies, transitive constraints, local/editable packages, build requirements, indexes/channels and scientific compatibility anchors. Import scanning is only a clue: optional paths, plugins and dynamic imports are invisible. Do not delete historical manifests until all consumers are understood. An environment export may include private URLs or absolute paths; inspect/redact it before sharing.

## Acceptance

Report which process now runs which prefix, what changed, the minimal application result, unresolved platform/toolchain constraints, and rollback. Retain scientific baselines: new BLAS builds, precision defaults or framework versions may change results/performance even if all imports succeed.
