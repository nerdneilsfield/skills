// Technical sharing / internal tech talk, 20-40 minutes.
// Structure: problem -> options -> chosen design -> how it works (diagram, code) -> measured result -> trade-offs -> takeaways.
#import "theme.typ": *
#import "@preview/fletcher:0.5.8" as fletcher: diagram, node, edge

#show: jp-theme.with(
  config-info(title: [Moving our job queue from polling to events], subtitle: [Tech talk],
    author: [Your Name], institution: [Team], date: datetime(year: 2026, month: 11, day: 5)),
  footer: [Job queue talk],
)

#title-slide()

== Polling cost us 30% of database load for no work
- 400 workers poll every 500 ms
- 92% of polls return nothing
- Tail latency spikes when polls pile up
#speaker-note[Open with the symptom the audience has felt. Ask who has seen the p99 spikes.]

== We compared three options and picked events
#table(columns: (1.4fr, 1fr, 1fr, 1fr),
  [Option], [Latency], [Complexity], [Verdict],
  [Faster polling], [Low], [Low], [Raises load],
  [Message broker], [Low], [High], [New dependency],
  [DB notify + events], [Low], [Medium], [#text(fill: jp.green, weight: "bold")[Chosen]],
)

== Workers wait for a notification and fall back to polling once a minute
#align(center, diagram(
  node-stroke: 1pt + jp.indigo, node-fill: jp.indigo-fill, node-inset: 8pt, spacing: (5em, 4em),
  node((0, 0), [Producer]), edge("-|>", [insert]),
  node((1, 0), [Database]), edge("-|>", [notify], label-side: right),
  node((2, 0), [Worker], stroke: 1.5pt + jp.vermilion, fill: jp.vermilion-fill),
  edge((2, 0), (1, 0), "-|>", bend: 60deg, [claim row]),
))

== The claim step is one atomic statement
```sql
UPDATE jobs SET state = 'running', worker = $1
WHERE id = (
  SELECT id FROM jobs WHERE state = 'ready'
  ORDER BY priority, id LIMIT 1 FOR UPDATE SKIP LOCKED
) RETURNING *;
```
Two workers can never claim the same row.

== Database load fell 28% and p99 latency fell from 900 ms to 140 ms
#stats(
  stat("−28%", "database CPU", color: jp.green),
  stat("140 ms", "p99 job pickup (was 900 ms)"),
)
#source[Production metrics, 7 days before and after. Replace with your data.]

== What we gave up: notifications can be lost, so the fallback stays
#callout(title: "Trade-off", kind: "warn")[A dropped notification delays a job by up to 60 s. We accepted this because the fallback poll bounds it.]

#focus-slide[Events for speed, a slow poll for safety.]
