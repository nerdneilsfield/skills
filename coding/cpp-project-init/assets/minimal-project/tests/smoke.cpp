#include <fixture_math/scale.hpp>

// Keep the offline fixture dependency-free; a real test suite may vendor Catch2.
// Do not use assert: this test must retain its checks in Release with NDEBUG.
int main() {
  if (fixture_math::scale(21.0, 2.0) != 42.0) return 1;
  if (fixture_math::scale(-3.0, 2.0) != -6.0) return 2;
  if (fixture_math::scale(0.0, 4.0) != 0.0) return 3;
  return 0;
}
