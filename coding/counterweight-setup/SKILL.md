---
name: counterweight-setup
description: Initialize or update the current repository's root AGENTS.md so Counterweight is the sole default task workflow. Use when the user asks to enable, initialize, configure, or repair Counterweight project instructions.
---

# Counterweight Setup

Configure Counterweight in the current repository. This Skill edits project
instructions; it is not a task workflow.

## Request scope

For an inspection, discussion, or proposal-only request, report the intended
changes without writing files. A request to enable or initialize Counterweight
authorizes the setup below, including creating a missing root `AGENTS.md`.
Carry forward authorization already given in the conversation.

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

Counterweight is the sole task workflow for coding implementation and
modification tasks in this repository. Do not invoke or
combine it with engineering-change, planning, orchestration, or other workflow
skills unless the user explicitly names that additional skill.
```

Replace an older Counterweight setup block instead of appending a duplicate.
Remove duplicate copies of either required instruction. Do not rewrite or
delete unrelated project guidance.

When the user authorizes Counterweight as the sole task workflow, replace
instructions in the target file that directly require a competing default
workflow, including its mandatory routing or orchestration pipeline. This is
part of the authorized setup; do not ask for the same approval again. Preserve
independent project constraints such as safety boundaries, validation commands,
coding conventions, and collaboration rules, even when they share a section
with the conflicting workflow instructions.

If the request leaves replacement authority unclear, identify the exact
conflicting text and ask only about that unresolved choice before writing a
contradictory setup. Report conflicts in global or other out-of-scope files
without modifying them. Do not combine workflows merely to perform this setup.

## Verify

Before finishing:

1. Confirm the target is the intended repository root `AGENTS.md`.
2. Confirm both required instructions appear exactly once.
3. Confirm unrelated content remains intact.
4. Confirm no competing default workflow remains in the target file after an
   authorized replacement; repeating setup should make no further changes.
5. Report the file created or updated, any workflow rules replaced, and any
   unresolved conflict. For inspection-only requests, report findings only.
