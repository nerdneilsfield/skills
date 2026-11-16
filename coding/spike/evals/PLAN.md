# Spike skill — suggested evals

Follow the repo pattern in `nerdneilsfield/skills/evals/` (trigger queries vs behavior). Do not run a paid eval until `/eval-plan` is approved. Formal method: [Testing Agent Skills Systematically with Evals](https://developers.openai.com/blog/eval-skills).

## 1. Auto-trigger (no `$spike`)

The skill should load; `python-project-init` / `cpp-project-init` / `python-ml` full pipeline should not.

**Task A.** 「在 experiments 仓库里写个脚本：用 GTSAM Python 优化一个很小的 pose graph，跑通就行，不要新建项目。」

Expect: `spike` loads, script lands as a named file in the experiments repo (or scratch if that repo is absent), shared env, one run, a verdict. No `uv init`, no CMake.

**Task B.** 「先过拟合一个 batch，看这个分类 loss 能不能降到接近 0。用现成的 torch 环境。」

Expect: one file, fixed seed, printed losses, no Lightning/Hydra/W&B, no `python-ml` reproducibility-artifact path.

## 2. Explicit trigger

**Task C.** `$spike` 用 Triton 写一个 elementwise add，和 torch 的结果比一下正确性。

Expect: `spike` + `references/cuda.md` path (Triton, `allclose` vs torch). No CUDA CMake project.

## 3. Exclusion (must not load `spike`)

**Task D.** 「给这个 C++ 库补上正式的 CMake presets 和 Catch2 测试。」

Expect: `cpp-project-init` and/or `cpp-testing`, not `spike`.

**Task E.** 「按 algorithm-experiment 的要求，对这个方法和基线做多种子消融并记 run log。」

Expect: `algorithm-experiment`, not `spike`.

## Checks

- Skill invoked / not invoked as above.
- No new per-idea `pyproject.toml`, venv, or CMake presets in A–C.
- A command was actually run, or the report is `BLOCKED` with a blocker.
- Verdict present. For B, evidence is training loss, not "forward pass didn't crash".
