---
name: counterweight-setup
description: Initialize or update the current repository's root AGENTS.md so Counterweight is the sole default task workflow. Use when the user asks to enable, initialize, configure, or repair Counterweight project instructions.
---

# Counterweight Setup

Configure Counterweight in the current repository. This Skill edits project
instructions; it is not a task workflow.

## Target

Resolve the repository root from the current project context or Git. Edit only
the root `AGENTS.md` unless the user explicitly names another file or scope.

- If the file does not exist, create it.
- If it exists, preserve unrelated instructions and formatting.
- Do not edit global or user-level agent configuration.
- Do not create nested `AGENTS.md` files unless the user explicitly requests
  narrower scope.

## Required Instructions

Ensure the root `AGENTS.md` contains a short `Counterweight` section with these
instructions exactly once:

```text
Use $counterweight by default for coding implementation and modification tasks.

Counterweight is the sole task workflow in this repository. Do not invoke or
combine it with engineering-change, planning, orchestration, or other workflow
skills unless the user explicitly names that additional skill.
```

Replace an older Counterweight setup block instead of appending a duplicate.
Remove duplicate copies of either required instruction. Do not rewrite or
delete unrelated project guidance.

If an existing instruction directly requires another default task workflow,
identify the conflicting text and ask the user before changing it. Still do not
combine workflows merely to perform this setup.

## Verify

Before finishing:

1. Confirm the target is the intended repository root `AGENTS.md`.
2. Confirm both required instructions appear exactly once.
3. Confirm unrelated content remains intact.
4. Report the file changed and any unresolved conflict.
