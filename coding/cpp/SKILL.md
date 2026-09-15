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

## Code and interface conventions

- Prefer value semantics and RAII for memory, files, sockets, locks, and other resources. Use exclusive ownership by default; `shared_ptr` needs a real shared-lifetime requirement. Prefer the Rule of Zero. When a type directly manages a resource, deliberately define or delete its copy/move operations and destructor rather than relying on accidental copying.
- Treat references, raw observer pointers, `string_view`, and `span` as borrows. Establish who owns the underlying data and what invalidates it. Pay particular attention to stored views, callbacks, and asynchronous work; a view neither extends lifetime nor prevents invalidation. Transfer or retain ownership when work must outlive the caller.
- Make headers self-contained, with include guards or `#pragma once` and direct includes for the declarations they use. Do not rely on inclusion order or transitive includes, or put global `using namespace` directives in headers. Expose only the necessary public contract and keep implementation details and third-party types internal where practical, without automatically adding PImpl or wrapper layers.
- Follow the project's error model consistently. Translate exceptions and error results at explicit boundaries; make failure and post-failure object state understandable. Consider `[[nodiscard]]` where ignoring a result is likely a bug. Do not change the language standard or add a result library merely to use `std::expected` in a C++20 project.

Read the relevant section of [references/code-examples.md](references/code-examples.md) when implementing a resource owner, retaining borrowed data, changing public headers, or defining failure semantics. Its examples illustrate decisions, not mandatory class shapes, naming conventions, or code to insert into plans.

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
| Terminal progress for iterative or batch work | [p-ranav/indicators](https://github.com/p-ranav/indicators), for tqdm-like feedback |
| GUI | Dear ImGui with SDL |

Do not add these libraries wholesale to a starter project. Pin compatible versions when introducing them and apply the vendoring policy to their required dependencies. For GUI work, choose an SDL version, ImGui platform backend, and renderer that fit the actual target platforms; retain their required source and state the choice. Do not assume a preferred library's upstream CMake configuration is offline-safe without inspecting it.

For long-running iteration or batch processing, consider indicators when progress helps the user understand the wait; a loop alone does not justify a progress UI. Show measured completion when a total is known, or activity without a fabricated percentage when it is unknown. Throttle updates, keep progress separate from machine-readable output, and disable animated rendering or use sparse plain messages for non-interactive output. Coordinate progress with logging so they remain readable.

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

Use targeted sanitizer configurations when memory, undefined-behavior, or concurrency risks justify them and the toolchain supports them. Keep diagnostic flags out of ordinary release presets. For performance work, establish a representative workload and baseline, locate the relevant bottleneck, then remeasure under comparable conditions while checking behavior. Do not claim a speedup from intuition or add benchmarks to unrelated tasks.

When tests are needed, make them reproducible and isolated: preserve random seeds, use independent temporary data, and synchronize on observable conditions with bounded waits instead of guessing completion with sleeps. Test behavior rather than internal call choreography; do not introduce interfaces or mocks solely to fit a test template. Read [references/diagnostics.md](references/diagnostics.md) when selecting diagnostic runs, measuring performance, or fixing unstable tests.
