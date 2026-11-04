# Original finite record contract

Run from this asset directory with an existing Python 3.9+ interpreter:

```sh
python -I -B records.py
```

Expected: `record contract: PASS (no performance claim)`. This is self-contained; the runtime skills bundle does not need repository tests. Full source checkouts/separate validation companions additionally provide `tests/test_python_contract_example.py`.

`prepare_records(rows, unit)` accepts an explicit small list (at most 10000 entries), unique nonempty string IDs up to128 characters, exactly three finite Python int/float coordinates (not bool/string), and explicit `m`/`mm` units. It produces owned nested tuples in metres. A malformed tail raises before the caller assigns a candidate to its published state. Source-list mutation cannot change the output.

This example deliberately converts numbers to Python float: it is not suitable for exact integer identity or arbitrary-precision coordinates, and finite representation is not a domain accuracy proof. Unit conversion may round. IDs remain strings. It rejects extra keys to make this small teaching boundary explicit, not to prescribe a universal application schema. It does not parse external files, sanitize text, allocate unlimited batches, perform NumPy optimization, implement streaming rollback or prove thread-safe publication. Staging costs another bounded batch; large inputs need an explicit chunk/transaction contract. Self-checks remain active with Python `-O`.
