#include <fixture_math/scale.hpp>
#include <iostream>

int main() {
  const double result = fixture_math::scale(21.0, 2.0);
  std::cout << result << '\n';
  return result == 42.0 ? 0 : 1;
}
