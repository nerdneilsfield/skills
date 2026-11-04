# Local tools and worked example

## Bounded CSV contract audit

From this skill directory, with an explicitly authorized local UTF-8 CSV:

```sh
python scripts/csv_contract_audit.py /approved/input.csv --key event_id --numeric duration_ms
```

The standard-library tool is read-only and makes no network calls. It counts rows, columns, blank key rows, repeated nonblank keys after the first occurrence, and missing/invalid/nonfinite numeric cells. Distinct repeated `--key` options form a composite key; duplicate selectors are rejected. Selectors and header names are limited to 256 characters, and selector counts cannot exceed the column limit. Repeated `--numeric` selects numeric checks. Blank means empty/whitespace; it does not infer that strings like `NA` are missing. Keys are compared exactly without trimming, case-folding or numeric coercion. The caller must define domain normalization separately.

Default limits are 4 MB, 100,000 rows and 256 columns. `--max-bytes` and `--max-rows` can raise limits only within hard ceilings of 32 MB and 1,000,000 rows. It reads at most byte-limit plus one before decoding, rejects malformed widths/duplicate headers, and fails rather than returning a misleading partial summary. Key tracking consumes bounded but potentially larger-than-input Python memory. This is a small-file structural check, not a large-data profiler or a sampling estimate. It does not validate units, timezones, ranges, missingness mechanisms or database relations.

The JSON report omits cell values and input paths, but selected column names and counts may still be sensitive. Do not automatically transmit the report. CLI errors deliberately avoid quoting raw parsing exceptions. Numeric validation uses `float` only to recognize syntax and finiteness, not to preserve monetary precision or validate exact integers. If domain precision matters, define a schema-specific parser instead. Symlink inputs are rejected. A nonblocking open plus file-descriptor type check rejects FIFOs/devices without reading; on platforms exposing `O_NOFOLLOW`, the open also rejects a raced symlink. Use a trusted stable regular file; this helper is not a hostile-filesystem isolation boundary on every platform.

Exit 0 means structural parsing completed, not that every count is acceptable; the agent must compare counts with the contract. Exit 2 means rejected input. The tool does not alter CSVs, remove rows, install packages or infer repairs.

## One coherent runnable example

```sh
python assets/analysis_example.py
python assets/analysis_example.py --png /approved/new-summary.png
```

The first command requires already installed pandas. The second additionally requires Matplotlib and writes a new PNG only; it refuses an existing path. No package installation, remote data or browser is used. Run from a dedicated batch process because the example selects Agg for headless rendering. If the default Matplotlib cache location is read-only, explicitly set `MPLCONFIGDIR` to an approved writable temporary directory for this process; do not modify the user’s home configuration or hide unrelated rendering failures.

Four synthetic events belong to three subjects. Cohort A contains three eligible events: one success, one failure and one unknown; cohort B has one known success. The result is **A: 1/2 observed successes with 2/3 outcome coverage**, not 1/3 and not a subject-level probability. B: 1/1 with 1/1 coverage. The tiny dataset supports descriptive demonstration only, not evidence that B is genuinely better.

`analyze` copies inputs, checks event identity and dimension uniqueness, rejects null keys, parses offset-bearing fixture timestamps, validates many-to-one merging and rejects uncovered subjects. Group aggregation keeps eligible, known, success and unknown counts. It leaves the rate undefined when no outcomes are known. The chart labels observed/eligible counts and intentionally omits inferential error bars because no independence model is specified.

When adapting this code, define the timestamp contract first: the function's UTC parse is appropriate to these offset-bearing fixtures, not arbitrary naive local timestamps. Decide whether unmatched subjects should be rejected, retained as an explicit unknown cohort, or excluded with reported coverage; changing that choice changes the target population. Preserve the assertions that express your chosen contract.

## Regression and manual checks

Only in a full repository checkout or the separate validation companion (not the runtime skills ZIP), `tests/test_python_data_analysis_example.py` checks rejection of duplicates/null keys/unmatched dimensions, the missing-outcome denominator, CLI limits/schema errors/value nondisclosure, and real PNG creation when Matplotlib is installed. Optional frameworks are skipped only when absent; installed-framework failures remain failures. The test suite does not exercise Polars, DuckDB, Arrow, Plotly or Altair.

For a new analysis, add fixtures for empty data, all-missing groups, timezone boundaries, duplicated effective-dated records and representative scale. Validate row-accounting invariants and intended time-order sensitivity. A real PNG signature confirms encoding, not readability; inspect final labels, gaps, axes and glyphs. Interactive exports require their own offline browser test. Do not advertise these tests as a full visualization backend certification.
