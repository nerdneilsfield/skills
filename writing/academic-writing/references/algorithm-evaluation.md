# Algorithm evaluation norms

For methods in perception, SLAM, LiDAR, planning, learning, and optimisation.

## Setup block

State, in the paper or appendix:

- Datasets with version and licence, splits (train, validation, test) and how they were made. Tuning on the test set is not allowed; if a benchmark only has a server-side test, say how many submissions were made.
- Sequence-based tasks (SLAM, odometry): list sequences used and those left out, with reasons.
- Preprocessing, augmentation, and any data you filtered.
- Baselines: the strongest recent methods, the code or numbers' source, whether you re-ran them, and with what tuning budget. Same data, same preprocessing, same metric code.
- Implementation: language, framework, hyperparameters and how chosen, initialisation, number of runs.
- Compute: hardware (CPU, GPU, embedded board, power mode), batch size, precision, software versions.

## Metrics

Define each metric by formula or by citation to its standard implementation, and state any variant: for trajectory error, which alignment (SE(3), Sim(3), none), whether per-sequence or pooled, and the unit. For detection or segmentation, the IoU threshold and averaging. For runtime, what is timed: the full pipeline or the module, with or without I/O and preprocessing, and warm-up. Say whether lower or higher is better in the table header.

## Seeds and variance

Single runs hide variance. Three things are reported separately; none replaces another.

- Algorithm randomness: mean and spread over several seeds (standard deviation or confidence interval, and which), or state that the method has no random component.
- Measurement repeatability: repeated timing and power runs, even for a deterministic method.
- Sample coverage: more than one scene or sequence, even for a deterministic method.

Aggregate seeds within each scene first, then compare across scenes. The independent unit is the scene, not scenes x seeds; pooling them as N is pseudoreplication and makes tests look stronger than they are. When differences are small, test significance at the scene level or call them equal.

## Ablation

Remove or replace one component at a time. Show each row on the same data and protocol. Ablate the claimed contributions, not arbitrary settings. Show a sensitivity study for the key hyperparameter. If two components interact, show the pairs.

## Runtime and efficiency

Always give runtime with the hardware and the measurement method. A speedup claim names the baseline, the hardware, and the workload. Memory, energy, and parameter count are reported when the claim is efficiency. Compare at equal accuracy or show the accuracy-cost trade-off curve. Real-time claims state the frame rate against the sensor rate.

## Qualitative evidence

Examples are not evidence for a general claim. Show typical and failure cases and say how they were chosen. Mark whether the figure uses test data.

## Real-world and field tests

Describe platform, sensors, environment, duration or length, conditions (night, rain, dynamic objects), and the number of trials. Report failures. A single successful demonstration is a demo, not an evaluation.

## Fairness checklist

- Baselines have comparable tuning effort.
- Training data and pretraining are equal or the gap is stated.
- Reported numbers from other papers use the same protocol; otherwise re-run or note.
- No selection of the best seed or best checkpoint on test data.
- Negative results and cases where the method loses are reported.
