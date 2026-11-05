---
name: cpp-testing
description: "Use when writing, fixing, organizing, or reviewing C++ tests: Catch2 or GoogleTest cases, CTest wiring, sanitizer test builds, floating-point assertions, and flaky or order-dependent tests. Defer shared conventions to cpp and project-wide presets to cpp-project-init. Not for crashes or races with an unknown cause (cpp-debug), benchmarks (cpp-performance), or solver and residual correctness (cpp-numerics)."
license: MIT
compatibility: Requires CMake with CTest. Examples use Catch2 v3; a project on another framework keeps it.
metadata:
  author: DengQi
---

# C++ tests that keep their meaning

Use the project's existing framework and presets. The `cpp` default is Catch2 with CTest. Vendor a framework the way `cpp-project-init` describes; do not add FetchContent to bring one in.

## Choose what to test

- Test the public interface of a target and link the test against that target. Tests that need `#define private public` are testing the wrong seam.
- For a bug, write the test first and watch it fail. For crashes and races whose cause is still unknown, go to `cpp-debug` first.
- Prefer a real collaborator or a small hand-written fake. Add a mock framework only when the interaction itself is the contract.
- Keep tests short enough to run in the normal build. Put slow suites behind a CTest label rather than an `#ifdef`.

## Agree the interface first

Before writing a suite, agree with the user on the seam the tests target: which public entry points, which layer, and what is out of scope. A test that needs `#define private public` is testing the wrong seam, and a suite written before the design settles has to be rewritten with it.

## Numerical tests

Assert the property when the property is what matters: an invariant, symmetry, monotonicity, conservation, or the residual of the defining equation. Compare against golden data only when the pipeline is fixed and the data is versioned with the test. Derive the tolerance from the error model, state it next to the assertion, and never widen it until the test passes.

## Wiring

```cmake
include(CTest)
if(BUILD_TESTING)
  add_executable(core_tests tests/core_test.cpp)
  target_link_libraries(core_tests PRIVATE core Catch2::Catch2WithMain)
  include(Catch)
  catch_discover_tests(core_tests)
endif()
```

```sh
ctest --preset dev --output-on-failure --no-tests=error
ctest --preset dev --repeat until-fail:50 -R 'Queue'
ctest --preset dev --schedule-random -j 8
```

## Gotchas

- `ctest` exits 0 when it finds no tests, so a broken test preset or filter looks green. Pass `--no-tests=error` in CI.
- `assert` vanishes under `NDEBUG`, so a test that relies on it passes in Release while checking nothing. Use framework assertions, and keep explicit checks for behavior that must hold in Release.
- A Catch2 `TEST_CASE` reruns from the top for each leaf `SECTION`. Setup runs many times, and a counter outside a section does not accumulate as it reads.
- `REQUIRE` aborts the test case, while `CHECK` continues. Use `REQUIRE` when later lines would dereference what was just checked.
- Treat assertion macros as not thread-safe unless the project enables Catch2's thread-safe option. Collect results in workers, join, then assert on the main thread. An assertion that throws in a worker terminates the process.
- `catch_discover_tests` runs the test binary after linking, so a sanitizer report or crash during startup fails the build rather than a test. `DISCOVERY_MODE PRE_TEST` moves this to test time.
- Compare floats with `Catch::Matchers::WithinAbs` or `WithinRel`. `WithinRel` around an expected value of zero never matches, so use an absolute tolerance there. Derive the tolerance from the error model.
- A coverage target is not a goal. Do not add or raise one as part of a change; line coverage says a line ran, not that anything checked its result.
- ASan and TSan cannot share a build. Give each a separate preset and binary directory, and let a clean TSan run count only for the interleavings it actually executed.
- A test that passes alone and fails in a shuffled run has shared state: a static, the working directory, the environment, or a fixed temp path. Fix the state rather than the order.

## Flaky tests

Synchronize on an observable event with a bounded wait, never a sleep. Log any random seed so a failure can be replayed. Stop and join workers on failure too, so a failed assertion cannot hang teardown. Do not add retries to hide a failure; `ctest --repeat until-fail` is for finding one.

## Report

State the preset, compiler, and exact command, plus pass, fail, and skip counts and any sanitizer or platform not run. Report whether a new regression test was seen failing first, and the interface the tests were agreed to target.

## References

- [Catch2 CMake integration](https://github.com/catchorg/Catch2/blob/devel/docs/cmake-integration.md), [Catch2 comparing floating-point numbers](https://github.com/catchorg/Catch2/blob/devel/docs/comparing-floating-point-numbers.md), [ctest manual](https://cmake.org/cmake/help/latest/manual/ctest.1.html).
