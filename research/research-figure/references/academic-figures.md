# Academic figures

Each entry gives when to use it, what to ask, the layout, and what to avoid. Ask the listed items when missing; everything else is a default. Random fields are only glyph choice and similar decoration. Route meanings are in `SKILL.md`.

## Method pipeline

Route: `image`, or SVG for exact content.

- **Use when:** the first figure of a method section, showing how the approach works from input to output in three to six stages. Not for layer-level detail (network architecture).
- **Ask:** method name; stages, each with name, operation, input, output; data modality, which decides the glyphs; skips, feedback, or branches.
- **Default:** 2:1 landscape, `paper-line`, English labels, one accent on the novel stage.
- **Layout:** left to right. Input thumbnail, equal stage blocks each with name and small glyph, output thumbnail. Tensor or data labels sit on arrows. Feedback runs below the main line. More than six stages becomes two tiers.
- **Avoid:** unequal blocks, more than four colours, thumbnails at mismatched resolutions, gradients that read as a slide deck.

## Mechanism diagram

Route: `image`.

- **Use when:** explaining how something changes over stages: a causal chain, reaction, failure path, or evolution. Not for a static device (schematic).
- **Ask:** phenomenon name; central object; stages in order, with the dominant process in a short phrase; branches or feedback; regions to emphasise.
- **Default:** 16:9, `textbook`, the same object redrawn across three to six stages.
- **Layout:** one row of stages with the object changing state across them. Process verbs sit on connecting arrows. Parallel paths are separate lanes that rejoin.
- **Avoid:** flames, glow, and explosions as drama; invented equations, constants, or temperatures; a full device cutaway.

## Network architecture

Route: `source`. Write SVG; shapes and tensor sizes are facts.

- **Use when:** showing layers, blocks, and tensor flow. Not for a method overview.
- **Ask:** model family; blocks and repeat counts; tensor shapes; skip, residual, and cross-attention links; output heads. Take these from the code or paper where you can.
- **Default:** landscape, `paper-line`, block colour means layer type with a legend, "× N" for repeats.
- **Layout:** one main axis. Encoder and decoder face each other for symmetric models. Shapes on the arrows. Skip links route around blocks. A dashed inset expands one repeated block.
- **Avoid:** missing or guessed tensor shapes, 3D cuboid stacks, six or more colours, skips crossing blocks.

## Scientific schematic

Route: `image`.

- **Use when:** one concept, device, or setup with a free composition. Not for sequential stages (pipeline, mechanism).
- **Ask:** the concept in one sentence; central entity; annotated parts; formulas to show, verbatim; intended look.
- **Default:** 4:3, `textbook`, central subject with leader lines to labels placed around it.
- **Layout:** subject at the centre, at most about eight callouts arranged on a clean margin, with an optional small inset for scale or a detail.
- **Avoid:** cartoon exaggeration, decorative texture, math set in text fonts. Set any formula as SVG or LaTeX, since generators garble it.

## Graphical abstract

Route: `image`, with no values.

- **Use when:** a single image summarises the paper for a journal page or a social post. Needs one sentence on what was done and found.
- **Ask:** the sentence; target venue, whose size rules you must confirm; problem, method, mechanism, main finding; label language.
- **Default:** 2:1, `editorial`, three panels reading problem, approach, finding.
- **Layout:** one visual story left to right with a single focal point. Words are limited to short phrases.
- **Avoid:** a compressed full paper, invented bars or curves, journal logos, "submitted to" stamps, glossy 3D renders.

## Multi-condition comparison

Route: `code`. Panels come from real data.

- **Use when:** one object, one view, one measure, across two to six conditions, as panels (a), (b), (c). Not for methods compared across samples (qualitative grid).
- **Ask:** the shared measure; the conditions; panel form; source data; grid shape.
- **Default:** shared axes and one shared colour bar, panel letters top left, a perceptually uniform colour map.
- **Layout:** equal panels on a tight grid. Condition names on the top edge or left edge only. One legend for all.
- **Avoid:** a separate range or colour map per panel, a dominant panel, mixed chart types, ranges chosen to flatter one condition.

## Qualitative comparison grid

Route: `code`. Cells are real outputs. Compose them; never generate them.

- **Use when:** rows of samples across columns of methods, including input, ground truth, and ours.
- **Ask:** samples and why they were chosen; methods with citations; cell type; zoom regions; result file paths.
- **Default:** three to six rows, at most six columns, ours marked and next to ground truth, same crop and scale across a row.
- **Layout:** strict grid with thin gutters. Column heads on top, row labels left. Zooms are the same region in every cell of the row, boxed in the accent colour.
- **Avoid:** different samples within a row, uneven cells, missing citations, picking samples only where ours wins without saying so.

## Overview poster

Route: `image`, with text set as SVG if labels are many.

- **Use when:** opening a thesis defence, proposal, or lab page: one project on one page. Not for a paper figure.
- **Ask:** topic; occasion; about five modules; the key question; object sketch; language.
- **Default:** 16:9, `editorial`, title band, key question beneath, equal modules, and goals at the end.
- **Layout:** title at the top, background on the left feeding into the central research modules, outcomes on the right or the bottom, with arrows for how the parts depend on one another.
- **Avoid:** a consulting-deck look, paragraphs inside modules, invented target percentages, one module outweighing the rest.

## Publication chart

Route: `code`, always. This skill departs from image-prompt chart templates here: no chart is generated, even as a mock-up that could pass for real.

- **Use when:** bars, lines, scatter, box, violin, or heatmaps of real values.
- **Ask:** data file; x and y with units; series; what error bars mean; sample size; column width.
- **Default:** matplotlib or similar with theme colours, white or off-white ground, line styles or markers as well as colour, vector output, the script saved as source.
- **Layout:** remove chart junk, label directly when series are few, state the error bar in the caption, one message per panel.
- **Avoid:** 3D bars and pies, rainbow colour maps for continuous values, truncated bar axes, missing units, implied precision from sparse data.
