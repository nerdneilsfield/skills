---
name: steward-board
description: "Use when a host hands over a batch of chronicle events and evidence to refresh the private board: rewrite BOARD.md and the affected project day records, keep batch, evidence, and gap ids, then advance the watermark. Also for a read-only status query against the board. Not for writing daily or weekly reports (steward-reports) or for distilling practices (project-learning)."
license: MIT
compatibility: Needs a host that writes event and evidence files into a chronicle directory. No specific agent runtime is required.
metadata:
  author: DengQi
disable-model-invocation: true
---

# Steward the board

Turn recorded events into the current project state. You write derived files only. The raw events and evidence are append-only and are not yours to edit.

Input is files in the chronicle directory. How they were collected is the host's business, and the events may come from any tool. Read [the chronicle layout](references/chronicle-layout.md) for the directory, the minimal event and evidence fields, the watermark, and the private-data rule.

## Pick the mode first

- **Consume a batch** — update `BOARD.md` and the affected `projects/<project-id>/<date>.md`, then advance the watermark. This writes, so it needs an explicit or scheduled call.
- **Answer a query** — read the board and the day records and answer. Change nothing: no file writes, no watermark move.

A question is never a batch. Decide the mode from the request before touching anything.

## Consume a batch

1. Read the consumer's watermark in `state/` and take the events after it. Do not re-process an earlier batch unless that run failed.
2. Drop duplicates first. The event `id` is the dedupe key; a repeated event counts once. `turn` is not an identity.
3. Bucket each event into a day by the device's local timezone, or `timezone` in `config.yaml` if set, not by the UTC timestamp. Keep the stored time in UTC.
4. For each affected project, rewrite its day record: what happened, the evidence ids behind it, and any gap.
5. Rewrite `BOARD.md`: project state, recent progress, next steps, blockers, update time, collection coverage, and evidence links.
6. Only after every derived file is written, advance the watermark past the last consumed event.

Carry the batch id, the evidence ids, and the gaps into the derived files. If any step fails, leave the watermark where it was and re-run the same batch.

## Keep fact, suggestion, and gap apart

Write the three apart and label them.

| Kind | Holds | Never |
| --- | --- | --- |
| Fact | What an event or evidence record shows | A guess about intent or cause |
| Suggestion | What someone might do next | Phrased as done, or as fact |
| Gap | Evidence that could not be read, or a period with no events | Silence, or "nothing happened" |

A gap is a result. Name what is missing and since when. Never let a missing evidence record read as a negative outcome.

## Say when the state is stale

Every board entry carries the time it was last updated and the coverage it rests on. When the newest event is older than the configured coverage interval, say the state is stale and name the gap. Do not present a stale board as current, and do not fill the gap by inference.

## One writer per file

Each derived file has one publisher. Do not let two runs write `BOARD.md` or the same day record. Serialize per project. If another writer holds the file, stop and report instead of merging.

## Gotchas

- Advancing the watermark before the derived files are written loses the batch when a later step fails. Write first, advance last.
- The day bucket is local; the stored time is UTC. Bucketing on the UTC date moves evening work to the wrong day.
- Duplicate events are normal: retries and overlapping handlers produce them. Count each `id` once, and do not add per-event counters twice.
- A gap is not an absence of work. An unreadable record, a missing turn, or a silent period is a gap to report, not a blank.
- A suggestion written in the same voice as a fact will be read as a fact. Keep the labels.
- A read-only query that writes is a bug. It moves the watermark or rewrites the board to answer a question.
- Do not invent a project id for an unmapped workspace. Leave it unmapped and surface it; the mapping is the user's.
- `.cw/HISTORY.md` is a rewritten summary, not a complete run log. Do not treat it as coverage.
- The chronicle is private. Never copy its contents into a public repository, a skill, or a user-level file.

## Report

State the batch id and range, the events consumed and deduplicated, the files written, the watermark's new position, and every gap.
