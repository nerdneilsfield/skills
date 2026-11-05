# Slide layout and visual hierarchy

Rules for the Typst templates in `assets/`; they hold for any deck.

## Grid and space

- Landscape 16:9. Margins about 2 em at the sides and 1.6 em at the top; keep content inside them. The theme sets this.
- Think in two or three columns of equal gutter. Use `grid(columns: (1.4fr, 1fr))` for text beside a figure, never hand-placed boxes.
- One gap unit (0.9 em in the theme) between blocks. Equal gaps look designed; random gaps look accidental.
- Leave at least a third of the slide empty. If the slide is full, split it or move detail to the speaker script or an appendix slide.

## Hierarchy

- Three levels at most: title (indigo, bold), body (ink), caption or source (muted grey, small). Size ratio roughly 1.15 : 1 : 0.5 in the theme; body stays at or above 20 pt on a 16:9 page.
- One accent per slide. Vermilion marks the single thing to look at (a number, one word, a callout); indigo is structure; green means good; crimson means a problem. If everything is highlighted nothing is.
- Weight and colour carry emphasis; avoid underline, all caps, and italic CJK.
- Align everything to the left edge of the title. Centre only the title slide, a single stat, or a diagram.

## Density

- Body text: three to five bullets of at most one line each, or one short paragraph. Code: eight lines. Table: five rows and five columns. Cards: six.
- If you need to read it aloud word for word, it belongs in the script, not on the slide.
- Do not shrink text to fit; reduce content.

## Picture to text

- Figure slides: figure 60-70% of the area, a title that states the finding, one line of takeaway, a source or caption. Remove chart decoration (gridlines, legends for one series, 3D).
- Text slides: pair with a small figure or a stat when one exists.
- Diagrams: at most seven boxes; arrows go left to right or top to bottom; label arrows with verbs.
- Number slides: one to three large numbers with a unit and a label.
- Colour-blind safe: do not rely on red against green alone; add a label or marker.

## Common page types

| Page | Layout |
|---|---|
| Title | Left aligned, vermilion rule, title, subtitle, name, date; logo top left |
| Section | Rule, section name; no body |
| Claim + evidence | Title claim, figure or table, source |
| Figure + points | Two columns, 1.5 : 1 |
| Comparison | Table with the chosen row highlighted |
| Process | Three to five steps in a row, one callout each |
| Stat | `stats(...)` row, one sentence below |
| Quote or takeaway | `focus-slide`, one sentence |
| Timeline | Table or fletcher diagram with dates |
| Appendix | Same theme, title starts with "Backup:" |

## Vary, then check

Do not use the same page type on more than three slides in a row. After building, render pages and look at them: text touching the footer, a second page of one slide, a table cut off, a figure placeholder left behind, an unreadable label. Fix by cutting words first, then by changing the layout, and only then by reducing size.
