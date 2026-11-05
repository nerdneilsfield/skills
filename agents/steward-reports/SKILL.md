---
name: steward-reports
description: "Use when the host asks for a daily or weekly summary from the chronicle: read the project day records, the board, and the evidence coverage for a period, then write daily/<date>.md or weekly/<year>-W<week>.md. Not for refreshing the board or the day records (steward-board) or for distilling practices (project-learning)."
license: MIT
compatibility: Needs a chronicle directory populated by a host. No specific agent runtime is required.
metadata:
  author: DengQi
disable-model-invocation: true
---

# Steward the reports

Summarize a period from the same evidence the board is built on. The report file is the deliverable; pushing it anywhere is a separate, optional step and never the only delivery.

The chronicle directory, the minimal event and evidence fields, and the report paths are described in `references/chronicle-layout.md` of the `steward-board` skill. Read it before the first run; if that skill is not installed, tell the user to install it.

## Before writing

1. Fix the period and its boundaries. Day and week boundaries follow the device's local timezone, or `timezone` in `config.yaml` if set, never UTC.
2. Read the day records, `BOARD.md`, and the evidence coverage for the period.
3. Read the events the records claim, and the evidence behind them. Add git or token counts only when the host supplies them, and mark them as supplied rather than measured by you.
4. List the gaps in the period before writing anything. A gap is content, not a reason to shorten the report.

## Keep fact, suggestion, and gap apart

| Kind | Holds | Never |
| --- | --- | --- |
| Fact | What an event or evidence record shows | A guess about intent or cause |
| Result | What was finished, checked, or left failing | A result inferred from a plan |
| Suggestion | What someone might do next | Phrased as done, or as fact |
| Gap | Evidence that could not be read, or a period with no events | Silence, or "nothing happened" |

Next steps are always suggestions. Do not write a plan as if it happened.

## Write the report

Write to `daily/<date>.md` or `weekly/<year>-W<week>.md`, using the local date for the period, and overwrite the file on a re-run of the same period instead of appending.

```markdown
# <date> daily

Period: <start>..<end> (<IANA timezone>)
Coverage: <n> events, <n> evidence records. Gaps: <list, or "none">
Batch: <batch id or ids>

## Facts

## Results

## Blockers

## Evidence
- <evidence id> — <what it shows>

## Suggested next steps
```

Adapt the sections to the period; keep the fact/result/suggestion/gap separation. Keep it short enough to read in one sitting. One report file has one writer, so two runs must not write the same period at once.

## Gotchas

- UTC is not the day boundary. A report bucketed on UTC dates moves evening work to the wrong day.
- A gap is not "nothing happened". If evidence could not be read, say which record and since when.
- Do not let a suggestion read as a fact. Next steps stay under their own heading.
- Do not measure numbers yourself and present them as facts. Mark host-supplied figures as supplied.
- Re-running a period must overwrite the same file. Appending duplicates the period.
- A report is derived; do not edit the events, the evidence, the day records, or the board from here.
- The chronicle is private. Never copy its contents into a public repository, a skill, or a user-level file.

## Report

State the period and timezone, the files written, the coverage and gaps, and what you could not corroborate.
