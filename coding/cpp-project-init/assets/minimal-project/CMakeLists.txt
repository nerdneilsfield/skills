cmake_minimum_required(VERSION 3.23)
project(offline_example VERSION 0.1.0 LANGUAGES CXX)

option(APP_BUILD_TESTS "Build first-party smoke tests" ON)
set(APP_COMPILER_CACHE "" CACHE FILEPATH "Optional explicit compiler launcher; empty disables")
if(APP_COMPILER_CACHE AND NOT EXISTS "${APP_COMPILER_CACHE}")
  message(FATAL_ERROR "APP_COMPILER_CACHE must name an existing executable")
endif()

# This local, self-authored fixture stands in for a reviewed vendored library.
# It is not downloaded and is not a recommendation for a real math dependency.
add_subdirectory(third_party/fixture-math-v1)

add_library(app_options INTERFACE)
target_compile_features(app_options INTERFACE cxx_std_20)
if(MSVC)
  target_compile_options(app_options INTERFACE /W4)
else()
  target_compile_options(app_options INTERFACE -Wall -Wextra -Wpedantic)
endif()

function(app_target name source)
  add_executable(${name} ${source})
  set_target_properties(${name} PROPERTIES
    CXX_STANDARD 20 CXX_STANDARD_REQUIRED YES CXX_EXTENSIONS NO)
  target_link_libraries(${name} PRIVATE app_options fixture_math)
  if(APP_COMPILER_CACHE)
    set_property(TARGET ${name} PROPERTY CXX_COMPILER_LAUNCHER "${APP_COMPILER_CACHE}")
  endif()
endfunction()

app_target(offline_example src/main.cpp)
if(APP_BUILD_TESTS)
  enable_testing()
  app_target(offline_example_test tests/smoke.cpp)
  add_test(NAME fixture_math_smoke COMMAND offline_example_test)
endif()
