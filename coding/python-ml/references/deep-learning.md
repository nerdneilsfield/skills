# Deep learning: make each state transition explicit

## 1. Prove one batch before scaling

Use the split/feature availability contract from [classical modeling](classical-ml.md), including training-only normalization. Keep stochastic augmentation in training; validation should use the declared deterministic evaluation transform or a separately specified test-time augmentation policy. Check a bounded batch for shape, dtype, units, label range and mask alignment. Cross-entropy commonly expects raw class logits and integer class indices, not an already-softmaxed tensor; binary losses have different shape/target contracts. Verify the chosen loss's reduction and how padding/ignored labels affect its denominator.

Start with one finite forward/backward/optimizer step. Inspect finite loss and gradients and prove at least one trainable parameter changes. If a tiny, clean subset cannot be overfit, investigate labels, masks, detached graphs, frozen parameters, learning rate and loss scaling before buying more compute. Overfitting this subset is a debugging test, not evidence of generalization.

[torch_train_eval.py](../assets/torch_train_eval.py) is a complete CPU-only example. It proves a parameter update and non-mutating graph-free evaluation. Its accuracy is on training examples and deliberately not labeled validation quality.

## 2. Training and evaluation are different states

`model.train()` and `model.eval()` change module behavior such as dropout and batch normalization. They do not switch autograd on/off. For ordinary validation, call `eval()` and disable gradient recording with `no_grad()`, then restore training mode before subsequent optimization. For pure inference, `inference_mode()` can remove additional tracking, but tensors created there have restrictions if later reused by autograd. Gradient-based explanations or input optimization still require gradients even when module behavior is `eval()`.

Keep inputs, masks, labels, model parameters and relevant buffers on compatible devices. A hidden `.cpu()`, `.numpy()` or `.item()` in the step may force transfer/synchronization; do not remove it if it is required for correctness, but move logging/aggregation to a deliberate boundary. Accumulate metric numerators and denominators rather than averaging unequal-size batch means. Exclude masked tokens consistently in both loss and metrics.

**Symptom:** validation changes with batch order/size. **Check:** missing `eval`, train-time transformations, batch-dependent normalization, stateful metric reset, sampler duplication. **Fix:** correct the state and aggregation first. **Verify:** repeat on the same sample IDs and compare full-set versus differently batched evaluation within tolerances.

## 3. Mixed precision and accumulation preserve a mathematical contract

Choose precision against hardware support and numerical requirements, not a blanket “half is faster.” With current compatible PyTorch, the public pattern is autocast around forward/loss and a gradient scaler for CUDA FP16 where appropriate. BF16 often does not require gradient scaling; precision suitability still needs measurement. Do not globally cast a model and every input to half as a substitute for autocast policy. Keep sensitive operations in a suitable precision when evidence warrants it.

For scaled gradients: backward on the scaled loss, unscale once after the complete accumulation window, then clip/inspect, perform the scaler-mediated optimizer step, and update the scale. Clipping before unscaling applies the wrong threshold. A nonfinite step may be skipped; scheduler and progress reporting must not assume every attempted step updated parameters. Check the installed framework API rather than copying an old `torch.cuda.amp` spelling blindly.

Accumulation is not automatically equivalent to a large batch: batch normalization, randomness and per-microbatch reductions differ. For unequal microbatch sizes or masked token counts, normalize by the actual total valid-example/token count in the accumulation window, not always by a fixed accumulation factor. Flush the final partial window with its real denominator. Advance optimizer/scheduler at the intended optimizer-step cadence; clear gradients only at the boundary, not between microbatches you mean to sum. Test a small deterministic model against a single concatenated batch before scaling this recipe.

### CUDA FP16 step skeleton: adapt only after the FP32 step passes

The following uses current `torch.amp` APIs; verify that API in the installed version. Here `model`, `optimizer`, `x`, `y` already exist on the same CUDA device and `y` satisfies cross-entropy's class-index contract. Create one scaler before the loop, not a fresh scaler every step. This snippet is not an executed GPU test.

```python
scaler = torch.amp.GradScaler("cuda")
# Each iteration, without gradient accumulation in this minimal example:
model.train()
optimizer.zero_grad(set_to_none=True)
with torch.autocast(device_type="cuda", dtype=torch.float16):
    logits = model(x)
    loss = torch.nn.functional.cross_entropy(logits, y)
scaler.scale(loss).backward()
scaler.unscale_(optimizer)
# Optional clipping only if the training design calls for it:
torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
scaler.step(optimizer)
scaler.update()
```

The clipping threshold is an example hyperparameter, not a universal recommendation. Compare loss/gradient finiteness, validation quality and time/memory against FP32 before retaining AMP. Do not transplant this exact CUDA FP16 recipe to CPU/BF16/MPS without the relevant backend/API support and precision rationale.

## 4. Distributed training introduces data and collective contracts

Begin with a working single-device run. In DDP, every rank needs its intended device and compatible collective order. Shard data explicitly; map-style `DistributedSampler` needs `set_epoch(epoch)` before each epoch's iterator to vary shuffle order. Its padding can repeat examples when sample counts are not divisible by world size. Training may tolerate a documented padding policy; evaluation must remove duplicates or use an exact non-padding partition and an appropriate evaluation strategy. Uneven forward/backward schedules can hang if ranks enter different collectives, including implicit buffer synchronization.

Reduce metric sums and counts globally; averaging rank-level means is wrong for unequal counts. Iterable datasets need sharding across both ranks and loader workers. DDP's gradient averaging and local loss reduction interact with unequal local sample/token counts; derive the normalization rather than assuming the usual equal-batch recipe. Gradient accumulation with `no_sync` must enclose the relevant forward and backward passes and synchronize at the intended final microbatch.

A one-GPU pass does not validate multi-rank ordering, sampler uniqueness or checkpoint resumption. Record explicit distributed test gaps. Framework wrappers such as Lightning can own these mechanics, but do not run an extra manual optimizer/scaler/scheduler loop on top of automatic optimization. Preserve the project's namespace/API generation; do not migrate frameworks to solve an unrelated loss bug.

## 5. Resume and deploy deliberately

Use [reproducibility and artifacts](reproducibility-artifacts.md) for checkpoint state, loading trust and interrupted-run tests. Use [training performance](training-performance.md) only after the loss/gradient/evaluation gates hold. Precision, compiler, export and quantization changes require representative task metrics in addition to tensor closeness; low arithmetic error on random inputs does not validate model decisions.
