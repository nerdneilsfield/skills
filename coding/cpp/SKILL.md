---
name: cpp
description: "Build and maintain C++ projects using CMake presets, vendored dependencies, and consistent local build and lint entry points."
---

# C++ development conventions

Apply these engineering defaults to C++ work. This skill supplies project conventions, not a separate planning or approval workflow; it can accompany Counterweight. Explicit task requirements take precedence. For existing projects, inspect relevant build files, presets, tooling configuration, and nearby code first. Apply conventions within the requested scope; a local fix does not authorize migrating the project's build system or replacing existing libraries.

## Language and build

- Default to C++20 unless a concrete compiler, platform, dependency, or user requirement calls for another standard. Require the selected standard and disable compiler-specific language extensions for first-party targets. Keep ownership, lifetime, and error handling clear using existing project idioms; do not introduce abstractions merely to showcase language features.
- Use CMake as the build definition. Prefer target-scoped sources, include directories, compile options, definitions, and dependencies with appropriate `PRIVATE`, `PUBLIC`, and `INTERFACE` visibility. Avoid global flags that leak first-party policy into vendored code.
- Commit shared platform and configuration choices in `CMakePresets.json`. Use inheritance for common settings, separate build directories for incompatible configurations, and toolchain files when needed. Keep machine-specific paths and overrides in untracked `CMakeUserPresets.json`. Choose a minimum CMake version and preset schema compatible with each other and the project's supported environments.
- Provide presets for platforms actually required by the task or project, not a speculative platform matrix. Pair configure and build presets; add test presets when tests exist. Avoid hardcoded developer paths. Document environment prerequisites such as the Windows compiler environment.
- Default `CMAKE_EXPORT_COMPILE_COMMANDS` to `ON`. Prefer Ninja for consistent cross-platform builds and compilation database support. CMake exports the database with Ninja and Makefile generators; do not promise it from Visual Studio or Xcode generators. When those generators are required, provide a suitable tooling configuration if analysis needs a database.
- Support ccache or sccache through CMake's compiler-launcher mechanism for supported generators and languages. Select one available launcher deterministically, allow explicit selection or disabling, and keep the real compiler as the compiler. An absent optional cache must not break normal builds; an explicitly requested missing launcher should produce an actionable error. Do not configure remote cache services or credentials implicitly.

## Vendored dependencies

Keep third-party source in `third_party/<name-version>/`, pinned to an identifiable upstream release or commit. Configure, build, and test must work offline once source and the documented compiler/platform tools are present. Dependency acquisition is a deliberate maintenance step, never a configure-time or build-time download.

Do not introduce Conan, vcpkg, CPM, FetchContent downloads, ExternalProject downloads, Git submodules, or package-installed substitutes for vendored libraries unless explicitly requested. Platform SDKs and development tools are prerequisites, not libraries to copy into the repository.

Vendor the smallest complete source subset needed for the selected features and supported platforms. Include necessary headers, implementations, generated inputs, transitive dependencies, and build integration. Omit unrelated upstream examples, benchmarks, tests, documentation, and assets unless required to build, use, or redistribute the chosen subset. Do not interpret “core only” as permission to drop required platform backends or legal notices.

Use one discoverable root `THIRD_PARTY_LICENSES.txt` as the consolidated record, or reuse the repository's equivalent. For each dependency, identify its name, pinned version/revision, upstream URL, retained source location, and complete applicable license and notice texts. Include licenses of retained bundled dependencies; a license name or URL alone is insufficient. Preserve source copyright/license headers and any separately required upstream notices or license files. Consolidation does not authorize stripping those notices or changing third-party license terms.

Record the retained subset, local patches and their reasons, and enough acquisition/update information to repeat the vendor operation in a concise existing dependency record or `third_party/README.md`. Keep upstream code recognizable; place project build adapters outside it where practical. Update source, provenance, and license records together. Do not silently trim files from an already-vendored tree during an unrelated edit.

## Libraries: only when needed

Use the existing suitable dependency first in established projects. When choosing a new library for a required capability, prefer:

| Capability | Preferred library |
| --- | --- |
| Tests | Catch2, integrated with CTest |
| Logging | spdlog |
| Command-line argument parsing | [p-ranav/argparse](https://github.com/p-ranav/argparse) |
| GUI | Dear ImGui with SDL |

Do not add all four to a starter project. Pin compatible versions when introducing them and apply the vendoring policy to their required dependencies. For GUI work, choose an SDL version, ImGui platform backend, and renderer that fit the actual target platforms; retain their required source and state the choice. Do not assume a preferred library's upstream CMake configuration is offline-safe without inspecting it.

## Formatting, analysis, and command entry points

For a new project or requested tooling setup, provide `.clang-format`, `.clang-tidy`, and a reproducible cppcheck invocation/configuration. Match existing style when present; otherwise choose and record a consistent style without inventing an elaborate custom rule set. Keep analyzer settings in version control and document compatible tool versions where behavior depends on them.

- Separate clang-format checking from formatting that modifies files.
- Run clang-tidy and cppcheck with the selected build's compilation database and relevant configuration. Make required configure/generated-header prerequisites explicit. Analyze first-party translation units; exclude vendored and generated code from direct formatting and analysis, and filter third-party diagnostics where supported.
- Keep suppressions narrow and explain non-obvious ones. Do not hide first-party findings with blanket exclusions. Make an explicitly invoked check fail clearly if its required tool or input is missing; do not silently report success after skipping it.
- Provide a root Makefile as a thin, documented entry point. Typical targets are `help`, `configure`, `build`, `format`, `format-check`, `clang-tidy`, `cppcheck`, and an aggregate non-mutating `lint`; include `test` when tests exist. Reuse established names in an existing project. Forward preset selection consistently to the underlying commands.
- Keep build settings in CMake/presets and analysis logic in one place: a short recipe, CMake target, or small script as appropriate. Do not duplicate flags or commands across Makefile, scripts, and CI. Document Make/shell prerequisites on supported platforms, and preserve direct CMake entry points for environments without Make.

## Maintainability and verification

A human or another agent without chat history must be able to locate code, follow the same file organization and style, and build, run, and check the next change using the repository alone. Keep concise development instructions covering prerequisites, preset selection, command entry points, and dependency updates in the existing README/development guide. Link to configuration as the source of truth rather than copying it into prose. Explain non-obvious ownership, ordering, platform constraints, and trade-offs near the relevant code; avoid comments that merely restate statements.

Verify the changed behavior with proportionate checks. For build/tooling setup, exercise the relevant local configure/build and Makefile entry points, confirm that the compilation database is actually produced, and run the configured first-party checks. For a dependency change, verify the retained subset builds without acquisition during configure/build/test. Run relevant tests when present; introducing this skill does not require adding tests to every change. Report untested platforms and unavailable tools accurately rather than claiming the whole preset matrix passed. Do not run an entire tooling matrix for a small unrelated source edit.
