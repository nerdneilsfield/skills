---
name: python-data-analysis
description: "Use when the user asks to analyze or plot tabular, time-series, or missing data in Python: join cardinality, denominators, group-by meaning, larger-than-memory aggregation, or honest uncertainty in a chart. Defer shared contracts to python. Not for predictive training (python-ml), NumPy kernel numerics (python-numerics), process profiling (python-performance), or environment repair (python-environments)."
license: MIT
compatibility: Requires Python 3; pandas, Polars, or DuckDB as the project uses them.
metadata:
  author: DengQi
---

# From a data question to a defensible figure

A fast query and an attractive chart can preserve the wrong answer. Keep one chain of evidence: **question → observation unit and schema → checked transformations → explicit estimate → visual encoding → inspected artifact**. Change the stage that failed, then verify that the meaning survived. Do not migrate a working pandas workflow merely because another engine exists. Defer shared data contracts to `python`. Defer predictive splits, training, and checkpoints to `python-ml`. Defer NumPy or SciPy kernel numerics to `python-numerics`. Defer process-wide profiling to `python-performance`. Defer interpreter and CUDA/ABI repair to `python-environments`.

## Read the matching reference, not the whole directory

| Current problem | Read first |
| --- | --- |
| Unclear question, duplicate joins, missing outcomes, timestamps, misleading averages | [Data contracts and estimation](references/data-contracts-and-estimation.md) |
| Memory blow-up, slow tables, chunking, lazy/streaming plans, engine choice | [Scaling without changing meaning](references/scaling-and-engines.md) |
| Plot choice, uncertainty, overplotting, fonts, headless/offline export, privacy | [Visualization and delivery](references/visualization-and-delivery.md) |
| Need bounded structural CSV check or runnable join-to-chart example | [Local tools and worked example](references/local-tools-and-example.md) |
| Need source/version/license provenance | [Research sources](references/sources.md) |

Read a second reference in this skill after the first one names a different stage of the same analysis (for example a join bug that also blows memory). Defer general profiling to `python-performance`, numeric precision and array layout to `python-numerics`, interpreter, source, lock, and CUDA configuration to `python-environments`, and predictive split, leakage, and training to `python-ml`. If a named owner is absent, request that exact skill from this bundle, not a global search or implicit installation. The operational explanations here work offline; external links are provenance.

## Establish the analysis contract

Record what one row represents, target population, time window, units, entity/event keys, missing-value meanings, join cardinality, denominator and delivery medium. Keep source inputs immutable. Distinguish descriptive exploration from a pre-specified statistical claim or predictive evaluation. An analysis of recorded events cannot silently become a conclusion about all people, devices or future events.

Validate at boundaries, not only at the final chart: parse failures, duplicate keys, join coverage, group counts, aggregation totals and exclusions. Retain enough local evidence to reproduce an answer without publishing raw personal data. Avoid complete data dumps as a debugging shortcut.

## Work from evidence to repair

For an unexpected result, reproduce on a bounded representative subset, identify the first boundary where counts/units disagree, and repair the transformation there. For a memory problem, measure intermediate shape and materialization before switching libraries. For a misleading figure, fix estimator/encoding before styling. Re-run the same correctness assertions and compare end-to-end time/memory if performance changed.

The bundled [example](assets/analysis_example.py) checks event identity, rejects null/duplicate dimension keys, validates a many-to-one join, reports observed and eligible denominators separately, and renders an optional headless PNG. It is synthetic and descriptive, not a statistical or library benchmark.

## Delivery contract

Deliver the answer plus its population/window/unit, estimator and denominator, exclusions/missingness, uncertainty meaning, data/code/dependency identity, and the plotted summary table when a chart was produced. Report which renderer/export was actually run and which offline/browser/font checks remain. A PNG signature test is not visual inspection; a successful notebook display is not proof that a standalone HTML file works without the notebook server.
