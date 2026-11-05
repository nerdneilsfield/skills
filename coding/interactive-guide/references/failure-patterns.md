# Failure patterns

How generated pages tend to go wrong in this template. Each is a default with room for exceptions. Fix what matters; do not paste this list into a report.

## Layout

- **Everything in a box.** Callouts, quizzes, and claims stacked until the page reads as a card wall. Prose and whitespace should carry most of it; keep a container only when it means something.
- **Same shape on every page.** Intro, three bullets, callout, repeated tab after tab. Let the content choose: a page that is one good flow is fine.
- **Rounded, shadowed, gradient.** Pills, soft shadows, purple gradients, and glass panels belong to generic dashboards. This template uses thin rules, square corners, and flat colour.
- **New colours.** A bright blue or green from outside the palette. Use the CSS variables; colour says state, such as verified, inferred, or warning, and is not decoration.

## Writing

- **Label noise.** An eyebrow above each heading, fake version numbers, or a progress figure that measures nothing. Keep `level` only when it is a real stage.
- **Slogan headings.** "Unlocking the power of X" tells the reader nothing. Title a page with its question or its finding.
- **Filler summary.** A closing callout that repeats the page. Delete it, or say what to do next.
- **Invented proof.** Benchmarks, user counts, dates, or quotes with no source. Use `⚠ 未指定` or leave it out.
- **Emoji as icons.** They read as decoration. `⚠` is reserved for the missing-fact marker.

## Figures and diagrams

- **Decorative image.** If deleting a figure loses no understanding, delete it.
- **Style drift.** Figures that change palette, line weight, or lettering between pages. Reuse one prompt description, and redraw the odd one out.
- **Generated numbers.** Charts or exact values in a generated image. Those belong in `compare`, code, or a real plot.
- **Diagram restates the prose.** A flow of three boxes that says the sentence above it. Show branches, order, or relations that text handles badly, or cut it.
- **Graph for its own sake.** A knowledge graph of ten nodes gives less than a list. Use one when the reader needs to explore.

## Motion and interaction

- **Spectacle.** Animation that shows no cause or order. Motion here traces a call; anything else stays still.
- **Quiz as a speed bump.** A question answered by the previous line. Ask the reader to apply the idea, or drop it.
- **Controls with nothing behind them.** A toggle that changes little, or a flow with one step. A plain block is better.

## Slides

- **Slide as wall.** A long block shrunk until it is small. Split the block, or leave it for reading mode.
- **Every block a slide.** Short blocks that make one point should be merged in the data first.
