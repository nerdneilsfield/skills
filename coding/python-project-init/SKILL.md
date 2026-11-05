---
name: python-project-init
description: "Use when the user asks to create a Python project or package, or to add pyproject.toml, src layout, Ruff, ty, or pytest configuration to one. Defer shared conventions to python and interpreter, lock, Conda, Pixi, and CUDA questions to python-environments. Not for ordinary source fixes or for changing the tooling of a project that already has working choices."
license: MIT
compatibility: Requires Python 3. Examples use uv; a project already on another tool keeps it.
metadata:
  author: DengQi
---

# Lightweight Python project initialization

Build the smallest project that can be installed, tested, and linted. Inspect first: an existing project keeps its layout, packaging tool, and supported Python versions unless the user asks to change them. A bug fix is not permission to initialize or migrate anything.

## Choose the shape

| Deliverable | Command |
| --- | --- |
| Script or service, never published | `uv init name` |
| Installable app with a command | `uv init --package name` |
| Library | `uv init --lib name` |

The last two give a `src/` layout, which stops tests from importing the working tree by accident. Add dependencies only for a current requirement.

## Minimal contract

```sh
uv init --package demo-app
cd demo-app
uv add --dev pytest ruff ty
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run ty check
```

Add this to `pyproject.toml`, with `tests/` beside `src/`:

```toml
[tool.pytest]
minversion = "9.0"
strict = true
addopts = ["--import-mode=importlib"]
testpaths = ["tests"]

[tool.ruff]
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP"]
```

Use Ruff for both linting and formatting, and ty for type checking. Do not add Black, autopep8, isort, or mypy alongside them. Add CI, pre-commit, and docs tooling only on request; each is another thing to keep working. Test design belongs to `python-testing`.

## Gotchas

- `uv init` sets `requires-python` from the interpreter it found, so a machine on the newest Python silently excludes every older one. Set the real minimum before publishing, or pass `--python`.
- The default build backend depends on the uv version: older uv writes `hatchling`, newer writes `uv_build`. Keep what was generated unless a build requirement says otherwise, and do not copy a `[build-system]` table from memory.
- Commit `uv.lock` for applications. For libraries it pins your development environment only; users resolve from your declared ranges.
- A distribution name uses hyphens and the import package uses underscores: `demo-app` imports as `demo_app`.
- Development tools go in `[dependency-groups]`, which is not published. Runtime needs placed there work locally and break for installers.
- `ruff format` conflicts with a few lint rules, such as `COM812`. Enabling `ALL` brings these in and creates churn; start from a short `select`.
- Do not pin exact versions in `[project.dependencies]` of a library. That forces conflicts on every consumer; pins belong in the lock file.

## Acceptance

Report the generated tree, the Python and uv versions used, the outcome of the test and lint commands, and what you did not set up. A new project that ships a command should also run under `uv run --isolated --no-editable <command>`, since an editable install hides missing package data.

## References

- [uv projects](https://docs.astral.sh/uv/concepts/projects/init/), [dependency groups](https://packaging.python.org/en/latest/specifications/dependency-groups/), [Ruff configuration](https://docs.astral.sh/ruff/configuration/), [src layout](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/).
