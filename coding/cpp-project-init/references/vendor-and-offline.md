# Pinned source and honest offline acceptance

Use this when adding/updating a dependency or checking whether a copied template really builds without acquisition. Normal configure/build/test must use source already present. No CPM, FetchContent, Conan or vcpkg; swapping in another implicit downloader does not satisfy the policy.

## Review a dependency from local evidence

1. Identify the required capability and inspect whether the project already has a suitable dependency. Do not add the default library list wholesale.
2. Record the exact upstream release/commit and upstream URL; distinguish a fetched archive identity/checksum from a local folder label. Do not call `main` a fixed revision. If offline source provenance is missing, record that unresolved fact rather than invent a commit.
3. Inspect retained files locally: public headers, implementation, generated configuration/input files, platform backends, build target definitions and transitive bundled dependencies. A header-only package can still include other packages or configure-time generation.
4. Inspect CMake and auxiliary scripts for network acquisition and optional features that enable it. Check `FetchContent`, `ExternalProject`, CPM, package-manager hooks, `file(DOWNLOAD)`, `execute_process`, custom build commands and shell scripts. A text search is a lead: indirect wrappers, generated scripts and scripts invoked by scripts still need reading.
5. Turn off unnecessary vendor examples/tests/docs using actual version-matched options, or integrate the necessary subset through a local adapter. Do not silently trim an existing vendor tree for an unrelated task.
6. Record complete applicable license and notice texts, names, revisions and paths in `THIRD_PARTY_LICENSES.txt` or the established equivalent. Preserve separately required upstream files and copyright headers. Include retained bundled dependencies; a single root license does not cover unrelated components automatically.
7. Preserve an update recipe: source acquisition step (separate from builds), revision/hash, retained subset, patch files and reasons, build adapter, license update checks and validation commands. Do not run acquisition during an offline validation.

Keep licensing conclusions scoped: a source record plus complete text is not a legal compatibility opinion. SuiteSparse and other collections can have component-specific terms. Unknown rights or missing notices are blockers for redistribution, not permission to drop the file.

## Optional machine-readable check

Existing Markdown/text records do not need migration. If a project wants a small machine-readable companion, the included script understands:

```json
{
  "dependencies": [
    {
      "name": "library",
      "revision": "exact-release-or-commit",
      "upstream": "https://upstream.example/library",
      "source": "third_party/library-PIN",
      "licenses": ["third_party/library-PIN/LICENSE", "third_party/library-PIN/NOTICE"]
    }
  ]
}
```

Paths are relative to the supplied repository root; each source must be a directory and each notice path a nonempty file. Absolute paths and symlinks escaping that root are rejected. `licenses` lists actual applicable retained texts; do not list an invented NOTICE file. Extra explanatory fields are allowed. An empty dependency list is valid for a dependency-free project.

Prerequisite: already installed Python 3.9+ standard library only. Commands use `python3`; on Windows substitute `py -3` or an explicit Python 3 executable. Do not assume a `python` alias or install packages.

From this skill's directory:

```sh
python3 scripts/check_vendor_manifest.py --help
python3 scripts/check_vendor_manifest.py assets/minimal-project/vendor-manifest.json \
  --root assets/minimal-project
```

Expected fixture result: `status: structurally_valid`, exit 0. Exit 1 means findings; exit 2 means an unreadable/malformed/oversized input. JSON input is limited to 1 MiB with a bounded read. The script only inspects provided records and local paths; it does not execute CMake, download source, hash huge trees, alter files or read license text contents.

**What this cannot prove:** correct upstream identity, complete source subset, complete/correct license text, legal compatibility, approved patches or offline operation. A nonempty LICENSE file containing nonsense passes the structural file check; human review remains necessary. Do not describe the script result as “license audit passed” or “offline build passed”.

## Offline validation with actual evidence

Use a disposable working copy or new binary directory. Do not delete user build trees or caches. Keep required vendor source/toolchain/SDKs available; “offline” does not mean making prerequisites disappear.

1. Record platform, compiler, CMake/generator, source revision and command/preset.
2. Select an environment with network already disabled, or an explicitly authorized sandbox/network policy that denies egress. Do not change host firewall/privileged settings without approval. When no isolation facility is available, continue static review but mark network isolation unverified.
3. Use a fresh build directory, not a cached successful configure. Check that no hidden downloader cache or globally installed substitute makes the test pass in place of retained source. Root CMake should refer to retained local sources, and the compilation/link commands should agree.
4. Run configure, build and applicable tests. Capture logs and exit codes. Inspect requested network attempts as failures even if a fallback cache happened to save the build.
5. Test selected optional modes when their dependencies changed (for example GUI renderer/backend). Only claim the actual supported platforms checked; one Linux run does not validate Windows or every architecture.
6. Record unexpected generated files and ensure they are reproducible with local prerequisites. A file downloaded manually during the test invalidates that offline acceptance run.

An already network-denied environment plus clean configure/build/test is stronger evidence than no visible download in a warm online log. Neither a grep nor the JSON checker proves the complete property. If configure cannot run because CMake is unavailable, say so and provide the exact pending command; do not install it implicitly.

## Result record

```text
Dependency/revision and retained path:
Required features/backends/transitive source:
License/notice files reviewed (and unresolved terms):
Fresh binary directory / source revision:
Network denial method (or UNVERIFIED):
Configure/build/test commands and exit status:
Unexpected acquisition attempts or fallback caches:
Platforms/features not exercised:
```

This is a concise evidence record, not a new mandatory approval bureaucracy. Keep it in the project's existing dependency/development documentation where useful.
