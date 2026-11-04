# Reproducibility and model artifacts

## Reproduction is a recorded experiment, not a seed

Keep a bounded manifest with code revision, dataset identity/version and split IDs, feature schema/units, preprocessing, target definition, hyperparameters, package/driver/device versions, precision and determinism choices, metric/threshold definitions and training budget. Do not include raw private data, credentials or an unfiltered environment dump. Hashes help identify files but are not proof a model's source is trustworthy.

Seed the generators actually in use: Python, NumPy generators, framework RNGs and data-loader workers. A newly created NumPy Generator has its own state; setting the legacy global seed does not seed all generator objects. A PyTorch worker receives a framework seed, but other random libraries and custom dataset state need intentional initialization. Deterministic algorithms can cost performance or reject unsupported operations. Reproducibility across versions, backends, devices and parallel reduction orders is not guaranteed by equal seeds; report tolerance and repeated-run variation where bitwise identity is unrealistic.

## Distinguish three artifacts

1. **Inference artifact:** model state plus the exact preprocessing/schema and output interpretation. No optimizer is needed if training will not resume.
2. **Training checkpoint:** model, optimizer, scheduler, precision-scaler state where used, epoch/global optimizer step, RNG states and enough sampler/data progress to resume the intended point. Include configuration and model selection state. Saving only weights restarts training dynamics rather than resuming them.
3. **Evaluation report:** split identity, metric implementation/threshold, sample counts, environment and quality/resource measurements. A checkpoint filename such as “best” is not evaluation evidence.

Save “best” state as an actual snapshot: retaining a reference to a mutable state dictionary can track later updates. Write a new artifact, verify it, then replace the intended checkpoint safely; do not overwrite the only usable state before validation. Framework-managed checkpointing can save much of the state, but a custom dataset's mid-epoch cursor or external sampler may still need explicit support. Lightning's `Trainer.fit(..., ckpt_path=...)` resumes training; merely constructing a module from saved weights is not the same operation.

Test interruption: run a deterministic short workload uninterrupted and with save/restart at a specified boundary; compare next sample IDs, optimizer step, learning rate, loss and parameters under stated tolerances. Exact mid-epoch replay can be harder with prefetched worker batches or elastic world-size changes. If only epoch-boundary restart was validated, state that limitation. Distributed checkpoint formats and rank-local state need their matching loader and topology plan; do not assemble shards by guessing filename order.

## Loading is a trust boundary

Do not inspect an unknown model by loading it. `pickle`, `joblib` and `cloudpickle` may execute code. For sklearn, same-version dependencies are needed for supported persistence; a file loading successfully in a different version does not establish supported behavior. `skops` permits more controlled inspection but still needs an explicit trusted-type review. ONNX can reduce Python dependency coupling, but conversion/operator coverage, numerical parity and runtime isolation still matter.

PyTorch's restricted `weights_only=True` loading narrows executable behavior but is not a sandbox against resource exhaustion or every malicious tensor. Do not fix a restricted-loader error by automatically setting `weights_only=False` or allowlisting unknown globals. Verify origin and expected size, use resource limits appropriate to the context, and load only authorized trusted artifacts. The bundled examples never load checkpoints. Remote model repositories may request execution of custom code; do not enable that implicitly.

## Deployment parity and monitoring

Keep preprocessing and output decoding with the model: class ordering, normalization, tokenizer/vocabulary, units and decision threshold are model behavior. Test known fixtures before/after save/export, then representative held-out examples, boundary shapes, missing/unknown inputs and relevant precision ranges. Report both tensor deviation and task metrics; small logit changes near a threshold can change decisions.

At serving time, separate schema validation, model computation and postprocessing failures. Bound input sizes and batching queues. Avoid logging raw personal inputs. Track latency/tails, errors, feature distribution and eventual label quality where labels arrive; feature drift alone is not proof model quality changed, nor does stable input distribution prove quality. Define rollback to a verified artifact and pipeline, not just a weight file.
