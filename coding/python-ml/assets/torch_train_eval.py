"""Bounded CPU-only train/eval contract example; no downloads or checkpoints."""
import json
import torch


def run():
    torch.manual_seed(31)
    torch.set_num_threads(1)
    device = torch.device('cpu')
    x = torch.randn(32, 4, device=device)
    y = (x[:, 0] > 0).long()
    model = torch.nn.Sequential(torch.nn.Linear(4, 8), torch.nn.ReLU(), torch.nn.Linear(8, 2)).to(device)
    optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
    original = [p.detach().clone() for p in model.parameters()]
    model.train()
    optimizer.zero_grad(set_to_none=True)
    logits = model(x)
    loss = torch.nn.functional.cross_entropy(logits, y)
    assert torch.isfinite(loss), 'nonfinite training loss'
    loss.backward()
    assert all(p.grad is not None and torch.isfinite(p.grad).all() for p in model.parameters())
    optimizer.step()
    changed = any(not torch.equal(before, after) for before, after in zip(original, model.parameters()))
    assert changed, 'optimizer did not update any parameter'
    trained = [p.detach().clone() for p in model.parameters()]
    model.eval()  # Module behavior; no_grad below independently controls graph creation.
    with torch.no_grad():
        evaluated = model(x)
        accuracy = (evaluated.argmax(dim=1) == y).float().mean().item()
    preserved = all(torch.equal(before, after) for before, after in zip(trained, model.parameters()))
    assert preserved and not evaluated.requires_grad
    return {'torch_version': torch.__version__, 'device': str(device), 'samples': len(y),
            'parameters_changed': changed, 'evaluation_preserved_parameters': preserved,
            'evaluation_requires_grad': evaluated.requires_grad, 'accuracy': accuracy,
            'scope': 'CPU train/eval mechanics only; training-set accuracy is not validation quality'}

if __name__ == '__main__':
    print(json.dumps(run(), sort_keys=True, allow_nan=False))
