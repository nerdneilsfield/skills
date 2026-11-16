---
name: spike
description: "Use when the user wants a throwaway spike or quick POC to validate one idea: spike this, $spike, POC 模式, 做个 POC, just make it run, validate the idea, overfit one batch, or try it before building it for real. Write the smallest thing that can run in the experiments repo or a scratch dir, execute it, and stop with a verdict. Not for production implementation, project scaffolding (cpp-project-init, python-project-init), formal experiment campaigns (algorithm-experiment), or paper number reproduction (paper-reproduce)."
license: MIT
metadata:
  author: DengQi
---

# Spike

A spike is the smallest executable check of one assumption. The verdict is the deliverable.

## Workflow

If the user already named the experiment, start coding. Do not open a planning phase.

1. **Assumption** — one falsifiable claim, one sentence. If several, do the riskiest first.
2. **Place** — put it in the experiments repo when one is present; otherwise a scratch dir in the current repo (see Placement).
3. **Approach** — the shortest path that can actually run. Load only the matching language reference below.
4. **Implement** — reuse the shared environment and tools already there. One file, or a small directory, named after the idea. Hardcode parameters and sample data.
5. **Run** — use representative input. Do not mock the core behavior being validated. Do not skip actual execution.
6. **Report and stop.** Productionization is a separate request.

## Placement

The user keeps **one dedicated experiments repo**. Each idea is a new file or directory named after the idea (`<idea>.py`, `<idea>.cpp`, or `<idea>/`). All ideas share one environment. Do not create a per-idea project, venv, `pyproject.toml`, or CMake tree.

- If we are already in that repo, or the user has named it, or the current / an obvious sibling repo is clearly the experiments repo, use it.
- In that repo: add any new dependency to the **shared** environment; use the repo's top-level Makefile for C++/CUDA; after a successful run, commit to `master` (local). Do not open a branch or PR. Push only if asked, or if that is already how this repo is used.
- If no experiments repo is present, fall back to a scratch directory in the current repo (`scratch/<idea>/` or `.scratch/<idea>/`). Do not commit or push unless asked. Still do not scaffold a project.

Do not invent a second experiments repo.

## Defaults

- One file, or a few files in one idea directory. Reuse the existing shared env.
- Hardcode config. Print-debug is fine. Ugly is fine.
- No templates, CI, lint, formatters, type-check gates, packaging, config frameworks, or persistent test suites (a single assertion may *be* the success signal).
- No new abstractions, no unrelated refactor, no deploy.
- Do not commit or push in a product repo unless asked.

## Evidence and verdict

Report a runnable command, the observed output, and what was and was not validated. If you cannot run it, report the blocker; do not pretend.

A passing check only supports the claim it actually exercised. Random tensors going through a forward pass do not prove accuracy. A short KITTI clip with falling ATE does not prove a full SLAM system.

`VALIDATED` | `PARTIAL` | `INVALIDATED` | `BLOCKED`

Stop when the signal is observed, the assumption is clearly false, or you are blocked. A short `NOTES.md` is optional — use it only if shortcuts would otherwise be lost. A time box is optional; if one was agreed, stop when it ends and report partial learning.

Do not tidy a spike into a production project unless the user asks. Rewrite later under the normal skills.

## Language references

Load only what you need, when you need it:

| Work | Read |
| --- | --- |
| Python script, deps, notebooks | [python.md](references/python.md) |
| PyTorch / deep-learning experiment | [torch.md](references/torch.md) |
| CUDA / Triton / inline kernels | [cuda.md](references/cuda.md) |
| C++, Eigen, quick bindings | [cpp.md](references/cpp.md) |
| SLAM, trajectories, datasets | [slam.md](references/slam.md) |
| Go or Rust | [go-rust.md](references/go-rust.md) |

## Yield

While this skill is active, do not load `cpp-project-init`, `python-project-init`, `cpp-testing`, `python-testing`, `spec`, or `codebase-design`. Do not load `python-environments` to scaffold a new env; add packages to the shared experiments env, or use the current interpreter. If `counterweight` is already in play, stay on its Direct track.

`cpp` / `python` hubs: a spike is not "create a project". Do not route it to `*-project-init`.

A one-batch training check or a short-sequence SLAM prototype is a spike, not a formal campaign. Do not start `python-ml`'s full pipeline or `algorithm-experiment`'s ablation/seed log unless the user asked for that campaign. After the spike, those skills can take over.

## Prompt switch

The user can say **POC 模式**, **spike**, or `$spike`, or drop this into `AGENTS.md` / `CLAUDE.md`:

```
When the request is a disposable spike or quick POC, use the spike skill.
Put each idea in the experiments repo as <idea>.py or <idea>/, sharing that
repo's environment. Do not scaffold a project. Run it, report a verdict,
commit to master there. In any other repo, use a scratch dir and do not
commit unless asked.
```
