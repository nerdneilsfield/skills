---
name: code-walkthrough
description: "Use when the user wants to see how a codebase works as an interactive page: an animated, step-through call flow with a layered explanation from overview to code. Produces one offline HTML file whose steps cite file:line. Not for a written map of a repository (code-reading), an architecture change (codebase-design), or a paper-to-code comparison (paper-to-code)."
license: MIT
compatibility: python3 builds the page; a browser views it. No network or build tools.
metadata:
  author: DengQi
---

# Turn a codebase into a page you can step through

The look is fixed by the template, so spend your effort on the content. Do not write your own HTML, and do not restyle the page unless the user asks. The result is one offline file.

## 1. Read before drawing

Use `code-reading` to find the entry points and trace real calls, at the pinned commit. Pick one to three questions a reader would ask, such as "what happens when a frame arrives?". A walkthrough of one real path beats a map of everything.

## 2. Write the data, shallow to deep

Save a JSON file with these fields:

| Field | Holds |
| --- | --- |
| `title`, `summary`, `repo`, `commit` | Plain words on what this code does, for someone who has never seen it |
| `overview`, `stages[]` | Level one: the big idea, then `{name, text}` for each stage, with no symbol names |
| `nodes[]` | Level two: `{id, label, layer, summary, file, line}`. At most 12. `layer` is an integer row, top to bottom in call order |
| `edges[]` | `{from, to, verified}`. Set `verified: false` on anything you did not read |
| `flows[]` | Level three: `{title, steps[]}`. Each step: `{from, to, title, explain, code, file, line, verified}`. `from` is `null` on the first step |
| `terms[]` | Optional `{term, meaning}` |

Each level assumes only the one above. `explain` says why this call happens, not what the line says. `code` is a short excerpt copied from the file, 12 lines at most. Write in the user's language.

[`assets/example.json`](assets/example.json) shows the shape.

## 3. Build and check

```sh
python3 scripts/build_walkthrough.py walkthrough.json walkthrough.html --repo /path/to/repo
```

Run it from this skill's directory. It refuses a missing file, a line out of range, an unknown node, a step without an edge, or a verified step with no file. Fix the data, not the check. Then open the page, or render it if you can, and step through every flow.

## Gotchas

- A plausible call you did not trace is the main risk. Mark it `verified: false`; the page draws it dashed.
- Dynamic dispatch, callbacks, and templates hide the real target from search. Confirm with a test, a debugger, or a trace, or mark it inferred.
- The validator proves a location exists, not that it shows that claim. Reread each excerpt against its `line`.
- Too many nodes turns the map into wiring. Merge helpers into their caller, and split a large system into several flows.
- Line numbers rot. Always record `commit`, and rebuild after a rebase.
- The page holds code excerpts. Do not publish one from a private repository without asking.

## Report

State the commit, the flows covered, how many steps are inferred, and the output path.
