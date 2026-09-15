# Ownership, interfaces, and failure examples

Read only the section relevant to the current change. These C++20 examples are intentionally small; adapt names, error handling, and file layout to the repository. They are not a starter framework.

## Resource ownership and Rule of Zero

When standard members already own the resources, let them implement destruction and copy/move behavior:

```cpp
#include <cstddef>
#include <vector>

struct Packet {
    std::vector<std::byte> payload;
};
```

Do not write five special members just because a type contains a buffer. For a C API handle, an existing RAII facility with the correct deleter may suffice:

```cpp
#include <cstdio>
#include <memory>

struct FileCloser {
    void operator()(std::FILE* file) const noexcept {
        std::fclose(file);
    }
};

using File = std::unique_ptr<std::FILE, FileCloser>;

[[nodiscard]] File open_readonly(const char* path) {
    return File{std::fopen(path, "rb")};
}
```

The caller checks for an empty result. `File` owns the handle and is movable but not copyable. This deleter releases the resource; it is not an example of reliably committing buffered writes. If successful close/flush is part of the operation's outcome, expose and check that operation explicitly before destructor cleanup. Use the API's actual release function, not `delete`, for foreign handles.

## Borrow now, own when retained

```cpp
#include <string>
#include <string_view>
#include <utility>

bool has_prefix(std::string_view input, std::string_view prefix) {
    return input.starts_with(prefix);
}

class PendingMessage {
public:
    explicit PendingMessage(std::string text) : text_(std::move(text)) {}

    // Borrow is valid only while this object and its storage remain valid.
    std::string_view text() const noexcept { return text_; }

private:
    std::string text_;
};
```

`has_prefix` consumes its borrows during the call. `PendingMessage` retains its input, so it owns a string. Changing the member to `string_view` would require an external lifetime contract. Likewise, a callback that runs later must not capture a caller's local data by reference unless completion is guaranteed before that data expires. Prefer moving owned data into the work item when that matches the operation.

`span` can express a borrowed contiguous range, but its storage can still expire or be invalidated by container reallocation. Do not describe views as automatically lifetime-safe or bounds-checked.

## A self-contained public header with an explicit failure contract

```cpp
#ifndef APP_PORT_CONFIG_H
#define APP_PORT_CONFIG_H

#include <cstdint>
#include <optional>
#include <string_view>

namespace app {

// Accepts a complete decimal port in [1, 65535]; nullopt means invalid input.
// Does not retain input. Invalid input leaves the caller's configuration unchanged.
[[nodiscard]] std::optional<std::uint16_t> parse_port(std::string_view input);

}  // namespace app

#endif
```

The header supplies its own includes and communicates the needed contract without exposing the parser implementation. `optional` fits this example because callers only need valid/invalid. When callers need failure reasons, use the project's established error type; when exceptions are the established model, retain that model. Do not flatten meaningful errors to an empty optional just to follow the example.

When header independence is at risk, compile a tiny translation unit that includes the changed header first. This is a targeted check, not a requirement to add permanent tests for every header.

## Reading sources

These examples are written for this skill. The selected principles also appear in [ECC's C++ coding standards](https://github.com/affaan-m/ecc/blob/main/skills/cpp-coding-standards/SKILL.md), [Jeffallan's C++ Pro](https://github.com/Jeffallan/claude-skills/blob/main/skills/cpp-pro/SKILL.md), and [Trail of Bits' modern-cpp](https://github.com/trailofbits/skills/blob/main/plugins/modern-cpp/skills/modern-cpp/SKILL.md). Consult sources for a specific unresolved question; do not import their entire workflow, standard-version preferences, or mandatory checklists.
