# Counterweight Skills

## Source of truth

Do not restate these concepts elsewhere. Link here, then to the authority.

| Concept | Authority | Other files may |
| --- | --- | --- |
| Four earn rules | [SKILL.md](SKILL.md) | cite, not restate |
| Implementation ladder | [SKILL.md](SKILL.md) | cite |
| Track definitions and selection | [SKILL.md](SKILL.md) | cite |
| Authorization | [SKILL.md](SKILL.md) | cite |
| Commit grouping and timing | [references/commits.md](references/commits.md) | SKILL.md: four bullets + link |
| Check choice and permanent vs session-only tests | [references/feedback.md](references/feedback.md) | SKILL.md: four-line list + link |
| Deep plan contract | [references/deep.md](references/deep.md) | cite |
| Setup text written into AGENTS.md | [../counterweight-setup/SKILL.md](../counterweight-setup/SKILL.md) | never inline in any README |

This package contains five discoverable Skills:

- `counterweight`: default restraint and evidence policy for coding work.
- `counterweight-setup`: initializes or updates root `AGENTS.md`.
- `counterweight-cut`: user-invoked cut list for work that did not earn staying.
- `grill-me`: user-invoked pressure testing of material decisions.
- `project-learning`: conditional persistence of durable project knowledge.

Install them from this repository with Skills CLI:

```bash
npx skills add nerdneilsfield/skills --skill counterweight
npx skills add nerdneilsfield/skills --skill counterweight-setup
npx skills add nerdneilsfield/skills --skill counterweight-cut
npx skills add nerdneilsfield/skills --skill grill-me
npx skills add nerdneilsfield/skills --skill project-learning
```

`counterweight` works when installed alone. `counterweight-cut`, `grill-me`,
and `project-learning` are optional and user-invoked. Setup does not install
cut as part of the default workflow. Run `$counterweight-setup` to write the
project's root `AGENTS.md`; the exact text lives in that skill.

No hook or router is required; actual automatic invocation depends on the
host's Skill support.

Direct handles bounded edits without planning overhead. Managed coordinates
dependent edits. Deep uses an executable plan; see
[Deep planning and execution](references/deep.md). Verification, commits, and
authorization follow [SKILL.md](SKILL.md).

Evals: [evals/core.jsonl](evals/core.jsonl) for the main skill,
[evals/suite.jsonl](evals/suite.jsonl) for optional companions including cut,
[evals/baseline.md](evals/baseline.md) for the YAGNI comparison.
