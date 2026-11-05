# Final review

Three views, for long guides, after the full build. Mark each item pass or fail, with the page and the evidence. Fix each failure before reporting.

## Editorial

- Every page does what the plan promised, and nothing the plan required was dropped.
- Pages run shallow to deep; none relies on a term or idea introduced later.
- Each stage ends with a quiz or task that asks the reader to apply the idea, not repeat a sentence.
- Prose carries the explanation. Blocks earn their place: try reading the point as a sentence, and if that works, cut the block.
- Claims are traceable. Each excerpt was reread against its `line`, inferred steps are marked `verified: false`, and paper claims keep authors and analysis apart.
- One language throughout, including captions, labels, and quiz options.
- Every `⚠ 未指定` is either filled from a source or left on purpose and named in the report. Every entry in `assumptions` is still true.

## Visual

- Colours stay in the template's palette and fonts in its stack. Anything from `--keep` uses the same variables.
- Figures share a style, keep their labels legible, and do not repeat what a nearby block already shows.
- Walk the signs in `references/failure-patterns.md`.
- Desktop and phone widths both read well: no clipped text, no sideways page scroll, wide tables and code scroll inside their own box.
- Light and dark colour schemes both hold up, including figures on their ground.

## Technical

- `--check` passes and each warning is resolved or accepted; both the default and any promised `--offline` build succeed.
- The console is clean on every page. CDN failures count when the reader is told the page needs network.
- Every flow plays to its last step, every quiz answers, the graph mounts and filters, and formulas and Mermaid render.
- Images have real `alt` text and each is under the size warning.
- Page ids, tab order, and any numbers in titles match `plan.md`. Read them from the built tabs, not from the data.
- Run `references/browser-acceptance.md`.
