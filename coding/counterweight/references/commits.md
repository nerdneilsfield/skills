# Local commit contract

For authorized implementation, local commits are the default completion step in all tracks, subject to user instructions and host/repository policy. A review-only or plan-only request does not become an implementation request because this skill describes commits. Commit a plan-only artifact only when committing that artifact is authorized.

## Grouping and timing: all tracks

Use `/co-commit`'s grouping principles below in Direct, Managed, and Deep alike. These rules are self-contained; they do not require installing another skill or adding a separate approval step to already-authorized implementation.

- Group by user intent, dependencies, and review/rollback boundaries. Independently useful changes belong in separate commits; tightly coupled changes that deliver one behavior belong together.
- Keep implementation, necessary tests, and documentation for the same behavior together. Do not split by extension, file type, Conventional Commit type, or workflow track. Different modules usually separate only when their changes serve independent purposes; a cross-module feature may be one unit.
- Split one file by hunks only when ownership and dependencies are clear. Otherwise keep the coherent change together. Do not split merely to increase commit count, or combine unrelated tasks merely because both are small.
- Identify likely boundaries before editing and adjust them as the actual diff develops. Commit a unit immediately after its appropriate simple check passes, before moving to the next separable unit. This applies during execution, not just at final handoff.
- A useful intermediate stage can be committed while the larger task remains unfinished: for example, a runnable basic command before adding an independently useful option. One plan task may therefore have several commits. Conversely, combine dependent steps that cannot stand alone into one commit.
- Commit checkpoints do not justify extra tests or new work. Use the existing functional/runnability evidence for that unit. Do not make knowingly broken intermediate commits or knowingly commit a subset that depends on omitted working-tree changes.

## Exceptions

- Explicit "do not commit" / patch-only instruction: leave changes uncommitted and report that disposition. Do not keep asking.
- No Git repository: deliver verified files; do not initialize Git just to satisfy this contract.

## Procedure

1. Inspect Git status, staged and unstaged diffs, and recent same-module commit subjects. Identify task-owned paths/hunks and pre-existing changes. Follow explicit repository conventions first, then recent same-module style; use Conventional Commits only when established or as a fallback. Briefly state the next group's scope and reason before committing; reuse an existing plan when present instead of creating another artifact.
2. Verify the unit being committed. A check of the whole working tree is insufficient if the staged subset omits code needed to pass it; include the coherent dependency set or verify that subset separately.
3. Stage only known task-owned paths or hunks. Never use blanket staging (`git add .`, `git add -A`, `git commit -am`) or include unknown files. Preserve unrelated staged/unstaged user changes. If unrelated paths are already staged, use a path-scoped commit where safe; if ownership overlaps and cannot be isolated reliably, leave the index intact and report the commit blocker.
4. Inspect the exact candidate diff and check whitespace before committing. Commit only that unit, then inspect the resulting commit and Git status to confirm scope and remaining work.
5. Confirm the commit contains the intended unit and continue. Do not leave eligible verified work uncommitted without a reason.

If a hook or commit fails, inspect the cause and preserve the changes. Fix an in-scope issue and rerun affected verification before retrying. For missing identity, credentials, signing, or external tooling, report the exact blocker; do not change global Git settings, bypass hooks/signing, reset the index, or rewrite history to force completion. If a hook changes files, inspect and verify those changes before staging them.

Local commit permission never implies push, PR creation, merge, release, or deployment. Perform those only when separately authorized by the task or existing conversation.
