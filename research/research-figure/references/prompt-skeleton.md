# Prompt skeleton

Write the prompt in plain language, because every backend reads that. Put layout before style, and give labels verbatim. Copy this into `figures/prompts/<slug>.md`, delete what does not apply, and add no tool flags to the body; those belong to the handoff.

```markdown
---
slug: <kebab-case>
type: <figure type>
route: image | source | code
style: <style>
theme: japanese
backend: <filled in after resolution>
output: figures/<slug>.png
assumptions:
  - <each unconfirmed choice>
inspection: <filled in after looking: pass, or what failed and on which try>
---

Purpose: <what the reader should understand, and where the figure appears>.
Canvas: <aspect ratio>, <background>, generous margins, no outer border.

Layout: <reading direction, then regions in order, with relative sizes>.
1. <region or stage>: <what it holds>, glyph: <simple glyph>.
2. ...
Connections:
- <from> to <to>, <solid or dashed>, label "<text>".
Grouping: <dashed containers, panels, swimlanes>.

Exact labels, spelled as given, and no other text:
"<label>", "<label>", "<label>"

Style: <style sentence from the list below>.
Colours, as rendering guidance only: background <hex>, line and text <hex>,
main <hex>, emphasis <hex>, used on <the one element that matters>.

Constraints:
- Do not display hex codes, colour names, or palette labels as text.
- No figure number, caption, watermark, logo, or signature in the image.
- No numbers, axes, or results beyond the labels listed above.
- Equal box sizes within a tier, aligned to a grid, arrows that do not cross boxes.
- No gradients, drop shadows, glass effects, 3D, emoji, or decorative texture.
```

For an image with no text, replace the labels section with "Contain no text, letters, digits, or symbols of any kind", and set labels later as SVG text.

## Styles

| Style | Sentence for the prompt | Fits |
|---|---|---|
| `paper-line` (default) | Clean flat vector figure in the manner of a conference paper: thin even lines, restrained colour, readable in greyscale | Pipelines, architecture, charts |
| `textbook` | Precise textbook illustration with simple shading by flat tone and thin leader lines | Schematics, mechanisms |
| `editorial` | Calm flat editorial illustration with large simple shapes and much empty space | Graphical abstracts, overview posters |
| `blueprint` | Technical drawing with fine lines, a faint grid, and monospaced labels | System architecture, topology |
| `ink-sketch` | Confident hand-drawn ink lines with sparse flat colour, tidy and legible | Teaching, slides, not journals |

Style and type are independent, but a journal figure stays with `paper-line` or `textbook`. A reference image passed to a backend should set style only. Say so in the prompt, or its content leaks in.

## Palette in other tools

For Mermaid, map the theme through the `base` theme's `themeVariables` in an init directive, and leave it out when the host page themes Mermaid itself, as `interactive-guide` does. For plotting code, read the hex values from the theme JSON instead of retyping them. Keep to four colours in one figure, including ink.
