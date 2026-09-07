# Local commit contract

For authorized implementation, local commits are the default completion step in all tracks, subject to user instructions and host/repository policy. A review-only or plan-only request does not become an implementation request because this skill describes commits. Commit a plan-only artifact only when committing that artifact is authorized.

## Boundaries

- Direct: verify the bounded edit, then make one coherent commit.
- Managed: commit verified coherent units; one commit is enough when edits implement one behavior.
- Deep: use the plan's verified task boundaries, then commit integration fixes and final plan status. Do not make knowingly broken intermediate commits merely to match a task count.
- Explicit "do not commit" / patch-only instruction: leave changes uncommitted and report that disposition. Do not keep asking.
- No Git repository: deliver verified files; do not initialize Git just to satisfy this contract.

## Procedure

1. Inspect Git status, staged and unstaged diffs, and recent same-module commit subjects. Identify task-owned paths/hunks and pre-existing changes. Follow repository message conventions.
2. Verify the unit being committed. A check of the whole working tree is insufficient if the staged subset omits code needed to pass it; include the coherent dependency set or verify that subset separately.
3. Stage only known task-owned paths or hunks. Never use blanket staging (`git add .`, `git add -A`, `git commit -am`) or include unknown files. Preserve unrelated staged/unstaged user changes. If unrelated paths are already staged, use a path-scoped commit where safe; if ownership overlaps and cannot be isolated reliably, leave the index intact and report the commit blocker.
4. Inspect the exact candidate diff and check whitespace before committing. Commit only that unit, then inspect the resulting commit and Git status to confirm scope and remaining work.
5. Record the SHA in the Deep plan or final response. Do not leave eligible verified work uncommitted without a reason.

If a hook or commit fails, inspect the cause and preserve the changes. Fix an in-scope issue and rerun affected verification before retrying. For missing identity, credentials, signing, or external tooling, report the exact blocker; do not change global Git settings, bypass hooks/signing, reset the index, or rewrite history to force completion. If a hook changes files, inspect and verify those changes before staging them.

Local commit permission never implies push, PR creation, merge, release, or deployment. Perform those only when separately authorized by the task or existing conversation.
