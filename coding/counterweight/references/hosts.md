# Running the roles on other hosts

Read this when the host is not pi, or pi has no `pi-counterweight` extension,
and the user wants a role from [roles.md](roles.md). Everything below was checked
on 2026-10-24 against the installed CLIs (codex, opencode 2.1.4, kimi 2.3.1,
grok 1.0.70) and the vendors' own hook and agent documentation. Flags and hook
formats change; run `--help` and check the doc for your version before relying
on one. Anything marked **unverified** was neither run nor found in the docs.
Nothing here was executed end to end: a hook script below is a documented shape,
not a tested one.

Two mechanisms are enough for every role:

1. **A read-only child run**: start the host's CLI once, non-interactively, with
   a read-only toolset, a role prompt, and a model. Pass the request and the
   diff in a file or on stdin, not on the command line. Read its final message.
2. **A before-tool hook**: a command the host runs before a tool call and that
   can refuse it. Needed only for PAUSE and for forcing.


## What each host gives you

| Host | Read-only child | Role as a profile | Refuse a tool call |
| --- | --- | --- | --- |
| pi | `pi --mode json --no-session --no-extensions --tools read,grep --system-prompt <file> -m provider/model -- @msg.md`. The planner uses `--no-tools`. | none, uses `--system-prompt` | needs an extension; without one, run roles by hand |
| codex | `codex exec -s read-only -m <model> --ephemeral "<prompt>"` | `~/.codex/agents/<name>.toml` with `sandbox_mode = "read-only"` and `developer_instructions` | a `PreToolUse` hook; see the hook note below |
| opencode | `opencode run --agent <name> -m provider/model --format json "<prompt>"` | an agent with `mode: subagent` and `permission` set to `deny` for `edit` and `shell` | a plugin hook: v2 `ctx.tool.hook("execute.before", ...)`, v1 `"tool.execute.before"`; see the opencode note |
| kimi code | `kimi -p "<prompt>" --agent-file <role.md> -m <model>`, with a `tools:` allowlist in the file | a Markdown file with frontmatter `tools:` (an allowlist) or `disallowedTools:`; the body is the prompt | a `[[hooks]]` entry in `~/.kimi-code/config.toml` with `event = "PreToolUse"`; exit 2 blocks, stderr is the reason |
| grok build | `grok -p "<prompt>" --tools "read_file,grep,list_dir" --output-format json` restricts the built-in tools only; MCP tools stay reachable (see the grok note) | `.grok/agents/*.md` or `~/.grok/agents/*.md` | a `PreToolUse` hook; see the hook note below |

Notes that matter:

- **codex.** `codex exec -s read-only` confines shell commands to a read-only
  sandbox. A `PreToolUse` hook can refuse a call
  with `permissionDecision: "deny"` and a non-empty reason, or by exiting 2 with
  the reason on stderr (the older `{"decision":"block","reason":...}` also
  works). `ask`, `approve` and `continue:false` are parsed but unsupported: the
  call proceeds and the hook is reported as failed. Hooks live in
  `~/.codex/hooks.json`, `~/.codex/config.toml`, `<repo>/.codex/hooks.json` or
  `<repo>/.codex/config.toml` (inline `[[hooks.PreToolUse]]`); the project layer
  loads only when that `.codex/` is trusted, and a new or changed hook is skipped
  until the user reviews it in `/hooks` (or the run passes
  `--dangerously-bypass-hook-trust`, which is for automation that already vets
  the hook). `PreToolUse` covers Bash, `apply_patch` (match `apply_patch`, `Edit`
  or `Write`), MCP and other local function tools. Input fields: `session_id`,
  `transcript_path`, `cwd`, `tool_name`, `tool_input`, `turn_id`.
- **opencode.** `opencode run --auto` approves every permission that is not
  explicitly denied, so a role that must not write needs `edit` and `shell` set
  to `deny`, not left at `ask`. The agent and permission fields were read from
  the installed binary's config schema. A plugin is a JS/TS module under
  `.opencode/plugins/` or `~/.config/opencode/plugins/` (or the `plugin` array
  in `opencode.json`) that returns a hooks object. This is the v1 shape: its
  `tool.execute.before` receives the tool name and arguments, can edit them, and
  throws to stop the call. The installed opencode is 2.1.4 (v2), where v1 plugin
  code does not run: a v2 plugin default-exports `Plugin.define({ id, setup(ctx) })`
  and registers `await ctx.tool.hook("execute.before", (event) => ...)`, where
  `event.tool` and `event.input` are the call. The v2 page shows inspecting and
  replacing the input there, and a permission hook (`ctx.permission.hook
  ("evaluate", ...)`) whose `event.effect` can be set to `deny`. **Unverified:**
  that throwing or denying from `execute.before` blocks a call in v2, and
  turn-end hooks. For a hard block in v2, use the permission hook, which is
  documented to deny.
