# Visualization and offline delivery

## Encode the question, not all available columns

Choose the plotted summary after validating its observation unit and denominator. A chart title should state what is measured; axes need units and transformation; a caption should state filtering, aggregation, sample counts, missingness and interval meaning. Maintain a small export table containing exactly the displayed quantities so a viewer can check them without reverse engineering pixels.

| Question | Useful starting form | Trap to avoid |
| --- | --- | --- |
| Compare category magnitudes | Dot plot or bars with denominator/count labels | Truncated bar baseline exaggerates length differences |
| Distribution or outliers | ECDF, histogram, box/violin plus sample size | Changing bin widths or smoothing hides structure |
| Change over ordered time | Line with explicit gaps and interval labels | Connecting missing periods implies measurements existed |
| Relationship | Scatter, hexbin or density with units | Overplotting masks density; association is not causation |
| Matrix of comparable values | Heatmap with labeled normalization | Per-panel normalization makes unlike magnitudes look equal |
| Uncertain estimates | Point plus named interval | Spread and confidence intervals answer different questions |

A bar-length encoding normally needs a zero baseline. A point/line plot may use a restricted range when explicitly labeled and appropriate. Log scales cannot display zero or negative observations; count/report those cases, choose a justified alternative such as a linear panel or symlog with disclosed threshold, and never silently replace zeros with an arbitrary epsilon. For signed deviations use a meaningful center and diverging palette; for monotone magnitude use an ordered perceptual scale. Categorical palettes should not imply numeric order. Use labels/markers/line styles redundantly so hue alone is not necessary. A named “colorblind-safe” palette is not proof that a rendered small chart is readable.

## Keep aggregation and uncertainty under control

Plotting libraries can estimate statistics automatically. If you have already aggregated a table, prevent a second aggregation or accidental confidence interval over group summaries. For seaborn functions that estimate, set the estimator and error-bar meaning deliberately, or plot precomputed values with an appropriate lower-level function. Show raw/distribution context when a mean hides multimodality. Handle repeated entities with a statistically appropriate uncertainty calculation before plotting; the plotting function cannot infer your experiment's independent unit.

Inspect counts and missingness alongside rates. Use compatible axes and units across panels when comparison is intended. Do not remove inconvenient outliers because they spoil an axis; investigate their validity, disclose exclusions, and use a second view or robust summary when needed. Smoothing, normalization and transformations must remain reconstructable. Exploratory figures can suggest hypotheses but do not retrospectively validate a pre-specified inference.

## Large data: reduce for the visual task

Millions of marks can exceed browser, serialization or graphics limits even after a fast query. First decide what detail the reader needs. Density/hexbin preserves concentration better than drawing every point; time bins can retain count, minimum, maximum and quantiles to reveal spikes rather than averaging them away. Sample with a documented seed/method only when the intended patterns survive; rare failure events may require stratified sampling or a separate full-resolution view. Do not use the downsampled figure data for full-dataset statistics unless that estimator and sampling design justify it.

Keep full analytical aggregates separate from display reduction. Bound category count through a documented top-k plus “other” calculation and reconcile totals. For interactive zoom, aggregate by visible scale when the application supports it; a standalone HTML cannot transparently query a private Python server that is no longer running. Altair's row guard encourages considering payload size; disabling it merely removes the guard. Preaggregate or use an appropriate installed transformer, and inspect what data the final spec embeds. Extra transformers are optional dependencies, not permission to install or fetch assets.

## Choose a stack for the destination

- **Matplotlib:** precise static output, batch/headless work and existing scientific workflows. Use object-oriented figures/axes; choose a noninteractive backend such as Agg before pyplot import in a dedicated batch process. GUI applications should not have their backend changed by a helper. Explicitly close figures in loops; retained figures/artists can consume memory even after saving.
- **Seaborn:** convenient statistical displays atop Matplotlib when its data/estimator semantics fit the analysis. It does not replace statistical design.
- **Plotly:** useful hover/selection and interactive HTML. A self-contained JS bundle increases file size; CDN mode needs network. Static export uses a distinct dependency path.
- **Altair:** declarative encodings and transformations that are easy to audit. Its serialized spec and data/JS dependencies must be checked for deployment/offline delivery.

Use the project's existing library when suitable. Supporting these choices does not mean installing all of them. A simple Matplotlib figure may be the most robust offline artifact; a genuinely interactive task may justify a larger HTML package.

## Export is part of the analysis

For headless Matplotlib, render with the installed backend and save at the actual delivery size. More DPI changes raster sampling, not data detail. Font files must already be available and licensed for the intended distribution. Verify Chinese glyphs, minus signs, math symbols, clipped legends and multi-panel labels in the final PNG/PDF/SVG, not only in the notebook. Avoid TeX rendering unless the local toolchain is present and required. SVG/PDF text/font behavior varies with settings; inspect portability on the target viewer. Close the figure in `finally` so a failed save does not retain it.

For Plotly HTML, `include_plotlyjs=True` embeds the plotting library, whereas `include_plotlyjs='cdn'` requires network access. Inlining JavaScript is not a blanket offline guarantee: remote image URLs, map tiles, fonts, MathJax or other resources may still be external. Inspect the generated document and open it with networking disabled. Treat the HTML as an active document; share only trusted generated code and approved data.

Plotly static export with Kaleido v1 depends on a compatible Chrome/Chromium already installed; a successful interactive display does not prove this path works. Do not auto-download a browser in an offline workflow. If absent, report the specific missing dependency, provide an available static alternative or keep the requested export pending. For Altair standalone delivery, verify the installed version's save/inline options and any required converter package, then test the resulting artifact disconnected. A referenced local JSON file must accompany the HTML and may face browser file-origin restrictions; bundled data or a supported local serving arrangement may be needed.

## Privacy and artifact verification

Interactive output often embeds more data than the visible marks reveal: hover fields, IDs, hidden traces and rows used for client-side filtering can remain readable in HTML/JSON. Remove unnecessary columns before creating the figure; aggregation is not automatically anonymization for very small groups. Do not embed credentials or signed private URLs. Review spreadsheet-friendly CSV exports for formula-like untrusted cells if recipients will open them in spreadsheet software; do not silently modify the analytical source data to address presentation risk.

Check the actual file format, dimensions, file size and existence, then visually inspect legibility and semantics. Compare plotted totals/labels against the saved summary. For interactive delivery test interactions offline in the intended browser, not merely that `write_html` returned. If only automated signature/schema checks were run, report that limited evidence. Keep raw-data provenance internally while sharing the minimum approved artifact; do not publish local paths, personal records or debugging dumps as “reproducibility metadata.”
