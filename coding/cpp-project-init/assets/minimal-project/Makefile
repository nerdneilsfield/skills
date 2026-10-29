PRESET ?= dev
# Shared presets define out/build/<preset>; no compiler flags are repeated here.
BUILD_DIR = out/build/$(PRESET)
FIRST_PARTY = src/main.cpp tests/smoke.cpp
.PHONY: help configure build test format format-check clang-tidy cppcheck lint
help:
	@printf '%s\n' 'make configure build test PRESET=dev|release' 'make format | format-check | clang-tidy | cppcheck | lint'
configure:
	cmake --preset $(PRESET)
build:
	cmake --build --preset $(PRESET)
test:
	ctest --preset $(PRESET)
format:
	clang-format -i $(FIRST_PARTY)
format-check:
	clang-format --dry-run --Werror $(FIRST_PARTY)
clang-tidy:
	clang-tidy -p $(BUILD_DIR) $(FIRST_PARTY)
cppcheck:
	cppcheck --project=$(BUILD_DIR)/compile_commands.json --enable=warning,style,performance,portability --error-exitcode=1 --inline-suppr -ithird_party
lint: format-check clang-tidy cppcheck
