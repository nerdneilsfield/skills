// Project review / milestone review, 10-15 minutes. Reviewers want: status, evidence, risk, decision.
// Structure: one-line status -> progress vs plan -> risks -> asks. Put the decision you need on the last content slide.
#import "theme.typ": *

#show: jp-theme.with(
  config-info(title: [Project Atlas: Q4 review], subtitle: [Status, risks and decisions needed],
    author: [Project lead], institution: [Team name], date: datetime(year: 2026, month: 11, day: 5)),
  footer: [Atlas Q4 review | internal],
)

#title-slide()

== On track for the March launch, with one decision needed
#stats(height: 32%,
  stat("4 / 5", "milestones done"),
  stat("92%", "budget used on plan", color: jp.green),
  stat("1", "decision needed today", color: jp.vermilion),
)
#callout(title: "Decision", kind: "key")[Approve two extra engineers for January to protect the launch date.]

= Progress
== Four of five milestones landed; the data migration slipped two weeks
#let rag(c, t) = text(fill: c, weight: "bold", t)
#table(columns: (2.2fr, 1fr, 1fr, 2.5fr),
  [Milestone], [Plan], [Actual], [Status],
  [API v1], [Sep], [Sep], [#rag(jp.green)[Done]],
  [Auth service], [Oct], [Oct], [#rag(jp.green)[Done]],
  [Data migration], [Oct], [Nov], [#rag(jp.vermilion)[Late, 2 weeks]],
  [Pilot with 3 teams], [Nov], [Nov], [#rag(jp.green)[Done]],
  [Public beta], [Mar], [Mar], [#rag(jp.indigo)[Planned]],
)

== Pilot users finish the task twice as fast
#grid(columns: (1.3fr, 1fr), column-gutter: 1.5em,
  figure-slot("bar chart: task time before vs after, 3 pilot teams", height: 7cm),
  [
    - 3 teams, 24 users, 4 weeks
    - Median task time 12 min to 6 min
    - Two requests repeated: export and SSO
  ],
)
#source[Pilot telemetry, Oct 7 to Nov 4. Replace with your data.]

= Risks
== Two risks can move the launch; both have an owner and a date
#table(columns: (2.2fr, 1fr, 2.5fr, 1.2fr),
  [Risk], [Impact], [Mitigation], [Owner],
  [Migration of legacy accounts], [High], [Run in parallel for 2 weeks], [Name A],
  [Only 1 engineer knows billing], [Medium], [Pair and document by Jan], [Name B],
)

= Asks
== We ask for two engineers in January and a go/no-go on Feb 1
+ Approve two engineers for January (cost: 2 person-months)
+ Confirm go/no-go review on February 1
+ Nominate a security reviewer for the beta

#speaker-note[Finish by repeating the decision. Leave 3 minutes for discussion.]
