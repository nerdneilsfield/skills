# Local helpers and examples

Run from this skill directory with the intended project's interpreter. Scripts do not install dependencies, fetch data, alter environments or load serialized models. Optional framework examples import their installed libraries and compute only small synthetic CPU workloads. Do not describe them as GPU or distributed validation.

## Declared split manifest audit (standard library)

Create an explicit metadata-only JSON array, for example:

```json
[
  {"id":"row-a","group":"entity-1","split":"train","time":10},
  {"id":"row-b","group":"entity-2","split":"validation","time":20},
  {"id":"row-c","group":"entity-3","split":"test","time":30}
]
```

```bash
python scripts/split_manifest_audit.py split.json --groups --time-gap 5
```

Contract: an explicit regular local file, not symlink; maximum 2,000,000 bytes, 2..20,000 rows; only `id`, `split`, optional `group` and `time` fields. IDs/groups are nonempty strings of at most 256 characters. Splits are `train`, optional `validation`, and `test`; train/test must be nonempty. IDs must be globally unique, including within a split. `--groups` requires every group and rejects groups spanning splits; groups may repeat within one split. Without it, group separation is **unchecked**, not automatically passed.

`--time-gap` requires a finite numeric time on every row, in one caller-declared common unit. It checks strict train-before-validation-before-test boundaries and a minimum boundary gap; zero still rejects equal timestamps. It does not sort or mutate records. Nonfinite/bool times, NaN JSON constants, duplicate object keys, unknown columns and unsupported structures are rejected. Omit `--time-gap` only when chronology is not the desired check; the output then marks it unchecked. Numeric timestamps do not encode label windows; choose the required gap from the data contract. Huge/adversarial files and concurrent filesystem mutation are outside the trusted metadata workflow; this is not a filesystem sandbox.

Exit codes: **0** declared checks passed, **1** overlap/chronology violations, **2** invalid/unreadable input. Output is bounded aggregate counts and limitations, never row/group identifiers. Passing does not prove leakage freedom: content duplicates, causality, feature availability, target contamination and distribution validity need separate inspection. Group checking can intentionally fail a legitimate known-entity future-prediction design; select checks from deployment semantics rather than forcing every mode.

## Classical ML example (NumPy + scikit-learn required)

```bash
python assets/classical_pipeline.py
```

Runs a 120-row synthetic classification example, a reserved 24-row test set, a two-choice training-only CV search, a baseline and assertions that scaling remains trained only on training rows. Outputs small JSON. This proves fitting/evaluation mechanics on IID data, not meaningful model quality or production schema safety. Missing dependencies are a prerequisite failure; use the environment skill to plan a compatible environment rather than auto-installing.

## Deep-learning example (PyTorch required)

```bash
python assets/torch_train_eval.py
```

Runs one CPU training step on 32 synthetic samples with finite loss/gradient checks, proves parameters changed, then checks `eval()` plus `no_grad()` produces graph-free outputs without parameter mutation. It fixes one CPU thread only in its own standalone process. It does not download datasets, save/load checkpoints, launch workers or probe CUDA. It does not benchmark, validate convergence, compare AMP, or test dropout/BatchNorm/DDP behavior. Adapt these assertions into the actual project's model; retain separate real-data and hardware gates.

Repository maintainers run `python -m unittest discover -s tests -p test_python_ml_example.py -v` from the repository root. That command is not available in a runtime-only exported skill package. Optional-dependency tests explicitly SKIP when the installed dependency is absent; an import failure in an installed broken package is a failure, not a silently accepted skip.
