# Where each agent keeps memory

Checked 2026-11-05 against vendor docs unless marked. Products change quickly: confirm against the installed version before relying on a path.

## Contents

- Comparison table
- Conflict behavior
- Limits and traps by tool

## Comparison

| Tool | User layer | Project layer, shared | Project layer, private | Agent-written memory |
| --- | --- | --- | --- | --- |
| Claude Code | `~/.claude/CLAUDE.md`, `~/.claude/rules/` | `CLAUDE.md`, `.claude/rules/`, or `AGENTS.md` | `CLAUDE.local.md` (gitignored) | `~/.claude/projects/<project>/memory/`, per repository, machine-local |
| Codex | `~/.codex/AGENTS.md`, `AGENTS.override.md` | `AGENTS.md` | None documented | Generated under `$CODEX_HOME` (`memories/` or `memories_v2/`), opt-in, machine-wide |
| Gemini CLI | `~/.gemini/GEMINI.md` | `GEMINI.md`, subdirectory files | None documented | Experimental Auto Memory |
| Antigravity (secondhand sources) | `~/.gemini/GEMINI.md` | `.agents/rules/*.md` | Not confirmed | Knowledge Items |
| Grok Build (secondhand sources) | Not confirmed | `AGENTS.md` | Not confirmed | Opt-in, `/remember` and `/memory` |
| Cursor | User rules in settings | `.cursor/rules/*.mdc`, `AGENTS.md` | Not confirmed | Not confirmed |
| Copilot | User-level preferences | Custom instructions | None documented | Repository facts with citations, shared with repository users |

The Gemini CLI docs state it was replaced by Antigravity CLI on 2026-06-18. Check which one is installed.

## Conflict behavior

- Claude Code concatenates files rather than overriding: a conflict may resolve arbitrarily, so remove one side.
- Codex: the file closest to the working directory wins, and `AGENTS.override.md` replaces `AGENTS.md` at the same level. Sources for this are partly secondary.
- Cursor: Team over Project over User.

## Limits and traps

- Claude Code loads `AGENTS.md` only when no `CLAUDE.md` or `CLAUDE.local.md` exists at or above the working directory. For both, have `CLAUDE.md` import it with `@AGENTS.md`.
- Claude Code loads the first 200 lines or 25KB of the auto memory `MEMORY.md`, so it stays an index. Target under 200 lines per `CLAUDE.md`.
- Claude Code memory is not shared across machines, and a gitignored `CLAUDE.local.md` exists only in its own worktree.
- Codex stops reading `AGENTS.md` content at `project_doc_max_bytes` (32 KiB by default, from a secondary source).
- Codex memory files are generated state. Do not rely on hand edits to change behavior, and put required rules in `AGENTS.md`.
- Copilot expires memories after 90 days unless validated, and checks citations against the branch. Retrieval alone does not renew them.
- `~/.gemini/GEMINI.md` is reportedly shared by Gemini CLI and Antigravity, so a change affects both.
