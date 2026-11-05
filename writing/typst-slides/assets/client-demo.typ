// Client demo / customer pitch, 10-20 minutes. Audience cares about their problem, proof, and next step.
// Structure: their problem -> what changes -> live demo cue -> proof -> terms -> next step.
// Confidentiality: set `confidential` below; never paste another customer's name, data, or logo without written permission.
// Logos: both are placeholders (dashed boxes). Replace with image("client-logo.svg", height: 1.4em) once you have cleared files.
#import "theme.typ": *

#let confidential = [Confidential: prepared for Client Name. Do not forward.]

#show: jp-theme.with(
  config-info(title: [Cut invoice processing from days to hours], subtitle: [Proposal for Client Name],
    author: [Presenter, Your Company], date: datetime(year: 2026, month: 11, day: 5)),
  footer: confidential,
  logo: stack(dir: ltr, spacing: 1em, logo-slot(label: "YOUR LOGO"), logo-slot(label: "CLIENT LOGO")),
)

#title-slide()

== Your team spends 3 days per cycle on manual invoice checks
#stats(
  stat("3 days", "per month-end cycle (from your interviews)", color: jp.crimson),
  stat("12%", "of invoices need rework", color: jp.vermilion),
)
#source[Client workshop, October. Replace with figures the client has confirmed.]

== Checks run automatically and only exceptions reach a person
#grid(columns: (1fr, 1fr, 1fr), column-gutter: 1em,
  callout(title: "1. Read", kind: "note")[Invoices are read from email and PDF],
  callout(title: "2. Check", kind: "note")[Rules match PO and contract],
  callout(title: "3. Review", kind: "key")[Only mismatches go to your team],
)

== Demo: one invoice from inbox to approval
#figure-slot("screenshot of the live demo, with a one-line caption", height: 7cm)
#speaker-note[Switch to the live system. Backup: recorded video on the desktop. Keep it under 4 minutes.]

== A comparable customer cut processing time by 70% in 8 weeks
#stats(
  stat("−70%", "processing time", color: jp.green),
  stat("8 weeks", "to go live"),
)
#source[Reference customer, shown with permission. Remove if permission is not in writing.]

== Pilot in 6 weeks, then a decision with real numbers
#table(columns: (1fr, 2fr, 1fr),
  [Week], [What happens], [Your effort],
  [1-2], [Connect mailbox, load rules], [2 days],
  [3-5], [Run in parallel with your team], [1 day / week],
  [6], [Review results and decide], [Half a day],
)

== Next step: nominate a pilot owner by Friday
+ Name a pilot owner on your side
+ We send the data-processing agreement for legal review
+ Kick-off call the week after

#focus-slide[Three days to three hours. Let us prove it on your data.]
