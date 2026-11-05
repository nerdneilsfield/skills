# Hardware evaluation norms

Use for architecture, circuit, accelerator, FPGA, and co-design papers. A hardware number without its conditions cannot be compared.

## Always state

| Item | What to write |
|---|---|
| Process | Node, foundry or "commercial", flavor (for example LP/GP), supply voltage, temperature, corner |
| Frequency | Target and achieved; the voltage it holds at |
| Power | Static and dynamic; at which voltage, frequency, activity, and workload; what is included (core only, with I/O, with memory, with PLL) |
| Area | Core or full die; with or without pads, SRAM macros, I/O; post-synthesis, post-layout, or die photo |
| Throughput and latency | Per workload, with batch size and precision |
| Accuracy | On the dataset, at the stated precision, with the same model across rows |
| Memory | On-chip size, off-chip bandwidth and its energy cost, if relevant |

## Evidence level

Label every number as one of: measured on silicon, measured on a board, post-layout simulation, post-synthesis estimate, RTL simulation, analytical model. Do not mix levels in one comparison row without saying so. A claim like "measured" requires the setup: chip count, sample variation, test equipment, how power was probed, and whether numbers are typical or best-case. Simulation papers say what the simulator assumes (technology library, wire model, activity source: vectors or random).

## FPGA

Give the exact device (part number, speed grade), tool and version (for example Vivado or Quartus release), clock constraint and achieved timing (WNS), and the resource table: LUT, FF, BRAM, URAM, DSP, with used counts and percent. Say whether the reported power is from the vendor estimator or from a board measurement, and which rail. Say whether the numbers are post-synthesis or post-implementation. Include the host interface and whether data transfer time is in the latency. Give the board, memory, and host if the comparison involves them.

## Normalised metrics and FoM

- Energy efficiency: ops per joule (TOPS/W). State what counts as an op (MAC = 2 ops or 1), the precision, and whether sparsity-skipped ops are counted.
- Area efficiency: throughput per mm2.
- Define any figure of merit in the paper with its formula and units. Name the source if you borrow it. Do not coin an FoM that the proposed design is built to win.
- Scaling across nodes: if you normalise to a common node, say the rule used (for example voltage and capacitance scaling) and show raw numbers beside normalised ones. Scaling rules are contested and reviewers will check them; present them as an aid, not as proof.
- Report efficiency at the operating point where it was measured; do not combine peak throughput from one voltage with lowest power from another.

## Comparison table fairness

- Same workload, precision, and accuracy, or say they differ and show the effect.
- Same scope: core versus system power, on-chip versus off-chip memory.
- Same evidence level per column, labelled.
- Include the strongest recent prior work, including designs that beat yours on one axis; show where you win.
- List sources for every other-work number (paper, table, or re-measured by you), and mark estimates you derived.
- Foot-note anything normalised, estimated, or not reported (use "N/R", not a guess).

## Breakdowns and scaling studies

Provide area and power breakdown (compute, memory, control, I/O), a sweep over the main design parameter (array size, bit width, frequency-voltage), and where utilisation drops. Show scaling to larger problems or configurations, with the trend and the limit. An ablation per architectural feature belongs in a co-design paper.

## Reproducibility

Say what is released (RTL, scripts, constraints, bitstream, test vectors, model weights) and under which licence, or why not. Venues may have artifact badges; check the current call.

## Venue note

Circuit venues such as ISSCC expect measured silicon with comparison tables; design-automation, architecture, and FPGA venues accept simulation or board results if the method is sound. Always check the target call.
