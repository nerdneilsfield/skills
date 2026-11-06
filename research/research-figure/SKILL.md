---
name: research-figure
description: "Use when the user asks for an academic or technical figure on any agent, with or without image generation: method pipeline, mechanism, network architecture, schematic, graphical abstract, comparison, poster, publication chart, system architecture, sequence, state machine, flowchart, ER, topology, or mind map. Picks a backend by detection, saves the prompt first, inspects every output, and delivers a compressed file with its editable source. Figure rules live here; data cleaning, joins, and statistics behind a publication chart belong to python-data-analysis. Not for analysing that data, inserting figures into a manuscript (academic-writing), or a paper's own published figures (qi-read-paper)."
license: MIT
compatibility: Scripts need only python3. Image generation depends on whatever backend is detected; no backend is required, since SVG and Mermaid always work. Rendering and compression use whichever of a browser, rsvg-convert, Inkscape, mmdc, cwebp, pngquant, or ImageMagick is installed.
metadata:
  author: DengQi
---

# Research figure on any agent

A figure is a prompt or source you can rerun, plus a file you have looked at. Nothing here depends on one image model. Paths are relative to this skill.

```
- [ ] 1 Route the type      - [ ] 4 Write prompt or source
- [ ] 2 Intake              - [ ] 5 Generate as a batch and inspect
- [ ] 3 Resolve the backend - [ ] 6 Deliver
```

## 1. Route the type first

Read the one reference you need: [references/academic-figures.md](references/academic-figures.md) or [references/technical-diagrams.md](references/technical-diagrams.md). Each type has a route, and the route limits the backend:

| Route | Types | Made with |
|---|---|---|
| `code` | publication chart, any figure with measured values, qualitative grid cells | Plotting code, SVG, or real result images. Never generated |
| `source` | sequence, state machine, ER, flowchart, network topology, mind map, network architecture | Mermaid or SVG first. A polished render may follow from it |
| `image` | method pipeline, mechanism, schematic, graphical abstract, overview poster, system architecture | Any backend, with an editable source when practical |

A named backend does not lift the `code` route. If the user asks for generated data, explain and plot it instead; For a publication chart, this skill owns the figure rules (theme, labels, export) and `python-data-analysis` owns cleaning the data and the statistics; `dataviz` can help with chart design if installed.

Hybrid figures, as in recent papers, put the intuition beside the components: panel (a) shows the idea, panel (b) the architecture, in one figure with shared colours, so a colour means the same thing in both. The structure panel keeps the `source` route; the intuition panel may be `image`. Compose them in SVG. Generate the intuition with no text at all and set every label as SVG text above it. Start from [assets/example-figure.svg](assets/example-figure.svg).

## 2. Intake

Sort each field of the chosen type:

- **Required:** changes what the figure claims, such as stages, labels, relationships, target venue. Ask.
- **Default:** safe to fill, such as aspect ratio, style, palette, label language.
- **Random:** decorative only, such as which glyph stands for a stage. Never a fact.

Scan for every missing required field at once and ask in one batch, each with a recommended default. Take facts from the paper or code first and ask only for what is absent. If unattended, decide, and record each assumption in the prompt file and the report. Never invent a label, value, or citation to fill a gap; leave it out and say so.

## 3. Resolve the backend

Take the first that is really available. Detect, never assume; do not name a tool you have not seen in this session.

1. The user names one for this request.
2. A project preference: `.research-figure.json` with `{"backend": "...", "theme": "..."}`, or a line in `AGENTS.md` or `CLAUDE.md`.
3. The running agent's own image tool, found in its tool or skill list. Codex, Grok, and Antigravity usually have one; Claude Code does not. Check rather than trust this sentence.
4. Another available agent that has one. Hand off with the prompt file and an absolute output path, using `agent-brief`, then accept the file with `agent-verify`. A CLI on `PATH` proves nothing until a file comes back.
5. The user's drawing MCP, found in the MCP tool list.
6. SVG or Mermaid, written by you. This always works.

