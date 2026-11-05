# Section-by-section guidance

Write for a reviewer who reads the abstract, then the figures and tables, then the introduction, and only then the method. Every claim in the front must be answered by evidence behind it.

## Claim-to-evidence chain

Before drafting, fill a small ledger. Keep it in a scratch file, not in the paper.

| Claim (one sentence) | Where stated | Evidence | Condition | Status |
|---|---|---|---|---|
| "Reduces energy per inference by 1.8x against baseline B" | abstract, intro, conclusion | Table 3, row 4 | 28 nm post-layout, 0.9 V, ResNet-18 | measured / simulated / missing |

Rules:

- Each claim in abstract, introduction, and conclusion points to a table, figure, proof, or measurement. No evidence, no claim; soften it or cut it.
- The same number is written identically everywhere it appears, with the same conditions. A script can check the abstract: [check_paper.py](../scripts/check_paper.py).
- Wording follows the evidence level: "measured", "post-layout simulation", "RTL simulation", "on dataset X". Do not write "achieves" for a projection.
- Each limitation that weakens a claim appears once, near the claim, not in a buried paragraph.

## Title

Name the object, the technique, and the setting; a reader should guess the field and the move. Avoid "towards", "a novel", and vague "efficient"; avoid a claim the paper cannot support ("real-time" needs a stated rate on stated hardware). An acronym is useful only if the field already knows it or the name is memorable. Check the venue's title rules (length, no acronyms in some tracks).

## Abstract

Five moves in about 150 to 250 words, or the venue's limit: problem and why it matters, gap, approach, evidence, headline result with its condition. Include the numbers that carry the claim (node, power, accuracy, speedup) and the baseline they are relative to. No citations, undefined acronyms, or "we also discuss". Each abstract number must reappear in the body.

## Introduction

Order: context in two or three sentences, the specific problem, why existing approaches fall short (concrete, with citations), the key idea, the contributions, and optionally a paper outline. Put Figure 1 where it does the most work, usually the idea or the headline result. Do not open with a general statement that fits every paper in the field.

### Contributions list

Three or fewer bullets, each a testable statement: what was built or shown, and the evidence. Good: "A weight-stationary dataflow that reduces off-chip traffic by 41% on the evaluated networks (Sec. V)". Bad: "We propose a novel framework." Do not list "we conduct experiments" as a contribution. Each bullet matches a row of the ledger.

## Related work

Group by idea, not by author. For each group say what it does, what it lacks relative to this paper, and cite precisely. Include the closest competitor and the most recent strong baseline, and be fair to them. Cite your own earlier work as plainly as any other. For double-blind venues, use third person.

## Method or architecture

State the problem formally or with a block diagram first, then the design. Give the reason for each choice before its detail. Notation is defined once and used consistently. Provide enough to reproduce: parameters, bit widths, memory sizes, algorithm steps, complexity. Keep a running example if the method is hard to follow. For hardware, distinguish what is new from what is standard.

## Implementation

Separate design from realisation: language and toolchain, code size, platform, configuration, and constraints. For hardware, put flow and tool versions here or in the setup of the evaluation. Say what is not implemented (for example, only the accelerator core was taped out, not the full SoC).

## Evaluation

Open with the questions the experiments answer, each tied to a claim. Then setup (see `algorithm-evaluation.md` and `hardware-evaluation.md`), main results, ablation, sensitivity, and limits. Interpret each result in a sentence: what it shows and why. Report where the method loses.

## Discussion and limitations

State where the method does not hold: assumptions, workloads that were not tested, failure cases, deployment costs. Venue rules may require a limitations section; check the call. Keep this honest and specific; generic hedges ("further work is needed") add nothing.

## Conclusion

Restate the finding and its evidence in new words, with the key numbers, and then what follows from it. Do not introduce new results or claims. Future work in one or two concrete sentences.

## Figures and tables

Every figure has a purpose in the argument, is referred to in the text before it appears, and can be read at print size in grayscale. Captions say what to see, not only what it is. Tables align decimals, state units in headers, and mark the best result consistently. Figure creation: see `research-figure`.
