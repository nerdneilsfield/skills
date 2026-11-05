// Research talk / group meeting, 15-20 minutes, about 12-15 slides.
// Structure: claim -> why it matters -> idea -> evidence -> limits -> ask.
// Replace every sentence; keep titles as full-sentence claims. Compile: typst compile research-talk.typ
#import "theme.typ": *
#import "@preview/fletcher:0.5.8" as fletcher: diagram, node, edge

#show: jp-theme.with(
  config-info(
    title: [Caching keys cut decoding latency by 40%],
    subtitle: [Group meeting, week 45],
    author: [Your Name], institution: [Your Lab], date: datetime(year: 2026, month: 11, day: 5),
  ),
  footer: [Caching keys | group meeting],
)

#title-slide()

== The claim: same accuracy, 40% lower latency
#stats(
  stat("−40%", "median decode latency"),
  stat("±0.1", "accuracy change (n = 5 seeds)", color: jp.green),
)
#speaker-note[State the result first. Say the one number, then promise to show where it comes from. 1 min.]

= Problem
== Decoding is memory-bound, so batch size stops helping at 32
#grid(columns: (1.5fr, 1fr), column-gutter: 1.5em,
  [
    - Latency grows linearly past batch 32
    - GPU compute stays below 30% busy
    - The same reads repeat on every step
    #v(0.5em)
    #callout(title: "Question", kind: "key")[Can the repeated reads be skipped without changing outputs?]
  ],
  figure-slot("line chart: latency vs batch size", height: 6cm),
)

= Method
== Reusing the key tensors removes the repeated reads
#align(center, diagram(
  node-stroke: 1pt + jp.indigo, node-fill: jp.indigo-fill, node-inset: 8pt, spacing: (3em, 2em),
  node((0, 0), [Input]), edge("-|>"),
  node((1, 0), [Encoder]), edge("-|>"),
  node((2, 0), [Key cache], stroke: 1.5pt + jp.vermilion, fill: jp.vermilion-fill), edge("-|>"),
  node((3, 0), [Decoder]),
  edge((3, 0), (2, 0), "-|>", bend: 40deg, label: text(0.6em)[reuse], stroke: jp.vermilion),
))
- #alert[One change]: the cache is read-only after the encoder
- Outputs stay identical, so no retraining

= Results
== Latency drops at every batch size
#table(columns: (2fr, 1fr, 1fr, 1fr), align: (left, right, right, right),
  [Setting], [Baseline (ms)], [Ours (ms)], [Change],
  [Batch 8], [41], [33], [#text(fill: jp.green)[−20%]],
  [Batch 32], [118], [74], [#text(fill: jp.green)[−37%]],
  [Batch 64], [236], [141], [#text(fill: jp.green)[−40%]],
)
#source[Own measurements, one GPU, 5 runs each. Replace with your data.]

== Without the cache, the gain disappears
#callout(title: "Ablation", kind: "note")[Remove the cache: −40% becomes −3%. The rest of the pipeline is not the source of the gain.]

= Limits and next steps
== It does not help below batch 8, and one task regresses
- Small batches are compute-bound: no gain
- Task B loses 0.4 points; cause not yet known
- Next: test on longer sequences (two weeks)

#focus-slide[Reuse the keys, keep the outputs, cut the latency.]

#show: appendix
= Backup
== Backup: full table and setup
Hardware, seeds, and the full result table go here.
