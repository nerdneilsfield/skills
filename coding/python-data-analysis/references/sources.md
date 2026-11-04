# Research provenance and version boundaries

Reviewed 2026-10-29. The local guides are original explanations, not copied manuals. Live documentation may follow a newer release than the installed environment; inspect local versions/signatures before using an API. Sources support mechanisms, not claims that one stack is universally fastest. No third-party source files, assets or code were vendored.

## Existing skills: useful structure, not unquestioned authority

- [K-Dense scientific-visualization SKILL](https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/skills/scientific-visualization/SKILL.md): metadata declares MIT; current reviewed version 1.4. Useful evidence-first figure integrity, accessibility and export inspection. Scope is publication figures, and pinned examples assume uv/Python 3.11+: these are not universal requirements for a general-purpose data-analysis skill. No code/text copied. The repository warns that individual skills have individual license metadata; do not assume its root license covers every skill or asset.
- [Scientific-visualization usage guide](https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/docs/skill-guides/scientific-visualization.md): useful request inputs (units, replicate structure and uncertainty). The present bundle extends upstream of figure design into data contracts, joins and denominator accounting rather than duplicating a plotting catalog.

## Primary technical references

| Source | Checked point and local use |
| --- | --- |
| [pandas merge](https://pandas.pydata.org/docs/reference/api/pandas.merge.html) | Explicit keys, cardinality validation, indicator coverage and null-key matching |
| [pandas groupby](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.groupby.html) | Explicit `dropna` and `observed`; do not rely on moving defaults |
| [pandas datetime parsing](https://pandas.pydata.org/docs/reference/api/pandas.to_datetime.html) | Parse errors and UTC handling; naive provenance remains caller responsibility |
| [pandas scaling](https://pandas.pydata.org/docs/user_guide/scale.html) | Load less, dtype choices, chunking limits; pandas remains useful for fitting workloads |
| [Polars lazy optimization](https://docs.pola.rs/user-guide/lazy/optimizations/) | Predicate/projection pushdown and plan-aware expressions |
| [Polars streaming](https://docs.pola.rs/user-guide/concepts/streaming/) | `engine='streaming'`, execution-plan inspection and unsupported-operation fallbacks |
| [DuckDB workload tuning](https://duckdb.org/docs/current/guides/performance/how_to_tune_workloads) | Larger-than-memory operations and remaining blocking-operator limits |
| [DuckDB OOM guide](https://www.duckdb.org/docs/current/guides/performance/oom) | Allocations outside the buffer manager; process memory can exceed configured limit |
| [Arrow datasets](https://arrow.apache.org/docs/python/dataset.html) | Schema, projection/filter and incremental batch scanning |
| [Seaborn error bars](https://seaborn.pydata.org/tutorial/error_bars.html) | Data spread versus estimator uncertainty; `errorbar` introduced in 0.12 |
| [Matplotlib backends](https://matplotlib.org/stable/users/explain/figure/backends.html) | Interactive versus file-rendering backends and headless use |
| [Matplotlib close](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.close.html) | Deregistration/closing figures after noninteractive saving |
| [Plotly HTML export](https://plotly.com/python/interactive-html-export/) | Embedded JS versus CDN/network dependency |
| [Plotly static export](https://plotly.com/python/static-image-export/) | Kaleido v1 needs an available compatible Chrome/Chromium |
| [Altair large datasets](https://altair-viz.github.io/user_guide/large_datasets.html) | Row guard is a payload/design warning; pre-evaluate transforms rather than blindly disable it |

## Social problem leads, verified independently

[DuckDB Reddit: memory limits/spillover](https://www.reddit.com/r/DuckDB/comments/1g8higx/memory_limitsspillover/) describes confusion over total RAM, simultaneous jobs and per-job budgets. It is a useful failure scenario, not an API guarantee; official DuckDB OOM/tuning documentation is the technical authority. Different processes and connections sharing an instance should not be conflated; budget according to the actual deployment.

[Reddit: sharing interactive visualizations](https://www.reddit.com/r/datascience/comments/fc95c9) highlights standalone delivery as a practical requirement. The thread is old and is not evidence for current export dependencies. Plotly's current HTML/static export documentation was used to establish the separate JS and browser requirements.

## Research does not equal runtime verification

Only installed local libraries may be exercised without an installation request. A reference to Polars streaming, DuckDB spilling or Plotly HTML explains a workflow; it does not establish that these engines were benchmarked or rendered here. Record actual optional-test and visual-inspection outcomes separately from this source inventory.
