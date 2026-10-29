# Eigen expressions and numerical data boundaries

Read for wrong matrix values, dangling expressions, overlapping assignments, unexpected copies, or an adapter between Eigen and image/point-cloud storage. This is a diagnosis worksheet, not a requirement to replace the project's types.

## Start from the failing operation

Record scalar type, dimensions, storage order, outer/inner stride, owner and lifetime for each operand. Preserve a tiny input with asymmetric/distinct values: identity matrices and constant images can hide transposes, stride errors and channel swaps. Check the adapter against an explicit element-wise copy before optimizing it.

| Observation | Smallest discriminating check |
| --- | --- |
| Correct once, corrupt after another operation | Track owner destruction, vector reallocation and retained expression operands |
| Different result for a block/ROI | Compare addresses/strides and overlapping source/destination regions |
| Works only for square matrices | Test a non-square shape and distinct row/column patterns |
| Correct Debug, wrong optimized build | Check lifetime, alias and alignment contracts before blaming vectorization |
| Large temporary/allocation cost | Materialize only necessary boundaries; measure with representative dimensions |

## Aliasing and expression lifetime

- Overlap is about addressed coefficients, not variable names: two blocks or maps can share storage. For an overlapping assignment, evaluate the right-hand side into an owning temporary before overwriting, or use a documented in-place operation.
- `noalias()` promises non-overlap to the expression machinery. It is not a checker and is inappropriate for an overlapping transpose or matrix product.
- A stored `auto` expression can borrow operands instead of storing results. If the result must outlive inputs or remain unchanged after mutation, make it an owning matrix/vector of the intended scalar and shape. An `.eval()` buried inside a larger lazy expression can itself create a short-lived operand; evaluate the complete needed result at the retention boundary.

Original micro-check, intended to be added to the project's existing Eigen test target:

```cpp
#include <Eigen/Core>
#include <cassert>

void check_overlapping_block_copy() {
    Eigen::Matrix3i a;
    a << 1, 3, 5, 7, 11, 13, 17, 19, 23;
    const Eigen::Matrix2i expected = a.topLeftCorner<2, 2>();
    a.bottomRightCorner<2, 2>() = a.topLeftCorner<2, 2>().eval();
    assert((a.bottomRightCorner<2, 2>().array() == expected.array()).all());
}
```

Use the project's test assertions instead of `assert` if `NDEBUG` is enabled; do not treat a disabled assertion as a test. This snippet is an application example, not a claim it was compiled in this repository.

## Mapping external storage

Before creating `Eigen::Map`, answer all of these:

1. Does the buffer contain the exact scalar type and enough valid elements? A byte reinterpretation is not numeric conversion.
2. Is row/column-major interpretation correct? Are strides measured in the units the API expects? Convert byte strides only after checking divisibility by scalar size.
3. Does the chosen aligned/unaligned map match the actual allocation and offset? An aligned base does not imply every ROI offset is aligned.
4. Who owns the storage, how long does it live, and can another thread or container operation invalidate it? A map does not retain ownership.
5. Is a mutable map authorized, and can writes alias another live view? Prefer const maps for read-only input.

Specific boundaries:

- **OpenCV:** inspect `type()`, channel count, `rows`, `cols`, `step` and `isContinuous()`. Cropped ROIs often retain parent row pitch. Shallow `Mat` copies share backing storage; `.clone()` changes ownership/copy cost. Choose the intended channel interpretation rather than mapping interleaved RGB as a single-channel matrix.
- **PCL:** inspect the exact point type and registered fields. Padding, packed color and alignment mean an XYZ record is not automatically three adjacent scalars with point stride `3 * sizeof(float)`.
- **Open3D:** inspect tensor dtype, shape, strides and ownership. Conversion/contiguity operations may allocate; include them in CPU end-to-end timing. Do not infer zero-copy from a familiar constructor name.

A deliberate copy can simplify lifetime and layout contracts. Keep it if its measured cost is acceptable; remove it only with a validated replacement.

## Version and ABI checks

Record Eigen version, C++ mode and relevant alignment/vectorization macros across translation units. Modern C++17 aligned allocation reduces some older allocation problems but does not make arbitrary buffers or ABI mixes safe. Do not paste legacy aligned allocator macros without identifying the affected allocation path. For small fixed matrices, first measure expression/layout costs; a BLAS switch is not an automatic improvement.

