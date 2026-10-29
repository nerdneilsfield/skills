# A complete lightweight offline starting point

Use this when the task genuinely initializes a project or explicitly changes its build/tooling. This file and the bundled example are sufficient to inspect the design offline; links at the end identify provenance, not required reading. Do not replace an existing project's conventions during an unrelated fix.

## What is actually included

The complete [minimal project](../assets/minimal-project/) contains:

```text
CMakeLists.txt                 target-scoped C++20 and local dependency
CMakePresets.json              dev/release configure + build + test
Makefile                      thin command forwarding, optional analysis commands
.clang-format / .clang-tidy    small first-party configuration
src/main.cpp                  executable
 tests/smoke.cpp               non-assert smoke test that still works in Release
third_party/fixture-math-v1/   self-authored header-only fixture, not upstream code
third_party/README.md          honest fixture provenance
THIRD_PARTY_LICENSES.txt       complete fixture license
vendor-manifest.json           optional static-check demonstration
```

The fixture library exists to demonstrate local `add_subdirectory` and target usage. It is not Eigen/Ceres, is not downloaded, and its identifier is not a real package release. This avoids shipping an external library merely to demonstrate a starter. Real projects can vendor Catch2 when a substantive test suite needs it; this smoke test deliberately has no external test framework.

Keep `src/` for implementation; introduce `include/<project>/` when a real public library interface exists. Do not create empty architecture layers, automatic release jobs, multiple GUI examples or all possible platform presets. GUI and large math dependencies remain opt-in capabilities.

## Prerequisites and exact commands

For the bundled preset paths: installed CMake >= 3.23, Ninja, and a C++20 compiler. No download is performed by the build files. On Windows, use a shell with the selected compiler environment initialized; GNU Make is optional and the direct commands below work without it. Tools missing on an offline machine are a limitation to report, not an instruction to install from the internet.

From the `assets/minimal-project` directory, in a disposable copy if you plan to edit:

```sh
cmake --list-presets
cmake --preset dev
cmake --build --preset dev
ctest --preset dev
cmake --preset release
cmake --build --preset release
ctest --preset release
```

Expected: both tests named `fixture_math_smoke` pass; running the built `offline_example` prints `42` and returns zero. Both binary directories contain `compile_commands.json`. The test uses explicit return codes rather than `assert`, so `NDEBUG` does not disable its checks.

Equivalent thin entry points, if GNU Make and its shell are present:

```sh
make configure build test PRESET=dev
make configure build test PRESET=release
```

Configure before build/test. Preset names select a single source of build configuration; do not add a second set of compiler flags to the Makefile. Its tooling path follows the documented `out/build/<preset>` convention. If a project changes `binaryDir`, change that path reference too or provide an existing build-directory lookup; do not assume arbitrary custom presets share this layout.

### If only a compiler is available

The following verifies the fixture source and local header integration, **not** CMake/presets, CTest registration or Make forwarding:

```sh
c++ -std=c++20 -Wall -Wextra -pedantic-errors \
  -I third_party/fixture-math-v1/include tests/smoke.cpp -o /tmp/fixture-smoke
/tmp/fixture-smoke
```

This example is for a Unix-like shell/compiler; use the compiler's native flags/output path elsewhere. Choose a writable temporary location. Do not call a direct-compiler success a passed CMake build. If no suitable compiler exists, do a static inspection and mark all builds unverified.

## Build choices to adapt deliberately

- Minimum CMake 3.23 matches preset schema 4 in this example. If supporting an older CMake, choose a compatible schema/features, not just a lower declared minimum.
- `app_options` carries first-party warnings and language features only. It is linked privately by app/test; vendor targets do not inherit those warning flags.
- The local dependency has its own include path as an `INTERFACE` target. Consumers link the target rather than duplicate include paths globally.
- The application target explicitly requires C++20 and disables compiler extensions. A real established C++17 project is not automatically upgraded.
- `APP_BUILD_TESTS=OFF` removes test targets, without altering analyzers, fuzzing, sanitizers or coverage. Those features are independent decisions.
- `APP_COMPILER_CACHE` is an optional explicit local compiler-launcher path, empty by default. It does not replace the configured compiler or create remote cache services. An explicitly nonexistent path causes a configure error. This example uses Ninja; validate launcher support before adapting to other generators/languages.
- Compiler cache auto-detection is not required by this small fixture. In real setup, if requested, discover installed ccache/sccache deterministically and allow off/explicit selection; missing optional cache must not break a normal build.
- Machine paths belong in ignored `CMakeUserPresets.json`; toolchain selection belongs in a toolchain file or actual supported configuration, not repeated shell flags.

## Formatting and analysis without surprise mutation

`make format` modifies only the two listed first-party files. `make format-check` is non-mutating. `clang-tidy`, `cppcheck` and aggregate `lint` are explicit requests, not implicit dependencies of every test.

These commands require installed tools. `clang-format --dry-run --Werror` is supported by modern clang-format; if an older installed version lacks those flags, use its documented local checking mode or state the limitation, never silently run mutating formatting as a check. The sample `.clang-tidy` starts with bugprone/performance checks; check supported names using the installed tool's `--list-checks` and pin/document versions actually used. Existing repository style takes precedence.

The analysis commands consume the selected compilation database after configure and any generated inputs needed by the code. The fixture has none; real projects may require a build first. Keep first-party source lists maintained as files are added. Exclude vendor/generated source from direct analysis, and filter incidental header diagnostics where the installed tool supports it rather than disable first-party checks globally.

## Adapting a real pinned dependency

```cmake
# Before add_subdirectory, set only options verified for this exact vendor version.
# The names below are illustrative; inspect the retained upstream CMake locally.
# set(ACTUAL_VENDOR_BUILD_TESTS OFF CACHE BOOL "" FORCE)
add_subdirectory(third_party/library-PIN EXCLUDE_FROM_ALL)
target_link_libraries(actual_app PRIVATE actual_vendor_target)
```

Do not paste imaginary vendor option/target names into a project. Inspect the pinned source's CMake locally. If it is not offline-safe or carries unwanted integration, a small adapter outside upstream code can define a target from the retained headers/sources and required system libraries. Preserve the true language features/platform backends; avoid stripping files until the supported platform builds confirm the subset is complete. See [vendoring and offline acceptance](vendor-and-offline.md).

## Origin of ideas

Original example for this bundle. Concept references: CMake presets/buildsystem manuals and historical personal/GUI templates linked in the main skill. No upstream template bootstrap, package manager or vendor implementation is copied. Verify APIs against installed CMake (`cmake --help-manual cmake-presets.7`, `cmake --help-command target_link_libraries`) when offline version differences matter.
