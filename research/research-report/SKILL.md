---
name: research-report
description: "Use when the user asks for a research report, survey, literature review, or wide topic investigation written up from many sources, in Chinese or English. Covers per-source notes, outline, chapter drafting, figures, whole-document review, and export to zip, PDF, or HTML. Not for reading one paper closely (qi-read-paper), a quick factual answer, or a manuscript reporting the user's own results (academic-writing)."
license: MIT
compatibility: Export uses pandoc and zip when installed. PDF also needs a PDF engine such as xelatex or typst; Chinese PDF needs a CJK font.
metadata:
  author: DengQi
---

# Research report from sources to export

Work in files, in order. Each stage reads the previous stage's files, so the work survives a new session and chapters can be drafted in parallel. Do not write the report from memory of the sources.

Copy this checklist and keep it current:

```
- [ ] 0 Frame
- [ ] 1 Source notes
- [ ] 2 Outline
- [ ] 3 Chapters
- [ ] 4 Figures
- [ ] 5 Assembled report reviewed
- [ ] 6 Full-document deai
- [ ] 7 Export
```

Use this layout unless the project has its own:

```
report/
  frame.md
  notes/<source-slug>.md
  matrix.md
  outline.md
  chapters/01-<slug>.md
  figures/
  report.md
```

## 0. Frame

Write `frame.md` before searching: the reader, the decision or question they have, the scope, what is out, and the [report kind](references/kinds.md). If the user is available, confirm it. If the reader cannot be named, the report has no way to decide what to leave out.

A survey meant for a journal or conference still follows this skill for its content; take the venue rules from `academic-writing`.

## 1. Source notes

Write one short note per source, as a separate file, before planning anything. Record the citation and link, what the source actually claims, its evidence, its limits, and how much to trust it. Mark a source read only from its abstract or snippet. Add a row to `matrix.md` for each note, as described in [Synthesis](references/synthesis.md). For finding the sources, use `paper-search`: it owns the query log, the inclusion criteria, and the stopping rule. For a paper that needs deep reading, use `qi-read-paper`.

## 2. Outline

Read `matrix.md` for agreements, splits, and gaps, then build `outline.md` from it. Write the report's main point first, as one sentence, followed by the structure for its kind in [Report kinds](references/kinds.md). For a survey, derive the taxonomy first. Keep the outline at most two heading levels. Under each chapter, give its one-sentence point, which must be a claim and not a topic, and the notes that support it. A chapter with no supporting note is a gap: search more, or cut it. If the user is available, confirm the outline before drafting.

## 3. Chapters

Write each chapter as its own file from the outline and the notes it cites. Follow `technical-writing` for technical material, and [Synthesis](references/synthesis.md) for paragraphs, confidence levels, and citations: organise by concept, compare sources, and do not give each source its own paragraph. Cite with the note slug, as `[@note-slug]`, and turn these into final numbers or links only during assembly, so parallel drafts cannot collide. Chapters may go to parallel agents; give each one the outline, its notes, and the terminology decisions, and require that citation form.

## 4. Figures

Add a figure only where it explains something prose does poorly. Use `research-figure` to choose the backend; data and exact structure always go through code, SVG, or Mermaid.

Save figures in `figures/` with descriptive names, give each a caption, and record the prompt or source. Check every generated image by looking at it.

## 5. Assemble and review

Concatenate the chapters into `report.md`, then read the whole document in order. Check these first, since chapters drafted apart fail here:

- The opening and closing of every chapter: does each ending lead into the next opening, and is anything said twice?
- The introduction's promises against what the chapters deliver, and the conclusion against the evidence.
- One term for one concept, and consistent units, names, and citation format.
- The review questions in [Synthesis](references/synthesis.md), and citations sampled against their sources.
- Contradictions between chapters, which often reflect real disagreement between sources. State them instead of smoothing them over.

Fix these in `report.md`, or in the chapter and reassemble, but keep one source of truth.

## 6. Full-document deai

Run `deai` on the assembled text. Run it once, here, not per chapter, so it can catch patterns that only show across chapters: repeated skeletons, identical openings, and uniform rhythm. Citations, numbers, and quotations must survive unchanged.

## 7. Export

Ask which formats the user wants unless they said: a zip, a PDF, or a single HTML file. Do not install tools without permission. If a tool is missing, say so and deliver the formats that work.

```sh
zip -r report.zip report.md figures
pandoc report.md -s --embed-resources --toc -o report.html
pandoc report.md --pdf-engine=xelatex -V CJKmainfont="Noto Serif CJK SC" --toc -o report.pdf
```

Run these from `report/`, so relative image paths resolve. Render Mermaid to SVG or PNG first; pandoc does not draw it. Then check each output: read pandoc warnings, list the zip contents, confirm the HTML has no external image paths, and sample the PDF with `pdfinfo` and `pdftotext` for page count and missing text. If you can view images, look at a rendered page too.

## Gotchas

- Without `--embed-resources`, the HTML depends on sibling image files and breaks when moved alone. It replaces the older `--self-contained`.
- A Chinese PDF built without a CJK font drops or garbles text, sometimes with only a warning. Check the font with `fc-list :lang=zh` and read a page of the output.
- A search snippet is not a source. Fetch the page, or mark the note as snippet-only.
- A citation that exists can still fail to support the sentence beside it. Spot-check claims against the notes during review.
- Taxonomy by year or by keyword reads as organised but explains nothing. Split on assumptions or trade-offs.
- Ten papers from one group or on one dataset are not ten independent confirmations.
- A long reference list hides thin reading. Report how many sources were read in full.
- Agents drafting in parallel each write their own introduction and conclusion. Tell them not to, or remove these during assembly.

## Report

State the report kind, the sources read and how many were snippet-only, unverified citations, known gaps, figures by origin, deai result, and each export with how it was checked.
