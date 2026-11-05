---
name: code-reading
description: "Use when reading an unfamiliar repository or a large module: build a map from the entry point through the data flow to the core loop, using a code graph or index when one is available and literal search otherwise, and report conclusions with file:line while keeping what you read separate from what you inferred. Not for reviewing a specific change (code-review) or redesigning a module (codebase-design). Not for checking an implementation against a paper (paper-to-code) or for making a requested change."
license: MIT
compatibility: Uses tokei, rg, fd, git, and gh; ast-grep, rga, and any semantic or graph index are optional and detected at runtime.
metadata:
  author: DengQi
---

# Read a repository you have never seen

The output is a map plus a list of things you verified and things you only suspect. A summary with no `file:line` is a guess.

## 1. Size the repository before reading it

```sh
tokei --output json . | jq 'to_entries | sort_by(-.value.code) | .[0:10] | map({(.key): .value.code})'
fd -t d -d 2 . | head -40
```

Then find the entry points: the CLI, the server, the main, the test suite, the build files. Read the build file first; it names the real entry points and the dependencies.

## 2. Build a map, not a summary

Prefer a code graph or semantic index when one is installed: build or refresh the index, then query the call path from the entry point and the neighbourhood of the core type. Their subcommands follow their own documentation; the capability is call-path and impact queries over an indexed repository. When no index is available, map with `rg` and `ast-grep`:

```sh
rg -n '^(def|class) ' src/ | head -50
ast-grep run -p 'def $F($$$ARGS): $$$B' -l python src/
rg -n 'import|from ' --type py src/ | head -30
```

Write the map as a file, so it survives a new session:

```markdown
# Map: <repo> @ <commit>

## Entry points
- <file:line> — <what starts here>

## Data flow
<source> -> <transform> -> <store> -> <output>, each with file:line

## Core loop
<file:line> — what repeats, and what ends it

## Boundaries
<config, IO, network, GPU>, each with file:line

## Unread
- <what you did not open>
```

## 3. Follow the data, not the directory tree

Directory names lie. Follow one real input from where it enters to where it is stored, reading each function it passes through. The core loop is usually where the data is transformed repeatedly; find it by looking for the hot call site, then confirm with a profile or a benchmark rather than by guessing.

## 4. Use history to explain the shape

```sh
git log --oneline -20 -- src/core.py
git blame -L 40,60 --date=short src/core.py
git log --oneline -S 'feature_flag' -- src/
```

A blame line names the last change, not the author of the logic. A pickaxe hit tells you when a symbol appeared, which often explains a workaround that reads as a mistake.

## 5. Keep read and inferred apart

Tag every statement. **Read** means you opened the file and can cite `file:line`. **Inferred** means you concluded it from naming, structure, or convention. Put the inferred items in their own list and say what would confirm each.

## Gotchas

- A repository with a graph or semantic index still needs the source read. The index gives leads; cite `file:line` after opening the file.
- A stale index answers about an old commit. Check the index time or rebuild it, and say which commit you mapped.
- `tokei` counts generated files and vendored dependencies. Exclude them, or the size ranking is wrong.
- The directory named `core` is often not where the work happens. Confirm by following an input.
- `git blame` shows the last touch, not who wrote the logic. A formatting commit can own every line.
- A large function is not necessarily the core loop; find the loop by what repeats at runtime, not by line count.
- An empty search result is about your pattern, not the code. Loosen the pattern before concluding a thing does not exist.
- A README describes intent, not behavior. The code is the truth; cite it.
- Do not summarize a module you have not opened. Say what you did not read.

## Report

State the commit read, the map with `file:line` for every claim, the data flow and the core loop, what you verified against the source, what you only inferred, and what you did not read.
