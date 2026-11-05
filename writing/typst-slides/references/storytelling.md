# Storyline and speaker script

Do this before any layout. The user approves the storyline and script; slides are built from them.

## 1. Fix the frame

Write four lines and get them confirmed: who is in the room and what they already know, what they must think or do afterwards (one sentence), how long you have, and what the Q&A will probe. A talk that cannot state its one sentence is not ready for slides.

## 2. Pick a spine

| Spine | Use when | Shape |
|---|---|---|
| Pyramid (answer first) | Reviews, client decisions, reports to leaders | Conclusion, then 2-4 supports, then evidence under each |
| SCQA | Opening of almost any talk | Situation (shared fact), Complication (what changed or hurts), Question (what follows), Answer (your claim) |
| Problem, idea, proof | Research talks, proposals | Gap, key insight, evidence, limits |
| Before, after, bridge | Pitches and demos | Today's pain, the changed state, how to get there |
| Explain, show, try | Teaching | Goal, concept, worked example, exercise, recap |

Pyramid principle in practice: each slide title is a claim, the slides under a section jointly prove the section's claim, and the sections jointly prove the opening claim. Read the titles in order; they should make a readable paragraph. If one title does not follow from the previous, the story has a hole there.

## 3. Storyline by scene

- Research talk or group meeting: result first (one number), problem and gap, idea, evidence including the ablation that shows why it works, limits, next steps. Spend at most 15% of the time on background.
- Project review: status in one line with a traffic-light, progress against plan, what changed since last time, risks with owner and date, the decision or help needed. Put the ask on the first content slide and again at the end.
- Defence or proposal: question, gap in the literature, contributions (numbered, three at most), method, results per contribution, limits, plan or publications. Reviewers read contributions closely, so each result slide names the contribution it supports. Keep backup slides for the questions you expect.
- Client demo: their problem in their words, what changes, a short live demonstration with a recorded fallback, proof from a comparable case, effort and terms, one concrete next step. Cut internal jargon; never show another customer's data.
- Technical sharing: symptom everyone felt, options compared, the design, how it works (diagram, then code), measured result, what you gave up, takeaways.
- Teaching: goals, recall, concept, worked example, student task, recap. Alternate telling and doing about every ten minutes.

## 4. Slide inventory

List every slide as a row, one idea each.

| # | Assertion title (full sentence) | Evidence (figure, table, number, source) | Time | Speaker script |
|---|---|---|---|---|

Titles state what the audience should conclude ("Latency halves at batch 64"), not the topic ("Results"). A slide with two ideas becomes two slides. Allow about one slide per minute for content slides and less for dense figures; section dividers and title are free. A 15-minute talk is 10-14 slides plus backup.

## 5. Write the script

For each slide write what you would say in the order you would say it, in short sentences, with the transition into the next slide. Mark numbers you must state exactly. Put it into `#speaker-note[...]` after the slide. Rehearse aloud once and keep the total under the time limit with a margin of about 10%; cut slides before speeding up.

## 6. Ownership of the text

The agent drafts from the user's material: papers, notes, data, earlier decks. Where the material is silent, leave a visible placeholder (`TODO`, `figure-slot`) instead of inventing a number, citation, or customer name. Every figure on a slide traces to a source line. Tell the user which claims you could not support, and let them edit titles and script before layout begins. Avoid stock phrases such as "let's dive in", "exciting", "in conclusion"; end on a takeaway or a request, not on "Thank you".
