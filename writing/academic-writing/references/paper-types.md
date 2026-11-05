# Paper types

Pick the closest type; hybrids take the evidence burden of each part they claim.

| Type | The claim is | Reviewers look for | Typical structure |
|---|---|---|---|
| Algorithm | A method is more accurate, robust, or cheaper on a stated task | Strong baselines, fair protocol, ablation, failure cases, runtime | Intro, related work, problem, method, experiments, limits |
| Hardware, architecture, circuit | A design reaches a better power, performance, area, or accuracy trade-off | Measured or credibly simulated numbers, fair comparison table, breakdowns, what is new in the design | Intro, background, architecture or circuit, implementation, results and comparison, conclusion |
| HW-SW co-design | Joint choices beat either side alone | An interface or cost model that explains the coupling; ablation of each side; end-to-end numbers on real hardware | Intro, bottleneck analysis, algorithm side, hardware side, joint evaluation |
| System | A working system solves a deployment problem | Design rationale, real workload, scalability, lessons, comparison with alternatives | Intro, requirements, design, implementation, evaluation, experience |
| Survey | The field is organised, compared, and its gaps named | Search method, inclusion rules, taxonomy, fair comparison, open problems | Intro, scope and method, taxonomy, analysis, challenges |
| Journal extension | A conference paper is substantially extended | New technical content, new experiments, disclosed overlap | Same as base type plus an explicit delta |

## Co-design

State the coupling, not just two halves. Show the numbers that exist only because both sides were changed: a quantisation scheme chosen because of the datapath, a sparsity pattern chosen because of the memory system. Evaluate algorithm change, hardware change, and both. If the algorithm runs on a general-purpose platform, report that baseline on the same workload.

## SLAM, LiDAR, and autonomous driving papers

Also common in this field: a method paper judged on public sequences plus a real-robot or vehicle run. Name the sequences, the ground-truth source, the alignment and metric definition (ATE, RPE, with or without scale alignment), the sensor configuration, and the onboard compute the runtime refers to. Real-world runs need the environment, trajectory length, and what failed.

## Journal extension

- Say what is new: venues often expect a substantial fraction of new technical content (figures such as 30 percent are folklore); check the journal's own rule, never memory.
- Cite the conference version, describe the overlap in the cover letter and in the paper, and list the new material. See `integrity.md`.
- New content should be method and evidence, not longer related work and more figures of the same result.
- Check the copyright and similarity-check rules of both venues.
