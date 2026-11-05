# Sources, mirrors and dependency-chain diagnosis

## Do not collapse four different meanings of “source”

A Conda **channel** supplies a coordinated package/build namespace and repodata. A PyPI **index** supplies Python distributions. A **mirror** changes where equivalent content is fetched. A locked artifact **URL/hash** records a selected object. Replacing one does not automatically replace the others. The user's report that “Pixi default sources caused confusion” is a symptom, not enough evidence to identify which layer was wrong.

Start with the failing command, installed manager version, selected workspace/environment/platform, error category, and redacted source names. Ask for relevant config keys only; no raw `env`, auth files, proxy passwords or private index URLs with tokens. Preserve originals locally. Do not diagnose “slow mirror” from a solver conflict or “bad package” from TLS failure.

## Pixi-specific facts and version gates

Current documented `default-channels` is fallback for workspace-independent operations; existing workspace operations use manifest channels. `pixi exec` can use the fallback even from a project directory. Thus changing defaults need not change a workspace. Mirrors are expected to preserve content; original fallback must be listed explicitly, and repodata must be trusted. PyPI index and artifact hosts can differ, so one rewrite may not cover both. These are current-version behaviors, not assumptions for older Pixi. [Configuration](https://pixi.prefix.dev/latest/reference/pixi_configuration/)

A per-package channel constraint and channel ordering also affect selection. Examine workspace, feature and package source declarations together rather than assuming one visible channel list is the whole policy. [Channel logic](https://pixi.prefix.dev/latest/advanced/channel_logic/)

## Worked diagnosis: changed default, old source still appears

1. **Classify the command.** Was it `pixi install/run` against an existing manifest, or `exec`/global/new-project activity? Record the actual manifest path; a parent workspace may have been discovered.
2. **Inspect relevant declarations.** Read only the explicit project manifest and project config, then ask for selected redacted user/global keys if still needed. Identify channel lists, per-package channels, PyPI indexes and mirror mappings separately.
3. **Read the locked selection.** A lock can still identify an original channel while an approved mirror transports its bytes. URL spelling alone does not prove the mirror was ignored. Conversely, replacing a channel in intent does not mean an existing lock already contains a new solution.
4. **Discriminate config effects safely.** If the installed command supports it, use a copied scratch manifest/lock and a narrow controlled config for a comparison. Do not run a mutating install just to inspect precedence. Never conclude `--no-config` means no project config.
5. **Repair the smallest layer.** For equivalent download acceleration, prefer a trusted mirror mapping; for deliberately different distributions, change explicit project source intent and review a new lock. Preserve a rollback. Do not add several public indexes as fallbacks for private names.
6. **Validate both provenance and speed.** In an authorized supply-stage test, compare same artifact/hash, target and cold/warm cache condition; record resolve time separately from transfer/build time. A speed claim from different packages or warmed caches is invalid.

Mirror trust, artifact completeness, lag and platform coverage matter more than brand. Keep TLS verification; fix approved CA configuration instead of disabling verification. A stale mirror can expose metadata for an absent archive. Retry a known approved equivalent source only after identifying that failure; do not silently broaden trust. No runtime skill requires a mirror to be reachable.

## Read a dependency chain, not just the top-level error

Three graphs answer different questions:

- **Intent graph:** direct requirements, extras/features, Python/platform constraints and build requirements.
- **Resolved graph:** selected versions/builds/artifacts in a target lock.
- **Installed graph:** metadata actually present in a prefix. This can drift from the lock and still omit native shared-library edges.

For a uv project with an existing lock, inspect local help, then use a bounded package-focused view where supported:

```sh
uv tree --locked --offline --package numpy --invert --depth 4
```

This asks which selected packages depend on NumPy. It is not an import test, and tool internals may use caches; do not call it a completely side-effect-free filesystem audit. If the lock is absent/stale, stop and report rather than dropping `--locked` to trigger a solve. For a trusted existing pip-style prefix, `uv pip tree --help` identifies its separate installed-graph interface; do not confuse it with project `uv tree`. [uv CLI](https://docs.astral.sh/uv/reference/cli/)

Pixi's current tree supports environment/platform, inversion and locked/no-install options. A controlled inspection can use:

```sh
PIXI_OFFLINE=true pixi tree --manifest-path /project/pixi.toml -e analysis --platform linux-64 --locked --no-install --invert '^numpy$'
```

Replace selectors with declared values; verify installed help and offline support. `--no-install` alone can still permit lock changes, hence pair with locked semantics and preserve the lock. Repeated nodes marked `(*)` are abbreviated subtrees, not missing dependencies. [Pixi tree](https://pixi.prefix.dev/latest/reference/cli/pixi/tree/)

## Turn conflict evidence into a repair

Example: package A requires NumPy below version X while selected package B requires X or newer. A top-level pin cannot satisfy both. Locate the direct parent(s), check whether an unnecessary extra brought one in, then choose a supported A/B pair or separate incompatible workloads. Do not simply remove all bounds. If the conflict concerns Python or a platform-specific wheel, changing NumPy may be irrelevant.

For native scientific stacks, include build variants: CPU/GPU torch, BLAS provider, CUDA runtime, compiler runtime and libc constraints. PyPI package metadata is not a complete native dependency graph, and Conda/PyPI names need not match one-to-one. Build dependencies form a separate graph from runtime dependencies; an isolated build failing for a missing backend is not fixed by proving the runtime package exists elsewhere.

Record the smallest contradictory path, why the chosen repair breaks it, the lock diff and the runtime regression check. Prevent recurrence by documenting source intent and environment selectors alongside commands, not in an individual's global config. Do not promise a specific cause for a user's environment until its relevant evidence is available.
