---
name: tool-compose
description: "Use when choosing how to investigate a codebase or a corpus, or when a search comes back empty or noisy: route the question to a tool layer by type, fall back when a tool is missing, and compose the layers into one verified answer. Not for reviewing a change (code-review), designing a module (codebase-design), or reading an unfamiliar repository end to end (code-reading)."
license: MIT
compatibility: Assumes rg, fd, git, jq, tokei are present. ast-grep, rga, gh, uv, hyperfine, valgrind, pdftotext, and any semantic or graph index are optional and detected at runtime.
metadata:
  author: DengQi
---

# Route the question, then verify the answer

Pick the layer from the question, not from the tool you like. Every layer has a fallback, and the fallback is always `rg` plus reading the file.

Check availability before using an optional tool, and say what you fell back to:

```sh
for t in rg fd ast-grep rga gh jq tokei uv hyperfine valgrind pdftotext xerj; do
  command -v "$t" >/dev/null && echo "have $t" || echo "missing $t"
done
```

## The layers

| Question | Layer | Default | Fallback |
| --- | --- | --- | --- |
| Exact symbol, string, error text | Literal search | `rg` | `grep -rn` |
| Find files by name or path | File search | `fd` | `find` |
| Code shape: calls, assignments, definitions | Structural search | `ast-grep` | `rg` with a loose pattern |
| Text inside PDF, Office, archives | Corpus search | `rga` | `pdftotext` then `rg` |
| "Where is X handled?" when you lack the word | Semantic or hybrid search | a local semantic index, if installed | expand synonyms, then `rg` |
| Call chain, impact of a change | Code graph | a local code-graph tool, if installed | `rg` for the symbol, then read callers |
| Why the code looks like this | History | `git log`, `git blame`, pickaxe | read the file and ask |
| Library or API usage | Docs | a documentation MCP server | read the installed package's source |
| Run or measure | Runtime | `uv run`, `hyperfine`, `valgrind` | the project's own runner |

A semantic index is an MCP tool or CLI that builds a local index of the repository and answers meaning-based queries; XERJ is one. A code graph is a tool that indexes symbols and edges and answers call-path and impact queries; `codebase-memory-mcp` is one. Their exact subcommands follow their own documentation — the tool names and capabilities are known, the syntax was not run here.

## Compose the layers

Start literal, widen only when literal fails, then verify with literal:

1. `rg` for the exact term; `fd` if you are missing the file.
2. If nothing, expand synonyms and try again.
3. If still nothing and a semantic index exists, query it; otherwise `ast-grep` for the shape.
4. Take the candidate locations and confirm each by reading the source.
5. For impact, trace callers with `rg` or a graph tool, then confirm at the definition.

Verified pipelines:

```sh
# structured matches into a line list
rg --json 'os.path.join' src | jq -r 'select(.type=="match") | "\(.data.path.text):\(.data.line_number): \(.data.lines.text|rtrimstr("\n"))"'

# structural match, then read each hit
ast-grep run -p 'self.$A = $B' -l python --json src | jq -r '.[] | "\(.file):\(.range.start.line + 1): \(.text)"'

# how large is what you are about to read
tokei --output json . | jq '.Python.code'

# who last touched this line, and when
git blame -L 10,20 --date=short src/module.py

# when was this symbol introduced or removed
git log --oneline -S 'old_function' -- src/

# repository facts from the host
gh repo view owner/name --json name,stargazerCount,defaultBranchRef
```

## Truncate and verify

- Cap the output before it floods context: `rg --max-count 5 -n`, `| head -50`, or `jq '.[0:20]'`.
- Confirm a hit exists rather than trusting a count: read the line the tool reported.
- A search that returns nothing is a result about the pattern, not about the code. Loosen it before concluding absence.
- Run the command and paste what it printed. A command you did not run is a guess.

## Gotchas

- `ast-grep` exits 0 whether or not it matched, and also when the pattern is invalid. Gate on its output, not its exit code. `rg -q` exits 1 on no match, so the two disagree.
- An incomplete `def` pattern such as `def $F($$$ARGS)` parses to an ERROR node and matches nothing while printing a warning to stderr. Include the body: `def $F($$$ARGS): $$$B`.
- A metavariable in the receiver position (`$X.save($$$)`) may fail to parse in some versions. Use a literal receiver, or a YAML rule under `ast-grep scan`.
- `ast-grep scan` also exits 0 on findings; add `--error` to make findings fail the run.
- `perf` needs `perf_event_paranoid` privileges and is often blocked. Fall back to `hyperfine` for wall time or `valgrind --tool=callgrind` for counts.
- `hyperfine --export-json` nests the statistics under `.results[].summary.<time_wall_clock|time_cpu|memory_peak_resident>`. Read the shape with `jq 'keys'` before writing a path.
- `rg --json` emits several event types; a bare `.data.lines.text` yields nulls. Filter with `select(.type=="match")`.
- A semantic or graph index can be stale. Check its index time or rebuild before trusting it.
- A semantic or graph hit is a lead, not a conclusion. Confirm it by reading the source and cite `file:line`.
- Never install a tool without the user's agreement, and never send private code to a hosted embedding service.

## Report

State the layers used, the exact commands, which optional tools were missing and what you fell back to, and which findings you confirmed by reading the source.
