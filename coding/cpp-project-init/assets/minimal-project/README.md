# Self-authored offline C++ fixture

This is a complete small example, not a generator or a real vendor package collection. `fixture-math-v1` is original sample code with no dependencies. Its identifier is not an upstream tag.

Prerequisites: CMake >= 3.23, Ninja and a C++20 compiler, already installed. No network acquisition appears in this project. Do not install anything implicitly on an offline machine.

```sh
cmake --preset dev
cmake --build --preset dev
ctest --preset dev
# Repeat with release for the other paired preset.
```

`offline_example` prints `42`; `fixture_math_smoke` exits zero. Generated files live in `out/build/<preset>`, including the compilation database. GNU Make is optional: `make configure build test PRESET=dev` forwards these commands. Read `make help` for optional formatting and analysis entry points; those tools must already be installed and explicitly requested.

The CMake cache variable `APP_BUILD_TESTS` controls only tests. `APP_COMPILER_CACHE` can name an installed compiler-launcher executable; it is off by default, does not replace the compiler and does not set up remote services.

See the skill's `references/layout-and-build.md` and `references/vendor-and-offline.md` for adaptation, full limitations and offline acceptance. A successful direct compiler smoke test does not prove the CMake presets or offline network isolation.