- **kimi.** `--plan` is planning mode, not a verified write barrier; do not
  treat it as the read-only boundary. For a role that must read files, use an
  `--agent-file` with a `tools:` allowlist (for example `Read`, `Grep`, `Glob`;
  `tools: []` disables everything). `disallowedTools` applies after `tools`, and
  both are enforced again before a call runs. The built-in `explore` sub-agent
  is read-only and `plan` has no shell, but those are for the main agent to
  spawn, not for a `kimi -p` run. `--agent-file` takes one file. Hooks go in `~/.kimi-code/config.toml` as `[[hooks]]` with
  exactly `event`, `matcher`, `command`, `timeout` (an extra key makes the whole
  config fail to load). The script gets snake_case JSON on stdin; exit 0 allows,
  exit 2 blocks with stderr as the reason, any other exit, a crash or a timeout
  allows. Only `PreToolUse`, `Stop` and `UserPromptSubmit` can block. The docs
  say hooks should not be the only safety barrier.
  Do not combine `--agent`/`--agent-file` with `--session`/`--continue`.
- **grok.** Do not use `--permission-mode plan` as the read-only boundary: it
  auto-approves edits to the plan file, and plan mode does not inspect shell
  redirection. `--tools` with an allowlist narrows the **built-in** tools only;
  per its docs, "MCP meta-tools remain available unless denied", so a configured
  MCP server that can write is still reachable. The tool names in the table come
  from the docs' own example and may differ by version. If the user has
  write-capable MCP servers configured, this is not a read-only run: deny them
  with `--deny`, run it where none are configured, or do not call it read-only.
  The `read-only` capability mode applies to subagents the main agent spawns,
  not to a headless `-p` run. Hooks are JSON under `<project>/.grok/hooks/*.json` (project hooks
  need the folder to be trusted: `--trust` or `/hooks-trust`). The reply is
  `{"decision":"deny","reason":"..."}` on stdout. **Every hook failure is
  fail-open**: a crash, a timeout, or bad output does not block the call. Only
  an explicit deny does. That matches PAUSE (fail open) and does not match a
  hard guard.
- **Credentials.** A child run inherits the host's login. Do not put API keys in
  a role file or on a command line.

## Running a review

1. Write the request, then the diff, to a temp file outside the repo.
2. Run the host's read-only child with the role prompt from `roles.md` (copy the
   rules into the host's profile format; do not paraphrase their limits) and a
   model other than the implementer's.
3. Read the final message as [roles.md](roles.md) describes.

If both review and over_review were chosen, run them as two separate children.

**Check the boundary once per host, and know what the check cannot see.** Before
relying on a read-only child, start it and ask it to create a file in a temp
directory. If the file appears, the boundary is not real on this host, version,
and flags. If it does not appear, that shows only that local file writes are
blocked. It says nothing about shell redirection (where the host allows shell),
MCP tools, or network calls. List what the child can call and remove the rest.
A flag in a table is not evidence of a boundary.

## PAUSE without the extension

You need a before-tool hook that can read the transcript.

- **grok:** the hook input carries `transcript_path`, `session_id`, `tool_name`,
  `tool_input`.
- **codex:** the same fields, but `transcript_path` may be null and the docs say
  its format is not a stable interface. A script that parses it can break on an
  upgrade; pass the file's text through as-is rather than parsing it.
- **kimi:** the hook input has `session_id`, `cwd`, `tool_name`, `tool_input`.
  A transcript path is **unverified**; the session directory
  (`wire.jsonl`) holds the history but its use from a hook was not checked.
- **opencode:** a plugin hook can reach the session through its `client`; that
  was **not verified** in v2.

Without a hook, do it by hand: when you
reach the first source edit of a turn and the cause is still unclear, stop, put
the investigation and the intended edit into a child run with no tools and a
stronger model, read the plan, then continue. That is the same mechanism, run at
your own discretion, so it is weaker than a hook: nothing makes you stop.

Grok's hook timeout defaults to 5 seconds, so a hook that calls a model must
raise it explicitly.

## Forcing on another host

"Review at the end of every turn" needs a hook on the turn-end event.

- **grok:** verified in its docs. `Stop` fires when a turn genuinely completes
  (not on interrupt), its input carries `stopHookActive` and
  `lastAssistantMessage`, and a hook can block the stop to keep the agent
  working, with the findings as the reason. Check `stopHookActive`, or the loop
  never ends.
- **codex:** documented. `Stop` input carries `stop_hook_active` and
  `last_assistant_message`; returning `{"decision":"block","reason":"..."}` (or
  exit 2 with the reason on stderr) continues the turn, with the reason becoming
  a new user prompt. Plain-text stdout is invalid for `Stop`. Check
  `stop_hook_active` so it cannot loop.
- **kimi:** documented. `Stop` fires when the model is about to end the turn and
  can block, with a message appended so the model continues. A user interrupt
  fires `Interrupt` in its place, so `Stop` does not run then. The payload fields
  beyond the base ones were not read.
- **opencode:** `session.idle` is an event, not a blocking hook, and whether a
  plugin can start another turn from it was **not verified**.

Even where a Stop hook exists it is fail-open on grok and kimi (a crash or
timeout lets the turn end), so forced review there is best effort.
