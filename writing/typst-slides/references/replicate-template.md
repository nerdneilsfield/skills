# Reproduce another template in Typst

For the user's own decks. A template is often someone else's work: reproduce structure, colours, grid and type scale freely for internal use, but do not ship a copy of its logos, photographs, or bundled fonts. Ask whether the template is the user's employer's brand template (usually fine for the employee's own work) or a purchased or third-party one (check its licence before redistributing the result). Replace every logo or ornament image with a placeholder (`logo-slot()` or a dashed rectangle) unless the user supplies the file and confirms the right to use it.

## 1. Extract a spec

`.pptx` or `.potx` (a zip of XML):

```text
python3 scripts/pptx_spec.py template.pptx -o spec.json
```

The JSON lists the slide size, theme colours and fonts, per master and layout the placeholders (position as percent of the slide) and decorative shapes, pictures (likely logos; flagged), embedded fonts, and each slide's layout and title. Colour modifiers (`lumMod`) are listed but not applied. Slides may override the master, so compare `title_run_style` with the master's `text_styles`. The script reads the zip in memory and never extracts it.

PDF:

```text
sh scripts/pdf_spec.sh template.pdf outdir
```

It prints page size and fonts (`pdffonts`), lists embedded images (`pdfimages -list`; the same image on every page is a logo or background), and writes page PNGs. Positions and sizes must then be measured on the PNGs. `.ppt`, `.key`, `.odp`: convert to PDF or `.pptx` with LibreOffice first.

Images only (screenshots): open them and note layout by eye. Sample colours with `convert page.png -colors 6 -unique-colors txt:-` (ImageMagick) and name fonts by looking; say which font you guessed.

Render the original too (`soffice --headless --convert-to pdf template.pptx`, then `pdftoppm -r 40 -png`) so you can put the original and your copy side by side. Fonts in the render may be substitutes.

## 2. Write the theme

Copy `assets/replica-theme.typ` and fill the `spec` dictionary from the JSON: `size` (use `slide_size.cm` so point sizes match), `bg`, `text`, `title-color`, `accent`, `font`, and the boxes for title, body, cover title and subtitle, footer and number. Add `decor` rectangles for bands and bars; add alignment if the extractor reports `align` (the skeleton is left aligned, the cover of a centred template needs `align(center)` edits). For each layout the user needs (cover, section, content, two columns, closing) add a slide function the same way `title-slide` is written. Fonts: use the template's font if installed; otherwise the nearest installed one and record it.

## 3. Check

Build a small deck (`deck-replica.typ`) that uses one of each layout, compile with `scripts/build_deck.sh`, and view the pages next to the original renders. Fix colour, size, and position until the match is close; do not chase pixel identity.

## 4. Report what is not reproduced

Always list, by category: logos and artwork (placeholders), fonts (original vs used), gradients, shadows, images as backgrounds, SmartArt and charts (rebuild natively in Typst or as images), animations and transitions (Touying `#pause` is similar but not identical), master text that depends on fields (date, footer), and anything you could not measure. Mention licence concerns for the logos and fonts found in `media` and `fonts_embedded`.

Tested: `pptx_spec.py` on a real 12-slide `.pptx` (dark green template) and a hand-built zip in the unit tests; a skeleton filled from the real spec reproduced the dark background, lime titles, title and agenda positions, footer and page number, and differed in the centred cover, pill tag, and rounded cards (listed above as not reproduced).