## Offline lab: overlap, padded rows and owning results

Use already-vendored Eigen headers and an installed compiler; this workflow neither installs nor downloads anything. Save the following as a temporary source outside production code, or turn each check into the project's existing test framework. It deliberately returns a failing exit status rather than rely on assertions disabled by `NDEBUG`.

```cpp
#include <Eigen/Core>
#include <iostream>

int main() {
    // A padded two-row image-like buffer: the last entry of each row is padding.
    float pixels[] = {1.f, 2.f, 3.f, -99.f, 4.f, 5.f, 6.f, -99.f};
    using RowMatrix = Eigen::Matrix<float, Eigen::Dynamic, Eigen::Dynamic,
                                    Eigen::RowMajor>;
    using PitchedMap = Eigen::Map<const RowMatrix, Eigen::Unaligned,
                                  Eigen::OuterStride<>>;
    PitchedMap image(pixels, 2, 3, Eigen::OuterStride<>(4));
    if (image(0, 2) != 3.f || image(1, 0) != 4.f) {
        std::cerr << "stride interpretation failed\n";
        return 1;
    }

    // Retained results own their storage; changing the source must not change them.
    const RowMatrix saved = image;
    pixels[0] = 42.f;
    if (image(0, 0) != 42.f || saved(0, 0) != 1.f) {
        std::cerr << "view/owner boundary failed\n";
        return 1;
    }

    Eigen::Matrix3i a;
    a << 1, 3, 5, 7, 11, 13, 17, 19, 23;
    const Eigen::Matrix2i expected = a.topLeftCorner<2, 2>();
    a.bottomRightCorner<2, 2>() = a.topLeftCorner<2, 2>().eval();
    if (!(a.bottomRightCorner<2, 2>().array() == expected.array()).all()) {
        std::cerr << "overlap copy failed\n";
        return 1;
    }
    std::cout << "PASS: padded rows, owner lifetime boundary, overlap copy\n";
}
```

With the source saved as `eigen_boundary_check.cpp`, adapt the **local path**, not a download URL:

```sh
c++ -std=c++20 -O2 -I /local/project/third_party/eigen-version \
    eigen_boundary_check.cpp -o eigen_boundary_check
./eigen_boundary_check
```

Prefer the existing project test target when compiler/toolchain flags matter. The expected exit status is 0 and the single PASS line. A compiler/header absence is a missing prerequisite, not a failed numerical check. This is original example code; this reference does not claim the installed project/library combination has been tested.

Interpretation and variations:

- Mapping with a packed outer stride of 3 would read `-99` as the second row's first value. The fixture makes the wrong assumption visible.
- Change the valid image size and pitch together; preserve allocated storage bounds. Also test a crop offset into the parent allocation, keeping its original pitch.
- The explicit `RowMatrix saved` distinguishes a stable owning snapshot from a live view. A view reflecting source mutation is correct only if that is the intended contract.
- For read-only ingress use a const map. Do not “fix” a lifetime bug by marking the pointer const; constness does not keep the owner alive.
- Exact integer/easily represented float equality is intentional for these indexing tests. Use scale-aware tolerances for arithmetic result checks, not for detecting a one-row addressing error.

## Sources to consult

- Eigen [aliasing](https://libeigen.gitlab.io/eigen/docs-3.4/group__TopicAliasing.html), [Map](https://libeigen.gitlab.io/eigen/docs-3.4/classEigen_1_1Map.html), [expression pitfalls](https://libeigen.gitlab.io/eigen/docs-3.4/TopicPitfalls.html), [alignment assertions](https://libeigen.gitlab.io/eigen/docs-3.4/group__TopicUnalignedArrayAssert.html). These are the official versioned Eigen 3.4 documentation branch (currently identifying 3.4.1), not nightly. Use the retained project headers/docs when its pinned version differs; no upgrade is implied.
- [OpenCV Mat reference](https://docs.opencv.org/4.x/d3/d63/classcv_1_1Mat.html), [PCL point-type tutorial](https://pointclouds.org/documentation/tutorials/adding_custom_ptype.html), [Open3D Tensor source](https://github.com/isl-org/Open3D/blob/main/cpp/open3d/core/Tensor.h). Verify interfaces against the pinned library release, not `main` alone.
