# Sources and maintenance notes

Researched 2026-10-29. This skill is original explanatory text and original local examples, not a copied manual or third-party skill. Sources below support specific decision boundaries. The offline workflow does not require opening them. Floating `stable` documentation is not a project version pin: during research PyTorch pages/search snapshots mixed 2.14 and 2.15, while Lightning's stable URL showed a 2.7 development header. Match APIs to the installed version and do not infer validated execution from a source link.

## Existing GitHub skills examined

- [K-Dense scikit-learn skill](https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/skills/scikit-learn/SKILL.md): useful reference routing, local datasets and explicit compatibility/test claims. Its file declares **BSD-3-Clause**, distinct from blanket assumptions about the repository. Its entry also emphasizes network installation and a particular version; those are not adopted as automatic actions or universal requirements here. The quickstart's scaling of a random forest is not a universal preprocessing requirement.
- [K-Dense PyTorch Lightning skill](https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/skills/pytorch-lightning/SKILL.md): declares **Apache-2.0**; useful distinction between CPU execution and unexecuted GPU/distributed examples, and local versus online logging. Framework-specific Trainer organization is not imposed on plain PyTorch/JAX projects. No upstream implementation was copied; license declarations are candidate-review observations, not a claim of license audit for every repository asset.

## Social discussion as a question, not an authority

- [PyTorch Forums: DataLoader slower with num_workers > 0](https://discuss.pytorch.org/t/dataloader-slower-with-num-workers-0/100970): reports from multiple older versions/platforms motivated the worker-count sweep and rejection of a universal cores-to-workers formula. These reports are not current universal performance measurements. The official loader documentation and tuning recipe below supply the implementation facts.
- [PyTorch issue 101188: import-order/data-loader performance](https://github.com/pytorch/pytorch/issues/101188): a concrete lead for investigating native-library/thread interactions, not permission to prescribe an import-order workaround without reproducing the actual version/workload.

## Primary technical references

### Modeling and evaluation

- [scikit-learn common pitfalls](https://scikit-learn.org/stable/common_pitfalls.html): train-only preprocessing and pipeline leakage boundaries.
- [Cross-validation](https://scikit-learn.org/stable/modules/cross_validation.html): IID/group/time assumptions and fold designs.
- [Hyperparameter search](https://scikit-learn.org/stable/modules/grid_search.html): development-set selection, search cost and nested evaluation.
- [Model evaluation](https://scikit-learn.org/stable/modules/model_evaluation.html): metric definitions, support and averaging distinctions.
- [Calibration](https://scikit-learn.org/stable/modules/calibration.html): calibration from held-out predictions and discrimination versus probability quality.
- [Model persistence](https://scikit-learn.org/stable/model_persistence.html): pickle execution risks, supported version context, skops/ONNX tradeoffs.

### Training state, reproducibility and safety

- [PyTorch inference mode, versioned 2.14](https://docs.pytorch.org/docs/2.14/generated/torch.autograd.grad_mode.inference_mode.html): graph tracking differs from module evaluation mode.
- [AMP examples](https://docs.pytorch.org/docs/stable/notes/amp_examples.html): scaled gradients, unscale-before-clipping and accumulation/step boundaries.
- [Reproducibility, versioned 2.14](https://docs.pytorch.org/docs/2.14/notes/randomness.html): generator/worker seeding, deterministic-algorithm tradeoffs and cross-platform/version limits.
- [Saving/loading models](https://docs.pytorch.org/tutorials/beginner/saving_loading_models.html): model versus optimizer checkpoints and mutable state snapshots.
- [Serialization semantics](https://docs.pytorch.org/docs/stable/notes/serialization.html): restricted `weights_only` loading is not a complete malicious-file sandbox.
- [Lightning checkpointing](https://lightning.ai/docs/pytorch/stable/common/checkpointing_basic.html): training state and `fit` checkpoint resumption. Verify the local release because this floating page exposed development documentation during research.

### Performance and parallel data handling

- [PyTorch DataLoader source documentation](https://github.com/pytorch/pytorch/blob/main/docs/source/data.md): worker copies/memory, seeding, persistent state and distributed sampler semantics. Main-branch source is a maintenance reference, not a tested local version.
- [DataLoader API](https://docs.pytorch.org/docs/stable/data.html): sampler padding, worker and prefetch configuration.
- [Performance tuning guide](https://docs.pytorch.org/tutorials/recipes/recipes/tuning_guide.html): tunable data loading, inference graph overhead, memory/compute tradeoffs.
- [Profiler API](https://docs.pytorch.org/docs/stable/profiler.html) and [bounded profiling recipe](https://docs.pytorch.org/tutorials/recipes/recipes/profiler_recipe): schedule/step semantics and instrumentation overhead.
- [CUDA semantics, versioned 2.14](https://docs.pytorch.org/docs/2.14/notes/cuda.html): asynchronous timing, allocator versus live tensor memory and stream lifetime.
- [JAX asynchronous dispatch](https://docs.jax.dev/en/latest/async_dispatch.html): complete device work before interpreting host timing. Numerical/JIT details are owned by `python-numerics`, not duplicated here.

## What has not been established by research

These sources do not prove the user's models speed up, a worker count is optimal, quantization preserves their accuracy, or a distributed job resumes correctly. The bundled CPU fixtures and metadata audits cover only their stated invariants. Actual GPU, mixed-precision, compiler, exported model and multi-rank tests must use the target runtime and representative data.
