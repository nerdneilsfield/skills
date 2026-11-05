---
name: paper-to-code
description: "Use when implementing a method from a paper: map its equations, algorithm steps, and notation to concrete code, and keep a record of where the code deliberately differs from the paper, which hyperparameters the paper never states, and the implementation tricks it omits. Not for reading the paper for understanding (qi-read-paper) or for reproducing its reported numbers (paper-reproduce)."
license: MIT
compatibility: Uses pdftotext or MinerU to get equations out of a PDF, rg and ast-grep to locate the code that must change. A code graph or semantic index, when available, shortens the first mapping pass.
metadata:
  author: DengQi
---

# From paper to working code

The deliverable is code plus a deviation record. A silent difference between the paper and the code is the defect this skill exists to prevent.

## 1. Map before writing

Produce three lists from the paper, and keep them as the worklist:

- **Notation** — every symbol, its meaning, its shape or unit, and where it first appears.
- **Equations** — the ones that must be implemented, numbered as in the paper.
- **Steps** — the algorithm, in the order the paper states it, including initialization and termination.

Mark each item `must`, `nice`, or `unspecified`. `unspecified` is the common case for initialization, schedules, and numerical guards.

## 2. Locate the code to change

Before writing, find the existing seams with the tools at hand. If a code graph or semantic index is available, build or query it to find the call path the method plugs into; otherwise map the entry point with `rg` and `ast-grep` and read outward from there. `tokei` tells you which parts of the repository are large enough to matter.

Map each `must` equation to a function or a block, and write the mapping down as you go.

## 3. Implement the paper's version first

Implement what the paper says, even where you expect it to be slow or unstable, so the first result is a faithful one. Optimize only after it runs, and keep the faithful version runnable for comparison.

Prefer the paper's variable names for the quantities it names. When the code and the paper use different letters for the same thing, put the mapping in a comment at the definition.

## 4. Keep the deviation record

One file, one row per deviation, written as you make it:

```markdown
# Paper: <title> (<arXiv id or DOI>)

## Notation
| Symbol | Paper meaning | In code |

## Deviations
- <date> | <paper eq/step> | <what the code does instead> | <why> | <does it change results>

## Unstated hyperparameters
- <name> | <value chosen> | <how chosen> | <sensitivity if known>

## Tricks the paper omits
- <what> | <where it shows up> | <source: author code / my discovery>
```

## 5. Check the mapping both ways

Walk the paper's steps once against the code and once in reverse: for every branch in the code, name the paper line that justifies it. An unjustified branch is either a trick the paper omitted or a bug. Record it either way.

## 6. Make it fast without losing the faithful version

Speed work starts after step 5, on a profile of the faithful version with the paper's shapes and precision. A number from the paper's runtime claim is a target only with the conditions from `paper-reproduce`.

Keep the faithful CPU path runnable and tested, and treat it as the reference for every faster version. Compare outputs on fixed inputs with a stated tolerance, derived from the metric's noise and the precision in use, and check non-finite cases. For a GPU port, follow the order in `python-performance`, starting from the least invasive option. Every change that can move results, such as `float32`, mixed precision, an approximate search, or another reduction order, goes in the deviation record.

## Gotchas

- Symbols are reused across sections of a paper. Resolve each occurrence against its local definition, not the first definition you read.
- The initialization, the learning-rate schedule, and the numerical epsilon are the usual reproduction gaps. They are `unspecified` until the paper or its code says otherwise; do not fill them silently.
- "We normalize the features" does not say per-batch, per-sample, or per-channel. Guess nothing; check the author code or state the choice in the deviation record.
- An equation that divides by a quantity can be computed in a different but equivalent form; the difference shows up only in floating point. Note which form the paper used.
- Reading order from `pdftotext` breaks on two-column papers and on equations. Check the equation against the rendered page before implementing it.
- The paper's "we use the default settings" is not a specification. Find the version of the library and the actual defaults.
- Do not copy code from a repository without checking its license; a paper's code license is often not the paper's license.
- A trick found in the author code but not in the paper is still a finding. Record it with its source.

## Report

State the paper version, the equations implemented, the tolerance and hardware of any speed work, every deviation with its reason, the hyperparameters the paper left unstated and how they were chosen, and what is not yet verified against the paper.
