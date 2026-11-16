# SLAM spikes

Prototype in **Python first**, on a **short** sequence, with one evaluation number. Port to C++/CUDA only after the idea is `VALIDATED` or you hit a hard performance/layout question.

## Default stack (shared Python env)

Add to the shared env only what you need:

| Need | Tool |
| --- | --- |
| Geometry / factors | [GTSAM](https://gtsam.org/) Python (`uv add gtsam` if missing) or [PyPose](https://github.com/pypose/pypose) |
| Vision / IO | OpenCV, NumPy |
| Point clouds / ICP / viz | [Open3D](https://www.open3d.org/docs/release/getting_started.html) |
| Trajectory error | [evo](https://github.com/MichaelGrupp/evo) (`evo_ape`, `evo_rpe`) |

One idea, one script (or one short directory) that: reads a clip, runs the method, writes a TUM/KITTI trajectory, prints ATE/RPE.

## Data

Do not ingest a whole benchmark for a spike.

- KITTI: a few hundred frames of one sequence, not 00 end-to-end.
- TUM RGB-D: a short walk (e.g. a `freiburg1_*` clip), not every room.
- EuRoC: one easy MH/V1 segment, not the full MAV suite.
- Synthetic / a recorded bag slice is fine if it has ground truth.

Hardcode calibration, paths, and the frame range.

## Success signal

Write `gt.txt` and `est.txt` (TUM or KITTI) and run evo. Docs and formats: [evo](https://michaelgrupp.github.io/evo/).

```sh
evo_ape tum gt.txt est.txt --align --t_max_diff 0.05
# or: evo_rpe kitti gt.txt est.txt --delta 1 --delta_unit m
```

`VALIDATED` means the metric you named (usually ATE RMSE after alignment) landed in the range you set on **that clip**. It does not prove loop closure, relocalization, or every sequence.

## Skip

ROS workspace / colcon / catkin for a first check (read a bag with Python if needed). Ceres/GTSAM/g2o C++ projects, `cpp-project-init`, full KITTI eval server submissions, RViz unless visualization *is* the question. Do not start `algorithm-experiment` or `paper-reproduce` unless the user asked to claim a paper number or run a seed-averaged campaign.

If the spike later needs C++, use `references/cpp.md` / `references/cuda.md` on the same idea name, still in the experiments repo, still no new project.
