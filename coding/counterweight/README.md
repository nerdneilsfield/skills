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
