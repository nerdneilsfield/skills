---
name: python-performance
description: "Use when measuring, fixing, or asking how to improve Python performance, even for a quick how or why question with no profile yet: latency, throughput, hotspots, memory growth, event-loop stalls, too many threads, paging, or poor application scaling. Defer shared contracts to python. Not for NumPy/SciPy numerical correctness (python-numerics), environment or CUDA/ABI repair (python-environments), training-loop or checkpoint work (python-ml), or joins and charts (python-data-analysis)."
license: MIT
compatibility: Requires Python 3. py-spy, Scalene, and memray are optional.
metadata:
  author: DengQi
---

# Python performance: evidence to a verified remedy

Improve useful work, not profiler rankings. This skill owns measurement and repair of application latency, throughput, hotspots, memory growth, event-loop stalls, thread counts, paging, and scaling. Separate Python execution, native execution, waiting, and memory pressure before choosing a change. Defer data contracts and resource lifetime to `python`. Defer shape, dtype, solver, BLAS, and precision changes to `python-numerics`. Defer interpreter, lock, and CUDA/ABI repair to `python-environments`. Defer training, evaluation, and checkpoints to `python-ml`. Defer joins, group-by meaning, and charts to `python-data-analysis`. If an owner is absent, name the missing skill; do not globally search or install a replacement. The references here remain useful offline without those owners.

## Route by the current uncertainty

Read the matching reference, not every document. Read a second reference after the first one names a different layer (for example waiting plus memory).

| Question | Local reference |
| --- | --- |
| Is the baseline comparable? What does the measurement mean? | [Measurement contract](references/measurement-contract.md) |
| Python loop or native kernel? Which functions/lines matter? | [CPU and native attribution](references/cpu-and-native.md) |
| Slow despite low CPU, async stalls, excessive workers, cache-line contention? | [Waiting and concurrency](references/waiting-and-concurrency.md) |
| Allocation churn, retained objects, RSS growth, faults or swap? | [Allocation and retention](references/allocations-and-retention.md) |
| Need a command, version gate, permission boundary or offline fallback? | [Tool recipes](references/tool-recipes.md) |
| Need a complete diagnosis → fix → prevention example? | [Batch pipeline](references/worked-pipeline.md) |
| Need to compare existing JSON samples? | [Bounded sample comparison](references/sample-comparison.md) |

## Establish the problem and choose one discriminating experiment

Record the required outcome (for example p95 latency with bounded memory), representative
input identity/size, output correctness, interpreter/build, dependency versions and usable
CPU/thread budget. Distinguish startup from steady state and one process from the whole
worker group. Start with wall time and process CPU, then select one profiler that can
resolve the uncertainty. A profile explains where to investigate; it does not establish
the speedup of a proposed fix.

For every finding report **evidence → supported cause → smallest remedy → risk →
verification → prevention**. A Python hot loop may call for fewer repeated operations;
a native hotspot may need a numerical/kernel change; waiting may need bounded scheduling;
growing retained state may need a lifetime/cache limit. Do not prescribe all four.

Use the project's existing execution model and authorized data. Bounded captures only;
no automatic attach to unrelated processes, privilege escalation, system tuning,
network installation, cloud AI optimization or uploading profiles. Missing counters or
dependencies are unavailable evidence, not zero cost or passed validation.

## Verify and stop

After the change, rerun correctness and the same representative workload **without the
profiler**. Check the relevant latency distribution, throughput, peak/retained memory and
scaling together. A faster average that violates tail latency or memory is not accepted.
Keep the old implementation as a comparison when useful; do not stack unmeasured tweaks.
Stop when the agreed target is met or the next necessary measurement is unavailable.

Return the workload/scope, evidence and uncertainty, concrete change, comparable before/
after observations, correctness result, tradeoffs and what remains untested. Label an
unmeasured remedy a hypothesis, not an established improvement. All decision procedures
and the example work without external links.
