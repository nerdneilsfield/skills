# C++ spikes

Default: one `idea.cpp` (or `idea/main.cpp` only if several files are unavoidable) in the experiments repo, built with the **shared** top-level Makefile. No per-idea CMake, presets, or vcpkg.

## Shared Makefile

```make
CXX ?= g++
CXXFLAGS ?= -O2 -std=c++20
CPPFLAGS ?=
LDLIBS ?=
EIGEN_INC ?= $(HOME)/opt/eigen   # or whatever the repo already uses

%: %.cpp
	$(CXX) $(CXXFLAGS) $(CPPFLAGS) $< -o $@ $(LDLIBS)

# usage: make idea && ./idea
# with Eigen: make idea CPPFLAGS="-I$(EIGEN_INC)"
```

One-liner when you are not in that repo:

```sh
g++ -O2 -std=c++20 -I"$EIGEN_INC" idea.cpp -o idea && ./idea
```

Eigen is header-only: add an include path, do not vendor it for a spike. Getting started: [Eigen Getting started](https://libeigen.gitlab.io/eigen/docs-5.0/GettingStarted.html).

## When a build file is unavoidable

A five-line CMake is a last resort, in the idea directory, no presets, no install rules:

```cmake
cmake_minimum_required(VERSION 3.20)
project(idea LANGUAGES CXX)
add_executable(idea main.cpp)
target_compile_features(idea PRIVATE cxx_std_20)
target_include_directories(idea PRIVATE "$ENV{EIGEN_INC}")
```

```sh
cmake -S . -B /tmp/idea-build && cmake --build /tmp/idea-build
```

Do not add `CMakePresets.json`, clang-tidy, or a test target.

## Compiler Explorer

For a question that is "does this snippet compile / what does it generate?" use [Compiler Explorer](https://godbolt.org) and do not create files. Paste a complete example, select the compiler, report the output.

## Quick Python bindings

Prefer calling the idea from a small C++ `main` first. If the spike *is* "can Python call this?":

- `pip`/`uv add pybind11` in the **shared** env, then one compile line ([pybind11 compiling](https://pybind11.readthedocs.io/en/stable/compiling.html)):

```sh
g++ -O3 -shared -std=c++20 -fPIC $(python -m pybind11 --includes) idea.cpp -o idea$(python-config --extension-suffix)
```

- nanobind is fine if the experiments repo already uses it; do not start a nanobind+CMake scaffold for a spike.

## Skip

`cpp-project-init`, CMake presets, FetchContent/vcpkg/Conan, Catch2/CTest, clang-format/tidy gates, `third_party/` vendoring, a library layout with `include/` + `src/`.
