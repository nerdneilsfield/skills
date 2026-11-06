# Intake

Collect missing facts before drafting. A paper built on guessed facts costs more to repair than one question.

## Facts to establish

| Group | Fact |
|---|---|
| Venue | Target venue, track, year, deadline; link to the current call or author instructions; double-blind or not |
| Type | Paper type from `paper-types.md`; new paper, journal extension, or resubmission |
| Claim | The one-sentence contribution; the two or three claims that carry it |
| Evidence | Which tables, figures, logs, or measurements exist now; which are planned |
| Platform | For hardware: process node, device and tool versions, simulation or measurement. For algorithms: datasets, baselines, compute |
| Material | Existing draft, bib file, figures, template, previous reviews, related own papers |
| Language | English, Chinese, or both; Chinese thesis versus paper |
| Policy | Disclosure rules for generated text and figures; code and data release; prior-publication overlap |
| House style | Whether a `.house-style.md` exists in the paper repository |

## Ask once

1. List what is already known from the files and the request. Do not re-ask it.
2. Send one batch with at most about eight questions. Give each a recommended default so the user can answer "defaults" or fix only some.
3. Mark questions that block the result (venue, claim, evidence) apart from those that only polish it.

Example batch format:

```
Blocking
1. Target venue and year? Default: none, I will write venue-neutral IEEE two-column.
2. Is the 18% energy reduction measured on silicon or from post-layout simulation? Default: treated as simulation and worded that way.
Non-blocking
3. Language? Default: English.
```

## Unattended runs

When nobody can answer, decide, proceed, and record. Put the assumptions in a block at the top of the draft or in the report, each with its default and the effect of being wrong:

```
Assumptions (unverified, confirm before submission)
- Venue-neutral IEEEtran, 8 pages: page limit not checked against any call.
- Results in Table II are taken as post-layout, not silicon.
```

Never assume a result, a citation, a measurement condition, or a policy. Missing evidence becomes a visible placeholder (`[TODO: measured power at 0.9 V]`), not a plausible number.
