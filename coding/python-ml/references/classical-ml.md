# Classical modeling: separate information before selecting an estimator

## 1. Define the example you are allowed to learn from

Suppose each row is an observation used to predict an event in the following week. A row ID is not necessarily an independent example: multiple rows can belong to one person, machine or session. First specify what deployment means: new entities, later observations of known entities, or both. This determines a split, not the model API.

- Independent, exchangeable rows: random splitting may be appropriate; stratification preserves class proportions but does not fix dependence.
- New entities: hold out whole groups. Entity/session identifiers must not straddle the boundary. Group folds must contain enough distinct groups and classes to evaluate the selected metric.
- Future prediction: train on earlier observations and evaluate later ones. A gap must cover the actual label/feature window overlap, not an arbitrary number of rows. Unequal time intervals require explicit fold construction if elapsed-time horizons matter.
- Both constraints: construct folds satisfying group and temporal rules together. Passing `groups` into a random split or checking chronology alone does not establish this.

Reserve the test set before model choices. Audit exact duplicate IDs and known group/time boundaries using the bundled manifest helper; then inspect content duplicates, near duplicates and feature generation separately. The helper cannot detect a target-derived column, duplicated images with different names or a future-computed statistic.

**Symptom:** CV is excellent, live performance collapses. **Evidence:** compare group membership, timestamps, duplicate content and feature availability across folds. **Fix:** rebuild the separation and fit only within each training fold; rerun all selection. **Verify/prevent:** keep immutable split IDs and tests for the boundary. Do not “repair” only the final test while retaining hyperparameters selected through leaked CV.

## 2. Make every learned transformation part of fitting

Imputation values, normalization statistics, categorical vocabularies, target encoding, feature selection and dimensionality reduction are learned state. Their `fit` belongs inside the training fold, even if a transformation does not consume labels. A scikit-learn `Pipeline` passed into CV is cloned and fitted per fold; fitting a scaler first on all development rows silently bypasses this protection. Target encoding additionally needs an appropriate out-of-fold training scheme: a pipeline alone cannot make a leaky custom transformer safe.

Use a `ColumnTransformer` when columns need distinct treatment; make unknown-category and missing-column behavior explicit. Preserve training feature names, order, dtype and units at inference. A model accepting an array of the right width may still receive swapped columns. Never include a feature merely because it is present in the offline table: availability at decision time is the contract.

The complete local example [classical_pipeline.py](../assets/classical_pipeline.py) uses synthetic IID data, reserves a test set, fits scaling inside a small CV search, compares a dummy baseline and asserts the final scaler learned only the training mean. It is a runnable explanation, not a template for group/time problems.

## 3. Select against the decision, not the largest score

Start with a simple baseline that exposes the task's difficulty: constant/majority prediction for classification, a mean/median for regression or a naive temporal forecast for forecasting. Compare with a model whose complexity fits data size and latency. Tune only a bounded, justified search on development data. Nested CV is useful when reporting the generalization of the selection procedure; a separate untouched test set serves a different purpose. Repeatedly examining that test to change features turns it into development data.

For imbalance, report class supports and confusion counts, not accuracy alone. Choose recall/precision or PR-oriented metrics for the actual cost of misses and false alarms; balanced accuracy and macro averages answer different questions. AUC assesses ranking, not the operating threshold or probability accuracy. Validate that folds have the labels needed for the metric and report undefined cases instead of silently converting them into favorable scores. For regression, compare unit-bearing errors and tail/subgroup behavior; a lower overall error can hide a critical regime.

Tune decision thresholds on development evidence, independently of the final evaluation. If probabilities drive downstream risk/cost decisions, assess calibration on out-of-sample predictions; fit calibrators without reusing their model's in-sample predictions. Reliability plots and proper probability scores complement discrimination; a Brier score alone mixes calibration and discrimination. Calibration cannot repair a changed deployment distribution.

Class weighting/resampling changes training behavior, and oversampling before CV can duplicate information across folds. Put resampling in the training-fold procedure, preserve realistic validation prevalence, and measure recall, precision and calibration again. Do not claim a universally optimal class weight.

## 4. Validate the whole deliverable

Freeze the selection procedure and evaluate once on the reserved set. Report counts, uncertainty appropriate to independent units, subgroup behavior, thresholds and failure examples. Repeated rows are not independent bootstrap samples; resample at the entity/time-block level when the design warrants it. For clustering/embeddings, a pleasing plot is not independent label validation; document distance/scale choices, stability across resampling and the meaning of any external labels.

Before deployment, test the same preprocessing and estimator together on a small known fixture, unknown categories, missing/invalid values and reordered columns. Record quality and inference time together. Route artifact trust/version concerns to reproducibility and artifacts (`reproducibility-artifacts.md`), rather than loading an arbitrary joblib file to “see what is inside.”