Report which backend was used and why earlier ones were skipped. A pinned backend that is missing is reported, then falls through; it is not silently replaced.

## 4. Prompt or source

Combine **type** (structure) × **style** (rendering) × **palette** (colour). Fill [references/prompt-skeleton.md](references/prompt-skeleton.md), which lists the styles and carries no tool syntax.

The default palette is Japanese traditional colours: ink and indigo with a vermilion accent on off-white, in [assets/themes/japanese.json](assets/themes/japanese.json). A theme is a JSON file with `light` and `dark` maps of CSS variables, so a new palette needs no code. In an image prompt, write the hex values from the theme.

Save each prompt to `figures/prompts/<slug>.md` before any generation. It is the record, and it lets a figure move to another backend unchanged.

## 5. Generate and inspect

Write all prompt files, then run them as a batch: the backend's batch interface if it has one, else up to four in parallel, else in sequence. Each task keeps its own prompt and output path. Retry a failed item once without redoing the successes.

Look at every output at its final size:

- Every label matches the prompt letter for letter, including units and symbols.
- Counts, arrow directions, and connections match the facts.
- No hex codes, palette names, fake logos, or baked-in captions.

Wrong generated text means regenerate from a corrected prompt with fewer labels. Never patch, cover, or inpaint a bitmap. Stop after three tries and use a text-free image with SVG labels, or SVG alone. If you cannot view images, say the output is unverified and hand the check to an agent that can.

Never use a generated image for data or exact numbers.

## 6. Deliver

Diagrams keep an editable source: Mermaid or SVG, and `.excalidraw` for box-and-arrow figures when practical.

```bash
python3 scripts/figure_tool.py theme figure.svg --out-dir figures            # .light.svg and .dark.svg
python3 scripts/figure_tool.py theme figure.svg --out-dir figures --flatten  # literal colours for picky converters
python3 scripts/figure_tool.py excalidraw boxes.json figures/slug.excalidraw # see assets/example-boxes.json
```

```
figures/<slug>.webp or .png    compressed final, 2x for screens, about 2100 px wide for a full page width
figures/<slug>.svg|.mmd|.excalidraw|.py    editable source
figures/prompts/<slug>.md      prompt, backend, assumptions, inspection result
```

Consumers:

- `interactive-guide`: a `figure` block, with `src` the local file, `alt`, `caption`, `origin: "explain"`, and `source` naming the prompt file or tool.
- `qi-read-paper`: the same block for explanatory figures, kept apart from the paper's own, which use `origin: "paper"`.
- `research-report`: a file in `figures/` with a caption, and the prompt or source recorded.

Report each figure's type, route, backend, files, assumptions, and whether you saw it.

## Gotchas

- Image backends are remote. A prompt may send unpublished results outside the machine; ask first when the work is embargoed or private.
- Generators paint what they read. Hex codes and palette names appear as labels unless the prompt forbids it.
- Every extra label raises the odds of a wrong one. Six short labels survive; a paragraph does not.
- Picture-of-results fabrication is the worst failure here. A generated "qualitative comparison" is invented evidence, even when marked as an example.
- ImageMagick's built-in SVG renderer dropped arrow markers and text colours from a CSS element selector when tested. Set `fill` on a `<g>`, render with a browser or rsvg-convert when possible, and look at the result.
- Some converters ignore CSS variables; use `--flatten`. Keep the unflattened file as the source.
- Inlined into HTML, `:root` binds the whole page, so two themed SVGs collide. Use `<img>` or a `figure` block.
- pdfLaTeX cannot include WebP. Use PDF, SVG via a converter, or PNG for manuscripts, and WebP for the web.
- Mermaid state and class diagrams do not convert element by element to Excalidraw. Build those from box JSON or stay with Mermaid.
- Vermilion and deep green can merge for colour-blind readers. Encode meaning twice, with shape, line style, or a label.
- Enlarging pixels or editing DPI metadata does not add resolution. Pixel width divided by print width in inches is the real number.
