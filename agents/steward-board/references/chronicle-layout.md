# The chronicle directory

The chronicle is a private directory of files. A host writes events and evidence into it; the steward skills read them and write derived files back. Nothing here is tied to a particular agent runtime or collector, and no command in this reference names one.

**Default location:** `~/.agents/chronicle/`. A host may point elsewhere; read its configuration before assuming the default.

**This directory is private.** It holds raw session records, paths, and outcomes. Never copy its contents into a public repository, a skill, a reference, or a user-level instruction file. Derived files stay private too.

## Layout

```text
<chronicle>/
  projects.yaml                 # workspace -> project id mapping
  config.yaml                   # host settings (timezone, coverage interval, consumers)
  events/<machine>/<event-id>.json
  evidence/<machine>/<record-id>.json
  state/                        # consumption watermark, one file per consumer
  BOARD.md                      # steward-board writes
  projects/<project-id>/<date>.md
  daily/<date>.md               # steward-reports writes
  weekly/<year>-W<week>.md
  memory/PRACTICES.md           # confirmed global practices
```

Event and evidence files are JSON, one object per file, UTF-8. An id is unique within its directory and never reused. Raw events and evidence are append-only: a steward reads them and never edits or deletes them.

## Minimal event fields

The host writes one file per event, named `<event-id>.json`.

| Field | Required | Meaning |
| --- | --- | --- |
| `id` | yes | Unique event id. The only dedupe key. |
| `time` | yes | When it happened, ISO 8601, **UTC** (`2026-11-05T13:07:14Z`). |
| `machine` | yes | Which machine produced it. |
| `agent` | yes | Which agent or session. |
| `workspace` | yes | Absolute path of the working directory. |
| `outcome` | yes | `ok`, `failed`, `cancelled`, or `unknown`. |
| `project` | no | Project id from `projects.yaml`; `null` when unmapped. |
| `turn` | no | Runtime turn id. May be `null` or repeated; **never** an identity. |

A missing or repeated `turn` is normal and must not change how the event is counted.

## Minimal evidence fields

The host writes one file per evidence record, named `<record-id>.json`.

| Field | Required | Meaning |
| --- | --- | --- |
| `id` | yes | Unique record id. |
| `event` | yes | The `id` of the event it supports. |
| `time` | yes | When it was captured, ISO 8601 UTC. |
| `source` | yes | The tool or artifact it came from. |
| `text` | one of | The captured content, when it is short and safe to store. |
| `pointer` | one of | A path or URL to the content, when it is not stored inline. |
| `gap` | one of | Why the evidence could not be captured. |

An evidence record with `gap` is how a gap is recorded. Do not omit the record: a missing file and a recorded gap mean different things, and only the recorded gap can be reported.

## Watermark

`state/` holds one watermark file per consumer (the board and the reports are separate consumers). Its exact shape is the host's, but it must answer: which events have already been consumed. A consumer advances it only after its derived files are written, so a failed run re-reads the same batch.

## Configuration the host supplies

Day and week buckets follow `timezone` in `config.yaml` when set, otherwise the device's local timezone. Times on disk stay UTC.

The rest are deliberately not fixed by the skills. Read them from `config.yaml` or ask the user; do not invent a default.

- **Coverage interval**: how often events are expected, so staleness can be stated.
- **Consumers and their names**: which watermark belongs to which skill.
- **Report push destination**: whether a report is sent anywhere beyond its file. Unset means file only.
- **Retention and remote**: how long raw records are kept and whether the directory is mirrored.

## Who writes what

| File | Writer |
| --- | --- |
| `events/`, `evidence/` | The host only. Append-only. |
| `state/` | The consuming skill, after its derived files are written. |
| `BOARD.md`, `projects/*/*.md` | `steward-board`. |
| `daily/*.md`, `weekly/*.md` | `steward-reports`. |
| `memory/PRACTICES.md` | `project-learning`, after the user confirms. Candidates wait in its pending list. |

One writer per file. Two runs must not write the same derived file at once.
