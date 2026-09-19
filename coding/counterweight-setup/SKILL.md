---
name: counterweight-setup
description: Enable Counterweight or repair its setup in a repository's root AGENTS.md.
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
## Counterweight

Coding implementation and modification tasks follow these rules:

1. Do not add an abstraction, dependency, config knob, fallback, retry, cache,
   or compatibility layer without a current requirement, a reachable caller, or
   an observed failure.
2. Do not write a plan, design document, or task list for work whose correct
   diff is already apparent.
3. Do not add a permanent test unless the behavior deserves future protection
   and its expected result comes from outside the implementation.
4. Do not put throwaway scripts, reproducers, or fixtures in the project's test
   tree. Use /tmp or an uncommitted scratch path.
5. Do not drop a security, accessibility, data-loss, or trust-boundary guard in
   pursuit of a smaller diff.

These rules yield to an explicit user request for more process. Language and
framework skills may be combined with them freely. Do not enable a general
planning or orchestration workflow by default.
```

Replace an older Counterweight setup block instead of appending a duplicate.
Remove duplicate copies of the required section. Do not rewrite or delete
unrelated project guidance.

When the user authorizes this setup, replace instructions in the target file
that directly require a competing default planning or orchestration workflow,
including its mandatory routing pipeline. Do not replace language or framework
skills, or independent project constraints such as safety boundaries,
validation commands, coding conventions, and collaboration rules, even when
they share a section with the conflicting workflow instructions. This is part
of the authorized setup; do not ask for the same approval again.

If the request leaves replacement authority unclear, identify the exact
conflicting text and ask only about that unresolved choice before writing a
contradictory setup. Report conflicts in global or other out-of-scope files
without modifying them.

## Development entry points

During authorized setup, add or update a short development navigation section
only when the root guidance lacks useful entry points. Use a bounded inspection
of existing project documentation and configuration to verify each reference.
Point readers to the relevant build/run/check instructions, architecture
guidance, and formatter or representative code conventions, with a brief
indication of when each is useful. Reuse existing navigation when sufficient.

Make reading conditional on the task; do not require the entire documentation
set before every edit. Prefer links to existing sources of truth over copied
commands or manuals. Do not invent paths, commands, conventions, or claims that
tests are isolated or safe. Missing documentation does not authorize creating a
development manual, changing tooling, or expanding beyond the target file.
Omit unverified entries and report a material missing entry point when useful.

For an explicit request to repair or clean up project instructions, inspect the
target file for obsolete blanket reading requirements, duplicate checks, and
repeated approval gates. Revise them only within the requested scope and with
supporting evidence, preserving real safety and validation requirements.
Ordinary enablement authorizes the workflow conflict handling above and
verified navigation, not a rewrite of all project rules; report other concerns
without changing them.

## Verify

Before finishing:

1. Confirm the target is the intended repository root `AGENTS.md`.
2. Confirm the required Counterweight section appears exactly once.
3. Confirm unrelated content remains intact.
4. Confirm no competing default planning or orchestration workflow remains in
   the target file after an authorized replacement; repeating setup should
   make no further changes. Language and framework skills may remain.
5. Report the file created or updated, any workflow rules replaced, and any
   unresolved conflict. For inspection-only requests, report findings only.
6. Confirm navigation references exist, explain when to use them, and do not
   duplicate existing guidance or impose unconditional reading.
