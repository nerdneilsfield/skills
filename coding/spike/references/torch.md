# PyTorch / deep-learning spikes

Goal: prove the training path can learn the intended signal, not stand up an experiment platform.

## Default

One file in the experiments repo, shared env (`uv add torch` only if it is missing). Fixed seed, tiny model, tiny data, print loss.

```python
# overfit_one_batch.py — shared env, no Lightning/Hydra/W&B
import torch, torch.nn as nn
torch.manual_seed(0)
x, y = torch.randn(8, 16), torch.randint(0, 3, (8,))
model = nn.Sequential(nn.Linear(16, 32), nn.ReLU(), nn.Linear(32, 3))
opt = torch.optim.Adam(model.parameters(), lr=1e-2)
for step in range(200):
    loss = nn.functional.cross_entropy(model(x), y)
    opt.zero_grad(); loss.backward(); opt.step()
    if step % 50 == 0 or step == 199:
        print(step, float(loss))
```

```sh
uv run python overfit_one_batch.py
```

## Recipe (in order)

From Karpathy, [A Recipe for Training Neural Networks](http://karpathy.github.io/2019/04/25/recipe/):

1. Fixed seed. Turn off augmentation and other fanciness.
2. Check loss at init (e.g. `-log(1/n_classes)` for softmax).
3. **Overfit one batch** of a few examples; drive training loss to its floor (often ~0). If it will not go down, stop and fix the path.
4. Only then try a slightly larger subset. Keep logging to `print` or a short list.

Shape the file like [nanoGPT](https://github.com/karpathy/nanoGPT): a short training loop you can read, not a trainer class. `wandb` is off by default there; keep it off here too.

## Skip unless the question is about them

Lightning, Hydra, W&B, Accelerate, a config store, dataset classes, checkpoint managers, `torch.compile`, distributed launch, AMP as a first step.

Leave `torch.compile` off until the eager path is correct — first-run compile time and graph breaks hide bugs. For a quick timing check after correctness: `torch.cuda.synchronize()` around `time.perf_counter()` on a few warmed iterations, or `torch.profiler` for one short span. A full `python-performance` / `python-ml` measurement contract is for a later campaign.

## Evidence boundary

A forward pass on random tensors that does not raise is not a training spike. It has not validated learning, labels, or the loss. `VALIDATED` for an overfit-one-batch spike means the printed training loss reached the floor you named, on that batch.

## After the spike

A multi-seed ablation with a proper split belongs to `algorithm-experiment` / `python-ml`, not this file.
