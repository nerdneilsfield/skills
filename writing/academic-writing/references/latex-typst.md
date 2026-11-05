# LaTeX and Typst mechanics

## Templates

- IEEE: `IEEEtran` class with the matching option (`conference`, `journal`, `transmag`) and `IEEEtran.bst` or the biblatex-ieee style. Use the version from the venue, not an older copy.
- ACM: `acmart` with the venue's option set. Copy the rights, CCS concepts, and keyword blocks the venue requires. Use the ACM reference style unless the call says otherwise.
- Use the template's own title and author macros. Do not edit class files or override margins and font sizes.
- Typst: use the venue's official template if one exists; otherwise a community package and flag that it is not official. Some venues require their own template or check the source package; confirm that a Typst-built PDF is accepted before using it.

## Bibliography hygiene

- Generate BibTeX from DOI or an indexed source (Crossref, DBLP, publisher, arXiv), not from memory. See `integrity.md`.
- One key style, for example `author2024word`. Unique keys.
- Fields: authors, title, venue, year, pages or article number, DOI. Preserve capitalisation of acronyms with braces (`{LiDAR}`, `{SLAM}`).
- Prefer the published version over arXiv when it exists; cite arXiv with its ID otherwise.
- Remove entries that are never cited if the venue prints the whole file.
- `check_paper.py` finds undefined citations, duplicate and unused entries, and missing fields.

## Cross references

- Label after the caption: `\caption{...}\label{fig:x}`. Prefixes: `fig:`, `tab:`, `sec:`, `eq:`, `alg:`.
- Refer with `\ref` or `\cref`; do not type numbers by hand. Non-breaking space before the reference (`Fig.~\ref{...}`).
- Every float is referred to in the text and appears after (or near) the first reference.
- Run the checker; resolve every undefined reference. In Typst, use labels and `@ref`; a missing label is a compile error.

## Figures and tables

- Vector formats (PDF, SVG) for plots and diagrams; raster at print resolution for photos. Fonts in figures comparable to caption size.
- Colour-blind-safe and readable in grayscale. Axis labels with units. Same style across figures.
- Tables: `booktabs` rules, no vertical lines, units in headers, consistent decimals, best value marked the same way.
- Double-column floats (`figure*`) only when needed. Keep captions informative.

## Compile checks

1. Compile with the venue's engine until the log is stable (`latexmk -pdf` or the venue's recommendation; `xelatex` or `lualatex` for CJK).
2. Read the log: fix errors, undefined references and citations, and overfull boxes that run into margins.
3. Run `python3 scripts/check_paper.py main.tex` and fix errors. Treat warnings as a list to review.
4. Check the PDF: page count by the call's rule, fonts embedded (for example with `pdffonts`), anonymity metadata, readable figures.
5. For arXiv or camera-ready, follow the venue's file-package rules (source plus `.bbl` where required).

## Script limits

`check_paper.py` is regex-based: it does not expand macros, does not see labels or citations produced by custom commands, and handles `\input`/`\include` but not `subfiles` or `\import`. It does not verify that a citation is real. Typst has no counterpart script; rely on the compiler.
