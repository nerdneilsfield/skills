---
name: typst-slides
description: "Use when the user wants a presentation as real, editable Typst slides instead of PowerPoint: research talk, group meeting, project review, defence or proposal, client demo or pitch, technical sharing, or teaching lecture, in English or Chinese. Plans the storyline and speaker script first, then builds a Touying deck in one Japanese-colour palette with figures from an image model, CeTZ, fletcher, or the user's images, and can reproduce another .pptx, .pdf, or image template. Not for a figure alone (research-figure), a paper's PDF (academic-writing), or an interactive HTML page (interactive-guide)."
license: MIT
compatibility: Needs Typst 0.15 or newer, which downloads Touying 0.8.0 from Typst Universe on first compile, plus poppler (pdftoppm, pdftotext) and python3 for the checks. CJK text needs an installed font such as Noto Sans CJK SC. Optional LibreOffice for viewing a .pptx template.
metadata:
  author: DengQi
---

# Typst slides

Body text stays real Typst text the user can edit. Never render a whole slide as an image. The agent drafts from the user's material and the user approves the words; placeholders replace anything the material does not support. Paths below are relative to this skill. First-time setup, fonts, and install commands: [references/setup.md](references/setup.md).

## Workflow

1. **Intake.** Ask once, in one batch, with a recommended default for each: scene (see templates), audience and what they know, duration, language, the source material (paper, notes, data, an old deck), figures that already exist, a template to follow, confidentiality. If the user is not present, decide, and record each assumption at the top of the storyline file.
2. **Storyline and script, then stop.** Write `storyline.md`: the one-sentence takeaway, the spine, and one row per slide (assertion title, evidence, time, speaker script). Method and tables: [references/storytelling.md](references/storytelling.md). The user edits and approves it before any layout.
3. **Pick a template** from [references/templates.md](references/templates.md), or reproduce the user's own with [references/replicate-template.md](references/replicate-template.md). Copy `assets/theme.typ` and the template into the user's folder. The palette is fixed: it is the light set of `research/research-figure/assets/themes/japanese.json` (ink text, indigo structure, one vermilion accent, kinari background); do not add colours.
4. **Layout.** One idea per slide, claim as title, body at 20 pt or more, one accent per slide, generous space: [references/layout.md](references/layout.md). Syntax and Touying use (grid, animation, notes, CJK, CeTZ, fletcher): [references/typst-syntax.md](references/typst-syntax.md). Put the script into `#speaker-note[...]`.
5. **Figures.** Existing images: `image(...)`. Diagrams: fletcher or CeTZ. Generated images: use the `research-figure` skill to pick a backend and keep labels and numbers in Typst. Until a figure exists, leave `figure-slot("what it shows")` and list it for the user.
6. **Compile and look.** `sh scripts/build_deck.sh deck.typ` compiles, renders PNGs, and flags pages that repeat a slide number without its title (likely overflow). Open every PNG with the image viewer you have. Fix by cutting words first. Also check the `.typ` for stray TODOs and private data.
7. **Report.** Give the PDF path, page count, assumptions, figures still missing, claims without a source, fonts used and substituted, and what was not reproduced from a copied template.

## Templates

`assets/research-talk.typ`, `project-review.typ`, `defense.typ` (Chinese), `client-demo.typ`, `tech-share.typ`, `lecture.typ`. All import `assets/theme.typ`, which also provides `callout`, `stat`, `stats`, `source`, `tag`, `figure-slot`, `logo-slot`, `focus-slide`.

## Template replication in brief

`python3 scripts/pptx_spec.py t.pptx -o spec.json` (stdlib, reads the zip in memory) or `sh scripts/pdf_spec.sh t.pdf` for a PDF; fill `assets/replica-theme.typ`; compile; compare with the original render; list what differs. Logos and artwork become placeholders; fonts and licence are flagged.

## Gotchas

- Touying 0.8.0 requires Typst 0.15. Older notes show 0.6 or 0.7 syntax; verify against the installed version.
- Overflow is silent: a too-tall slide becomes two pages. Look at the PNGs and compare page count with the storyline plus animation steps.
- An uninstalled font only warns, then CJK may render as boxes. Check `typst fonts` and edit the lists at the top of `theme.typ`.
- Do not use `#set page` in a deck or hand-place boxes; use `config-page` and `grid`. Details and wrong-versus-right forms are in [references/typst-syntax.md](references/typst-syntax.md).
- `$`, `@`, `#`, `<` in plain text must be escaped (`\$5`); `fill: #fff` is invalid, write `rgb("#fff")`.
- `#pause` does not work inside `context`; every step is a PDF page.
- Image generators garble text and may send unpublished results to a remote service; ask first for private or embargoed work.
- Client decks: confidentiality line in the footer, logo placeholders until files are supplied, no other customer's name or data without written permission. Third-party templates: reproduce structure for the user's own use, never redistribute their logos or fonts.
- Never invent numbers, citations, or quotes to fill a slide; leave a visible TODO.
- The deck's PDF metadata carries the title and author from `config-info`; check them before sharing.
