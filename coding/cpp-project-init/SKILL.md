---
name: cpp-project-init
description: Use when creating a C++ project or explicitly restructuring its CMake presets, vendored dependencies, or developer command entry points.
---

# Lightweight C++ project initialization

Build the smallest usable project, not a framework for hypothetical projects. This skill is the single owner of toolchain/build, vendor/legal-record and offline-build policy. Apply [cpp](../cpp/SKILL.md) for language, ownership and preferred capability libraries. If `cpp` is unavailable, tell the user to install **`cpp`** from this bundle; do not globally search, fetch a substitute or automatically install it. Current requirements override historical templates.

## Offline supporting materials

- For a complete local starter and exact commands, read [layout and build](references/layout-and-build.md); its [minimal project assets](assets/minimal-project/) include coherent CMake/presets/Makefile and original fixture source.
- For adding/updating vendor source or proving offline operation, read [vendor and offline acceptance](references/vendor-and-offline.md). The optional checker is `python3 scripts/check_vendor_manifest.py --help` from this skill directory; it is a read-only structural check, not license/offline certification.
- No runtime command requires network access. Missing local tools are reported, not installed implicitly. References explain the workflow locally; source links are provenance.


## Establish the boundary

- Inspect existing code, build files, supported compilers, platforms and dependency constraints. A bug fix is not permission to initialize or migrate the project.
- Default new first-party code to C++20; keep an established standard when required. Require the standard and disable compiler language extensions on first-party targets.
- Choose executable, library, or both from the actual deliverable. Add `include/<project>/` only for a public interface, `src/` for implementation, and tests when there is behavior to test. GUI and numerical stacks are not starter defaults.
- Reuse useful ideas from old templates, not their bootstrap code, package managers, CI matrix, or coupled feature switches.

## Minimal build contract

| Concern | Deliverable |
| --- | --- |
| Build definition | Root `CMakeLists.txt`; target-scoped sources, dependencies and visibility |
| Shared configurations | `CMakePresets.json` with paired configure/build and applicable test presets |
| Local overrides | Ignored `CMakeUserPresets.json`; no developer-specific absolute paths |
| Dependencies | Pinned source under `third_party/<name-version>/`, provenance and complete legal notices |
| Developer commands | Thin root Makefile forwarding to CMake/presets and first-party check commands |
| Instructions | Concise README: prerequisites, exact commands, outputs, dependency update steps |

Choose a CMake minimum and preset schema compatible with supported machines. Use preset inheritance for common settings and toolchain files when needed. Start with actual local Debug and Release needs, not every OS/compiler combination. Keep incompatible configurations in separate binary directories. Diagnostic configurations are opt-in, not hidden inside the test switch.

Prefer Ninja; set `CMAKE_EXPORT_COMPILE_COMMANDS=ON` for Ninja/Makefile generators and verify the file exists. Visual Studio/Xcode generators do not promise this database. Select a supported tooling configuration if one is needed there.

Support optional ccache/sccache via compiler launchers on supported generators/languages, keeping the real compiler as the compiler: deterministic selection, explicit disable/selection, no implicit remote cache services or credentials. Optional absence is harmless; explicitly requesting a missing tool is an actionable error.

## Vendor source, never acquisition at configure time

No CPM, FetchContent, Conan or vcpkg. Do not substitute ExternalProject downloads, submodules, or system package copies as an acquisition workaround. Compiler tools and platform SDKs remain documented prerequisites.

1. Identify the exact required library features and pin upstream release/commit. Acquire source only in an authorized, separate maintenance operation.
2. Retain the smallest **complete** subset: implementations, headers, generated inputs, platform backends and transitive dependencies. Inspect upstream CMake for indirect downloads and default tests/examples that pull extra dependencies.
3. Integrate retained source with local `add_subdirectory` or a small target adapter outside upstream code. Explicitly disable unwanted upstream features. Do not globally impose first-party warning flags on vendors.
4. Record URL, revision, subset, local patches and update procedure. Maintain complete applicable licenses/notices in the root consolidated record, preserving required upstream files and headers too; URLs alone are insufficient.
5. Verify configure/build/test from fresh build directories with dependencies already present and network acquisition unavailable. A warm cache or successful online build is not offline evidence.

Choose only needed capabilities using the [cpp library preferences](../cpp/SKILL.md#libraries-only-for-a-needed-capability); that skill owns the preference list and progress/GUI conventions.

## Commands and checks

Provide `help`, `configure`, `build`, `format`, `format-check`, `clang-tidy`, `cppcheck`, `lint`, and `test` when applicable. `lint` and `format-check` do not modify files. Forward selected presets consistently; do not duplicate build flags across Makefile, CMake, scripts and CI. Document Make/shell prerequisites and platform compiler environments (such as the Windows compiler environment). Direct CMake commands remain usable without Make.

For example, if the project defines a `dev` configure preset and matching build/test presets:

```sh
cmake --preset dev
cmake --build --preset dev
ctest --preset dev --output-on-failure
```

For a new project or requested tooling setup, provide versioned `.clang-format`, `.clang-tidy` and reproducible cppcheck configuration. Match existing style; otherwise choose and record a consistent style without an elaborate custom rule set. Document compatible tool versions where behavior depends on them. Analyze first-party translation units with the real compilation database and generated-header prerequisites. Exclude vendor/generated code from direct formatting and analysis; filter third-party diagnostics where supported and keep suppressions narrow. Explicit checks fail clearly when their required tool or input is absent.

Tests, sanitizers, coverage, fuzzing and analyzers are separate choices. Enabling tests must not silently enable them all. No automatic formatter commits, template cleanup bots, or speculative deployment setup.

## Acceptance evidence

Report the tree and chosen dependencies; exercised configure/build/test presets and thin command entry points; compilation database location; format/analyzer results; offline-verification method; untested platforms and unavailable tools. If network isolation is unavailable, report offline behavior as unverified rather than infer it from a text scan. Do not require a full matrix for an unrelated existing-project edit.

## References

- [CMake presets](https://cmake.org/cmake/help/latest/manual/cmake-presets.7.html) and [buildsystem targets](https://cmake.org/cmake/help/latest/manual/cmake-buildsystem.7.html): match documentation to the chosen CMake version.
- Historical layout references only: [personal template](https://github.com/nerdneilsfield/cpp-project-template), [GUI starter](https://github.com/cpp-best-practices/gui_starter_template), [C++ best practices](https://github.com/cpp-best-practices/cppbestpractices). Their dependency and automation defaults are not adopted.
