# Counterweight Skills

This package contains four discoverable Skills:

- `counterweight`: default restraint and evidence policy for coding work.
- `counterweight-setup`: initializes or updates root `AGENTS.md` so Counterweight is the sole default task workflow.
- `grill-me`: user-invoked pressure testing of material decisions.
- `project-learning`: conditional persistence of durable project knowledge.

Install them from this repository with Skills CLI:

```bash
npx skills add nerdneilsfield/skills --skill counterweight
npx skills add nerdneilsfield/skills --skill counterweight-setup
npx skills add nerdneilsfield/skills --skill grill-me
npx skills add nerdneilsfield/skills --skill project-learning
```

Run `$counterweight-setup` to configure a project's root `AGENTS.md`. It adds:

```text
Use $counterweight by default for coding implementation and modification tasks.

Counterweight is the sole task workflow in this repository. Do not invoke or
combine it with engineering-change, planning, orchestration, or other workflow
skills unless the user explicitly names that additional skill.
```

No hook or router is required; actual automatic invocation depends on the host's Skill support.

Direct handles bounded edits without planning overhead. Managed coordinates dependent edits. Deep uses an executable plan with exact targets, dependencies, acceptance checks, and a progress record; execution follows `task → run/check → commit`, then confirms the assembled feature works. No automatic reviewer pipeline is required. See [Deep planning and execution](references/deep.md).

Verification stays small in every track: confirm the code runs and the requested function works. Reuse existing checks or a simple smoke run; do not add permanent tests or rare-failure coverage without concrete evidence that they are needed. Deep adds execution discipline, not a larger test campaign.

Prioritize the first useful runnable version and real user feedback. TDD is optional, useful for a concrete problem or explicit request; imagined edge cases and agent-written tests that mirror the implementation must not delay delivery.

For implementation work in a Git repository, all tracks use `/co-commit`'s grouping principles: commit by task intent, dependencies, and review/rollback boundaries. Commit each verified coherent unit during execution, including useful intermediate stages; do not wait until the whole request is finished. Track selection does not determine commit count, and one task may produce several commits. Explicit no-commit instructions and host/repository restrictions take precedence. Commit scope excludes unrelated user changes; push, PR creation, merge, and release require their own authorization. See [commit contract](references/commits.md).
