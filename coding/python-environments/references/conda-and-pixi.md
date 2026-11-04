# Conda and Pixi: solve the intended environment

## Conda: preserve one package owner

Use an isolated project environment rather than `base`. Confirm `conda --version` and the exact prefix before looking at package records. A named environment can refer to different locations on different machines; record the resolved path locally but redact private paths in shared evidence.

For an authorized local inspection, `conda list -p /explicit/prefix` describes that prefix. Output may include private channel URLs, so keep it local and share only the relevant redacted package/build/channel rows. Do not treat a package name/version alone as a full native compatibility identity.

Traditional mixed workflow: install the Conda-resolved dependencies first, pip-only dependencies last, and avoid `pip --user`. Later Conda changes should generally be tested by recreating from the combined intent rather than repeatedly modifying a prefix whose pip changes may not be tracked. This is not a ban on all mixed environments.

Version gate: current `conda-pypi` support requires **Conda 26.9+**, the **rattler solver**, and **conda-rattler-solver 0.1.1+**. It covers supported **pure-Python wheels from public PyPI**, not arbitrary compiled wheels, private indexes or every Conda-compatible client. Compiled extensions still need an appropriate Conda package in this workflow. Wheels are fetched from PyPI during installation; the channel is not an offline wheel archive. Ordinary pip mutations remain a different workflow.

Check locally without changing configuration:

```sh
conda --version
conda config --show solver
conda list -n base '^conda-rattler-solver$'
```

The package check belongs to the environment hosting the Conda executable, normally base; use its explicit prefix instead if this installation differs. A package record alone does not prove the active solver selection. Share only the relevant redacted version/solver fields. If prerequisites or supported artifacts are missing, report them and keep the established route; do not auto-update Conda, install plugins, change the global solver or append channels.

Channel choice is a native-stack choice, not just download speed. Prefer a coherent source stack and strict priority. Do not assume defaults and conda-forge builds are interchangeable. Test requested migration in a new prefix; do not rewrite global `.condarc`. A portable environment intent file and a platform-specific exact restoration record answer different questions; keep both where reproducibility requires them.

## Pixi: workspace, feature, environment, platform

A workspace declares package intent. Features combine optional sets; an environment selects features; platforms select target artifacts. A lock may contain several such solutions. Being in the workspace directory does not guarantee every Pixi command uses the same environment or source policy. Record `-e` selection, target platform and manifest path, particularly in CI or a monorepo.

Current install semantics:

```sh
# MUTATING: only after an environment restoration is authorized.
pixi install --manifest-path /project/pixi.toml -e analysis --locked --offline
```

Use an environment actually declared in the project, not blindly `analysis`. Check `pixi install --help` for installed-version support. `--locked` rejects stale manifest/lock pairs; `--frozen` uses the existing lock without that check. Offline mode needs cached data. `pixi run`/`shell` can auto-install, and activation/tasks can execute project code, so they are not read-only probes.

## Platform capability version gate

Official latest documentation checked 2026-10-29 marks `[system-requirements]` deprecated and uses rich platform entries:

```toml
[workspace]
name = "registration"
channels = ["conda-forge"]
platforms = [{ platform = "linux-64", cuda = "12" }]
```

This declares a solver assumption, not a toolkit or driver installation. The exact first release supporting this syntax was not established in this research: check the installed manifest schema/help and pinned project version. Keep valid older `[system-requirements]` manifests until a deliberate compatible migration. Do not silently force the latest format into an older deployment.

Virtual-package overrides are suitable for explicitly planned cross-target solving/CI, not a fix for missing hardware at runtime. Setting a CUDA override can make a solver accept a target; it cannot make the workload execute on a machine without the required GPU/driver. Record assumed versus observed capabilities separately.

## Cross-ecosystem dependencies

If a PyPI torch is selected in Pixi, dependencies on that torch should follow the supported PyPI route rather than mixing in Conda packages that expect a Conda torch. Platform support and PyPI solve environments can constrain cross-platform resolution; a macOS machine is not guaranteed to solve a Linux CUDA mixed environment. Use an appropriate authorized target builder when necessary, not fake host capability as proof of success.

For a conflict, obtain the named package, its parent constraints, selected feature/environment/platform and the earliest meaningful solver cause. First test whether removing an unintended feature or correcting Python bounds resolves the logical contradiction. Do not widen all pins or add unrelated channels at once. For source and dependency-graph troubleshooting read [sources and dependency chains](sources-and-dependencies.md).

## Validation and prevention

Retain lock/manifest before changes; compare package source, build variant and platform as well as version in the candidate lock. Materialize into the intended environment, then run the explicitly selected application check. If numerical outputs change, compare BLAS/framework builds before blaming the solver. Document the manager version and environment selector next to the entrypoint so teammates reproduce the same solve.

Sources checked 2026-10-29: [Conda environments](https://docs.conda.io/projects/conda/en/stable/user-guide/tasks/manage-environments.html), [Conda PyPI integration](https://docs.conda.io/projects/conda/en/stable/user-guide/tasks/install-packages-from-pypi.html), [conda-forge transition](https://conda-forge.org/docs/user/transitioning_from_defaults/), [Pixi install](https://pixi.prefix.dev/latest/reference/cli/pixi/install/), [Pixi capability migration](https://pixi.prefix.dev/latest/workspace/system_requirements/), [Pixi PyTorch](https://pixi.prefix.dev/latest/python/pytorch/).
