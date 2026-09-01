# Counterweight Skills

This package contains three discoverable Skills:

- `counterweight`: default restraint and evidence policy for coding work.
- `grill-me`: decision-only clarification.
- `project-learning`: conditional persistence of durable project knowledge.

Install them from this repository with Skills CLI:

```bash
npx skills add nerdneilsfield/skills --skill counterweight
npx skills add nerdneilsfield/skills --skill grill-me
npx skills add nerdneilsfield/skills --skill project-learning
```

To reinforce default use in a project, add one line to its `AGENTS.md`:

```text
Use $counterweight by default for coding implementation and modification tasks.
```

No hook or router is required; actual automatic invocation depends on the host's Skill support.
