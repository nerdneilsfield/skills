# Source map and research decisions

Checked 2026-10-29. The local prose and runnable example are original synthesis,
not mirrored manuals. External links are provenance and refresh points; the
workflow does not require network access. `stable`, `latest` and repository
`main` move: these links do not pin a project's supported version. Inspect the
installed API and project lock before applying a version-sensitive detail.

## Primary technical sources

| Source | Specific use |
| --- | --- |
| [NumPy vectorize](https://numpy.org/doc/stable/reference/generated/numpy.vectorize.html) | Convenience wrapper is not native-loop acceleration |
| [NumPy broadcasting](https://numpy.org/doc/stable/user/basics.broadcasting.html) | Input broadcasting can avoid copies while results still consume memory |
| [NumPy copies/views](https://numpy.org/doc/stable/user/basics.copies.html) | Indexing, reshape, flatten and shared storage |
| [NumPy thread safety](https://numpy.org/doc/stable/reference/thread_safety.html) | GIL release is operation-dependent; shared mutation and object arrays |
| [SciPy parallel execution](https://docs.scipy.org/doc/scipy/tutorial/parallel_execution.html) | Default execution, BLAS teams and opt-in workers |
| [SciPy solve](https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.solve.html) | Structure assumptions, finite checking and overwrite contracts |
| [threadpoolctl](https://github.com/joblib/threadpoolctl) | Loaded native pools, scoped controls and runtime limitations |
| [Numba performance tips](https://numba.readthedocs.io/en/stable/user/performance-tips.html) | Compiled loops, nopython, fastmath and parallel transformations |
| [NumExpr guide](https://numexpr.readthedocs.io/en/latest/user_guide.html) | Expression engine, dtype differences, precision policy and thread pool |
| [JAX benchmarking](https://docs.jax.dev/en/latest/benchmarking.html) | Compilation, synchronization, dtype matching and transfers |
| [CuPy performance](https://docs.cupy.dev/en/stable/user_guide/performance.html) | Event-based timing, streams, warm-up and initialization |
| [PyTorch numerical accuracy source](https://github.com/pytorch/pytorch/blob/main/docs/source/notes/numerical_accuracy.md) | Reduction order, backend variation, extremal values and conditioning |

These are not mandatory runtime dependencies or a claim that every optional path
has been executed. Published example speedup numbers were deliberately not reused.

## Actual skill candidates inspected

- [NVIDIA official catalog](https://github.com/NVIDIA/skills): product-specific
  skills maintained in source repositories and mirrored into the catalog.
  Its README distinguishes CC-BY-4.0 documentation/skills and Apache-2.0 source.
  Do not import the whole catalog or assume one MIT license.
- [cuML agent-skill authoring](https://docs.nvidia.com/cuml/latest/developer_guide/agent_skill/):
  useful structure is a short entrypoint, on-demand numerical parity reference,
  removed-API scanner/data and precise evaluation assertions. It tests replacement
  APIs against the actual package. The documentation acknowledges that a held-out
  independent evaluation set is still needed; advertised evaluation is not proof
  of universal correctness. Its online evaluation infrastructure is not a
  prerequisite for this offline skill.
- [K-Dense optimize-for-gpu](https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/skills/optimize-for-gpu/SKILL.md):
  useful evidence-first GPU suitability and end-to-end verification decisions.
  Broad triggers and extensive product compatibility tables are not adopted in
  this CPU-first skill. [MIT license checked](https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/LICENSE.md).
- [theneoai numpy-scipy-expert](https://github.com/theneoai/awesome-skills/blob/main/skills/tool/scientific/numpy-scipy-expert/SKILL.md):
  not selected as a quality baseline. At review, GitHub displayed frontmatter YAML
  parse failure and the skill used unverifiable expert-persona claims and an
  overly categorical vectorization preference. A repository title is not quality
  assurance. No material or license from this candidate was incorporated.

## Community leads, not authorities for technical claims

- [Numba optimization discussion](https://www.reddit.com/r/Python/comments/1bk9tav):
  prompted examination of fusion rather than simply decorating NumPy expressions.
- [No Numba speedup](https://www.reddit.com/r/learnpython/comments/l1d1xm):
  prompted explicit separation of first compilation from warmed execution.
- [NumPy multicore](https://www.reddit.com/r/Python/comments/1fgdhvo/can_we_talk_about_numpy_multicore/):
  prompted distinguishing native teams from general array operations.
- [Large-array Numba comparison](https://stackoverflow.com/questions/78558552/using-numba-to-speed-up-vectorization-on-very-large-numpy-arrays):
  illustrates why algorithm, hardware and versions matter to a benchmark.

The decisions above were cross-checked against primary sources rather than
copying anecdotes, claimed speed ratios or universal tool rankings.
