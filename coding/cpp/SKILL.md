---
name: cpp
description: Use when writing, reviewing or maintaining C++ code and its shared language, ownership, build, dependency or interface conventions.
---

# Shared C++ engineering conventions

This is shared policy and routing, not another planning/approval workflow. Inspect the project's build, tooling and nearby code before editing. Explicit current task requirements take precedence; historical templates are not requirements. A local fix does not authorize a build migration, library replacement or whole-repository cleanup.

## Load only the relevant specialist

| Task | Skill |
| --- | --- |
| New project or explicitly requested build/tooling restructuring | `cpp-project-init` |
| Unexplained/wrong results after minimal triage; crash, hang, race, corruption or unresolved build failure | `cpp-debug` |
| CPU latency, throughput, cacheline/lock contention, scheduling/oversubscription, paging, allocation or scaling problem | `cpp-performance` |
| Creating/modifying Eigen, Ceres/GTSAM, manifold, sparse/BLAS or numerical data-boundary code; numerical failures or slowness | `cpp-numerics` |

Use only the relevant specialist alongside this language/interface policy. If a named skill is unavailable, tell the user its exact name to install from this bundle (for example, `cpp-project-init` for build/vendor work or `cpp-debug` for deeper diagnosis). Do not perform a global skill search, fetch a substitute, install anything automatically or invent the missing skill. Continue only the independent work that does not require it. CUDA is separate and deferred; do not fold it into this CPU split.

## Language, ownership and interfaces

- Default new first-party code to C++20 unless compiler, platform, dependency or explicit requirements dictate otherwise. Preserve established project constraints. Require the selected standard and disable compiler language extensions; avoid novelty-driven abstractions.
- Prefer value semantics, RAII and the Rule of Zero. Use exclusive ownership by default; `shared_ptr` requires actual shared lifetime. A direct resource owner deliberately defines or deletes relevant copy/move/destructor operations.
- References, observer pointers, `string_view` and `span` are borrows: establish owner, lifetime and invalidation. Stored views, callbacks and async work do not extend underlying lifetime. Transfer/retain ownership when work outlives the caller.
- Keep public headers self-contained with guards and direct includes, no global `using namespace`. Expose necessary contracts, keep implementation/vendor types internal where practical, and do not automatically add PImpl or wrapper layers.
- Follow the existing error model at explicit boundaries, including post-failure object state. Use `[[nodiscard]]` where ignoring a result risks a bug. Do not upgrade a C++20 project or add a result library merely for `std::expected`.

Read [ownership/interface examples](references/code-examples.md) when relevant. They are examples, not mandatory class shapes or plan content.

## Build, vendor and offline policy: one owner

[cpp-project-init](../cpp-project-init/SKILL.md) owns toolchain/build setup, dependency vendoring, complete source/legal records and offline acceptance. Read its relevant local reference when that area changes; do not maintain a second policy here. An ordinary source fix reuses the existing build and does not authorize initialization or migration. If this owner skill is missing, ask the user to install **`cpp-project-init`** from this bundle; do not search or download a replacement.

## Libraries: only for a needed capability

Use the existing suitable dependency in established projects. New choices prefer:

| Capability | Preference |
| --- | --- |
| Tests | Catch2 with CTest |
| Logging | spdlog |
| CLI parsing | [p-ranav/argparse](https://github.com/p-ranav/argparse) |
| Terminal progress | [p-ranav/indicators](https://github.com/p-ranav/indicators) |
| GUI | Dear ImGui with SDL |

Do not add this bundle wholesale. For dependency integration, apply the owning `cpp-project-init` policy. GUI work needs an explicit compatible SDL version, platform backend and renderer for actual platforms.

Progress UI is optional, not justified by every loop. Use a real known total or indeterminate activity, throttle updates, separate it from machine output, coordinate with logs, and disable animation/use sparse plain text for non-TTY output.

## Proportionate verification and handoff

Keep concise repository instructions for prerequisites, preset/command selection and dependency updates. Link to configuration instead of duplicating flags. Explain non-obvious ownership, ordering and platform trade-offs, not each line of code.

Verify changed behavior with relevant checks. For build/dependency changes use the acceptance rules owned by `cpp-project-init`. Report untested platforms and unavailable tools; no unrelated full-matrix requirement or tests added merely because this skill exists.

Use targeted diagnostic configurations for relevant memory/UB/concurrency risks, separate from ordinary Release. Performance claims need comparable before/after measurements and correctness checks. Reproducible tests preserve seeds, isolate temporary state and wait on bounded observable conditions; avoid guessed sleeps and internal call choreography. Do not create interfaces/mocks merely to satisfy test templates. See [targeted diagnostics](references/diagnostics.md), then load the specialist for deeper work.

## Reading pointers

Use [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines), [C++ best practices](https://github.com/cpp-best-practices/cppbestpractices), and [A Tour of C++](https://www.stroustrup.com/tour3.html) for specific questions. These links do not import their licenses, standard-version choices, package-manager recommendations or entire workflows. Specialist skills link their actual tool/library references.
