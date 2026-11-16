# Python spikes

Default in the experiments repo: one script named after the idea, run in the **shared** uv/venv. Add dependencies to that env, not to a new project.

```text
experiments/
  pyproject.toml          # one shared env, already there
  uv.lock
  overfit_toy_ae.py       # a new idea = a new file
  pose_graph_tiny.py
```

```sh
uv add pillow             # add to the shared env, once
uv run python overfit_toy_ae.py
```

If the shared env already has the package, just run. Do not `uv init`, do not add `src/`, Ruff, ty, or pytest "for completeness".

## When there is no experiments repo

A single file with PEP 723 inline metadata, then `uv run --no-project` if a nearby `pyproject.toml` would otherwise get involved:

```python
# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy"]
# ///
print("ok")
```

```sh
uv run --no-project idea.py
```

This is the fallback, not the experiments-repo default. Official form: [PEP 723](https://peps.python.org/pep-0723/), runner: [uv scripts](https://docs.astral.sh/uv/guides/scripts/).

## Scripts vs notebooks

Prefer a script you can run with one command. Use a notebook only when the question is visual or exploratory and a script would hide the result.

- [marimo scripts](https://docs.marimo.io/guides/scripts/) can be run as a file (`marimo run` / `uv run` as the repo already does). Still one idea, one file, shared env. Do not add a notebook stack for a print-the-number check.
- Do not start Jupyter, papermill, or a results warehouse for a spike.

## Skip

`python-project-init`, `pyproject` per idea, CI, lint/type gates, packaging, CLI frameworks, `.env` layers, Docker.

## Success signal

`uv run python <idea>.py` (or the shared interpreter) exits 0 and prints the number, plot path, or assertion you named as the check.
