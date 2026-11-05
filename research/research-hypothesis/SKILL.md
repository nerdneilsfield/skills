---
name: research-hypothesis
description: "Use when an observation, a surprising result, or a research idea has to become a testable hypothesis before running anything: keep observation, question, hypothesis, mechanism, prediction, alternative explanation, null, and evidence apart, list rivals including artifacts, and write predictions that discriminate between them. Not for running the experiment (algorithm-experiment), designing the method (algorithm-design), or finding the literature (paper-search)."
license: MIT
metadata:
  author: DengQi
---

# Turn an observation into a test that can tell rivals apart

The output is one file, written before the experiment: the frozen observation, the rival explanations, and a matrix of predictions that differ between them. A hypothesis stays a candidate until a test could have gone against it, and it stays a candidate afterwards too.

## Keep the objects apart

| Object | What it is | Example |
| --- | --- | --- |
| Observation | What was measured, with provenance and uncertainty | ATE rose 12% on 3 of 11 scenes, seeds 0-4, commit `abc123` |
| Question | What the work must answer, with its scope | Does the new matcher degrade on low-texture scenes? |
| Hypothesis | A candidate explanatory claim | Too few inliers survive the threshold in low texture |
| Mechanism | The process linking cause to outcome | Fewer inliers, then a worse-conditioned pose solve, then drift |
| Prediction | An observable consequence, written before checking | Error rises with the condition number of the pose Hessian |
| Alternative | A rival account, including bug, data, and bias | Those three scenes share a calibration file |
| Null | The specific no-difference model an analysis tests | Paired per-scene error difference has median zero |
| Evidence | Observations bearing on a claim, never the claim itself | Per-scene table linked from the run log |

A mechanism is not a prediction. A prediction is not evidence. Rejecting a null does not establish the mechanism, and beating one rival does not eliminate the rivals nobody listed.

## 1. Freeze the observation

Write what was seen before explaining it: the number, the commit, the data, the seeds, and how the pattern was found. Say whether it was expected or picked out after looking at many results. A pattern selected after scanning a results table needs fresh data; the data that suggested it cannot also confirm it.

## 2. List rivals before choosing a test

Write rivals from different classes before settling on the favorite, and do not pad to a fixed number:

- **Implementation:** a bug, a stale cache, a changed default, a wrong unit.
- **Data:** a split difference, a label error, leakage, a corrupted scene.
- **Selection:** the subset was picked after seeing it, or the best of many trials.
- **Measurement:** the metric, its alignment step, or timing resolution produces the effect.
- **Noise:** seed variance or scheduling.
- **Competing mechanism:** another real cause, or the same cause at another scale.

Check the cheap artifacts first. An hour spent ruling out a bug is worth more than a good theory about a bug.

## 3. Write discriminating predictions before running

For each candidate write the condition, the observable, the expected direction or size, and the result that would count against it. Then fill the matrix:

```markdown
| Test | Hypothesis H1 | Rival R1 | Rival R2 | Null | Cost | Discriminates? |
| --- | --- | --- | --- | --- | --- | --- |
| Swap calibration on the 3 scenes | no change | error drops | no change | no change | 10 min | R1 vs rest |
```

A row where every candidate predicts the same result is uninformative, so drop it or redesign it. Run the cheapest row that splits the remaining candidates, and declare what an indeterminate result means before seeing one.

Add a negative control: a case that shares the same bias paths but where the mechanism cannot operate, such as shuffled labels or a component replaced by a no-op that should reproduce the baseline. If the "effect" appears there, the pipeline is producing it.

## 4. Fix the design before the run

- **Unit of replication:** decide what the independent unit is. Five seeds on one scene are repeats of one scene; generalizing across scenes needs scenes.
- **Pairing:** run arms on the same seeds and inputs and analyze per-pair differences; this removes variation you would otherwise pay for in repeats.
- **Order:** interleave or randomize run order when drift is possible, such as thermal throttling, a warming cache, or a shared machine.
- **Interactions:** one-at-a-time ablation cannot see two components that only help together. If you suspect that, run the small factorial.
- **Interim looks:** peeking and stopping when the result looks good inflates false positives. Fix the run count, or write the stopping rule first.

Hand the frozen file to `algorithm-experiment` for execution. If the hypothesis came from `algorithm-design`, record which candidate it tests.

## 5. Update, do not promote

After the test, record per candidate: supported on this test, contradicted, or undecided, with a link to the evidence. Keep the wording narrow: "consistent with H1, R1 ruled out by test 2, R2 not tested". Changed predictions after seeing the result are a new hypothesis on new data, and are labeled exploratory.

## Gotchas

- Explaining a result first anchors every later test on that explanation. Write the rivals before reading the code you suspect.
- "No effect found" with an underpowered run is indeterminate, not support for the null. State the smallest effect the run could have detected.
- A prediction made after seeing the data is a description. Date it honestly.
- A paper's mechanism is the authors' hypothesis, not an established fact. Check what they actually measured.
- A proxy metric that moved does not mean the construct moved. Say what the proxy is standing in for.
- "Novel" means not found within a stated search. Log the search through `paper-search`; never claim nobody has done it.
- Surviving one test does not make a mechanism true. Unlisted rivals and auxiliary assumptions remain.

## Report

State the frozen observation, the candidates and rivals, the discrimination matrix, what was decided before running, the verdict per candidate, and which rivals remain untested.
