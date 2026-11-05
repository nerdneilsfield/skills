// Teaching lecture / tutorial, 45-90 minutes; this skeleton is one 45-minute block.
// Structure: goal -> recall -> concept -> worked example -> try it -> summary. Alternate talking with doing every 10 minutes.
#import "theme.typ": *

#show: jp-theme.with(
  config-info(title: [Gradient descent in one hour], subtitle: [Lecture 3],
    author: [Instructor], institution: [Course name], date: datetime(year: 2026, month: 11, day: 5)),
  footer: [Lecture 3 | Gradient descent],
)

#title-slide()

== By the end you can run gradient descent by hand on a small problem
+ Explain why the update moves downhill
+ Choose a learning rate that converges
+ Spot divergence from a loss curve
#speaker-note[Read the three goals aloud. Say what you will not cover. 2 min.]

== Recall: the derivative tells us which way is up
#callout(title: "Quick check (1 min)", kind: "key")[If f'(x) = 3 at x = 2, which direction lowers f? Discuss with a neighbour.]

= Concept
== Each step moves against the slope by a small amount
$ x_(t+1) = x_t - eta f'(x_t) $
#pause
- $eta$ is the learning rate: the step size
- Small $eta$ is slow, large $eta$ can overshoot

= Worked example
== For f(x) = x², starting at x = 4 with η = 0.25, the point halves each step
#table(columns: (1fr, 1fr, 1fr), align: center,
  [Step], [x], [f(x)],
  [0], [4.00], [16.0],
  [1], [2.00], [4.0],
  [2], [1.00], [1.0],
)
#pause
#callout(kind: "good")[Each step multiplies x by 1 − 2η = 0.5.]

= Practice
== Your turn: what happens with η = 1.1?
#callout(title: "Exercise (5 min)", kind: "key")[Compute three steps from x = 4. Predict: converge, oscillate, or diverge?]
#pause
#callout(title: "Answer", kind: "note")[x goes 4, −4.8, 5.76: it grows. Any η above 1 diverges for this f.]

#focus-slide[Downhill steps, sized by the learning rate.]
