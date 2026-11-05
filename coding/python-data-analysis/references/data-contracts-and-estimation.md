# Data contracts and estimation

## Start with the observation unit

Suppose a table records processing events and a dimension table assigns subjects to cohorts. The question “which cohort succeeds more often?” is incomplete. It might mean event-weighted success, equally weighted subject success, probability of any success per subject, or success within a fixed exposure window. Repeated events give busy subjects more weight in the first estimate. Choose the estimand before grouping; report both row and independent-entity counts. Do not invent independence from a large row count.

Keep a compact contract beside the analysis: source identity, snapshot/time window, row grain, key, measurement units, valid domain, null meanings, timezone, expected relationship to other tables and exclusion policy. Preserve original fields while deriving cleaned fields where investigation is needed. A column called `id` may contain leading zeros or values too large for exact float representation: read identifiers as strings, not inferred floats. A blank outcome is not automatically failure; a missing amount is not automatically zero.

## Parse deliberately, and make missingness visible

Use explicit input columns and dtypes where supported. Nullable integer/boolean types preserve missing values without converting identifiers or flags to floating approximations. Declare CSV delimiter, encoding, decimal conventions and known missing tokens rather than assuming an inference engine understands the source. Count invalid conversions separately from originally missing values. For example, `errors='coerce'` is useful to collect bad numeric/date rows only if a subsequent assertion or report exposes newly coerced values; it is not a data-cleaning policy by itself.

On pandas 3.0 or later: parsed datetimes default to `datetime64[us]`, so `astype('int64')` gives values 1000x smaller than `ns` code expects; call `as_unit()` first. String columns infer `str`, so `dtype == object` checks stop matching. Chained assignment never writes; assign through `.loc` on the object itself.

For times, separate **localizing** a naive wall-clock value from **converting** an already timezone-aware instant. If naive data were recorded in Shanghai, assigning UTC shifts the intended instant by eight hours. Require the source timezone; explicitly resolve or reject daylight-saving ambiguous/nonexistent local times. Offset-bearing input can be converted to UTC for ordering, while business-day aggregation may require conversion to a named local timezone first. Record bin closure/labels and window boundaries. An event at midnight and a DST transition belong in regression fixtures. `to_datetime(..., utc=True)` normalizes offset-bearing timestamps but assumes naive ones are UTC; it does not infer their provenance.

Do not silently sort away a causality error. Time-window joins need sorted keys, permitted direction, matching group/entity and tolerance. Nearest-time matching can select a future measurement: for online features use only information actually available at prediction time. Keep outcome availability time distinct from event time. Cross-validation, preprocessing fit and predictive leakage details belong to `python-ml`.

## Join without multiplying the population

Before a merge, write the relation in words: many events to one current dimension record; one event to several measurements; or intentional many-to-many expansion. For a key with `a` left rows and `b` right rows, an equality join can emit `a*b` rows. “It fits in memory” does not make that multiplication correct. Check key uniqueness on the side promised unique, null-key policy, overlapping column names, and coverage before aggregation.

For pandas, specify `on=` rather than letting shared column names become accidental keys. Use `validate='many_to_one'` for the event/dimension example and `indicator=True` for coverage. Null keys on both sides can match each other in pandas, unlike usual SQL null equality; reject or deliberately separate unknown keys before joining. `validate='many_to_many'` permits expansion and is not a protective uniqueness check. For a left many-to-one join, assert unchanged left row count and inspect unmatched rows. Do not repair failed validation with `drop_duplicates()` unless the business rule chooses one version deterministically; effective-dated dimensions often require time-aware matching instead.

A repair is complete when both the small counterexample and representative data satisfy the relation, row counts and totals. Add a fixture with duplicate right keys, unmatched keys, nulls and competing versions so the same mistake cannot quietly recur after a schema change.

## Aggregate with explicit denominators

Track at least eligible rows, observed outcomes, successes and exclusions. In pandas `size` counts rows while `count` excludes missing entries of the counted column. Choose `dropna` explicitly so missing group keys are either reported or deliberately excluded; choose `observed` explicitly for categorical groups so library-version defaults do not alter empty-group output. Use a separate missing-category label only if it cannot collide with a real category.

If cohort A has 1/1 successes in batch 1 and 0/99 in batch 2, averaging batch rates gives 50%; pooling successes/eligible events gives 1%. Both can answer different questions, but neither may be mislabeled as the other. For chunking, combine numerator and denominator, not the chunk means. Preserve zero-denominator groups as undefined, not zero. An all-missing group's reduction may produce a numeric zero: the known count must gate its interpretation. A weighted mean needs a defined weight, valid domain and a positive total weight; negative survey/model weights require their specific method, not an ad hoc formula.

Ratios and normalization can hide changing composition. Compare groups within important strata and examine exposure/coverage before calling a pooled trend causal. Report excluded/missing proportions by group: a 95% success rate observed for 5% of a group is not directly comparable to 95% complete observation. Sensitivity bounds for unknown binary outcomes can be shown as `successes/eligible` through `(successes+unknown)/eligible`; label them as missing-outcome bounds, not confidence intervals.

## Descriptive spread is not inferential uncertainty

A standard deviation describes dispersion of observations. Standard error or a confidence interval concerns an estimator under assumptions. A percentile range describes part of the empirical distribution. Select the intended quantity and name it in the caption rather than accepting a plotting default. Seaborn's `errorbar` controls several different quantities; modern `errorbar` differs from older `ci`, so check the installed version when adapting code.

Repeated observations within subject, scene, session or time window are correlated. Row-wise resampling can make uncertainty unrealistically narrow; use entity/block resampling or an appropriate statistical model where justified. A resampling seed makes a computation repeatable, not valid. Tiny samples, selection bias, multiple comparisons and exploratory subgroup selection constrain any claimed conclusion. For a simple descriptive request, show distribution, sample counts and missingness rather than fabricating significance tests. When inference is requested, state assumptions, hypothesis family, effect size and uncertainty; distinguish association from a causal claim.

## Verification before visual polish

Use a hand-computable fixture covering missing, duplicate, empty and zero-denominator cases. Assert accounting: input = included + excluded where categories are mutually exclusive, join cardinality, and aggregate counts reconciling with contributing records. Check input-order invariance where order should not matter, and exact time boundary behavior where it should. Compare alternative implementations on the same fixture before accepting a “faster” result. Round for presentation only, after calculations and comparisons.
