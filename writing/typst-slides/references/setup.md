# Setup for a first-time user

## What you need

| Tool | Why | Install |
|---|---|---|
| Typst 0.15 or newer | compiler | `brew install typst`, `winget install Typst.Typst`, `cargo install typst-cli`, or a release binary from github.com/typst/typst/releases (unpack anywhere and put it on PATH, or call it by path) |
| Poppler (`pdftoppm`, `pdftotext`) | render pages to PNG and check overflow | `apt install poppler-utils`, `brew install poppler` |
| Python 3.9+ | extractor and check scripts, standard library only | usually present |
| Internet, first compile only | Typst downloads `@preview/touying:0.8.0`, `cetz`, `fletcher` into its cache | none; afterwards it works offline from the cache |
| Optional: LibreOffice | render a `.pptx` template to PDF so you can look at it | `apt install libreoffice` |

Check: `typst --version` prints 0.15 or higher.

## Fonts

Typst finds system fonts. The theme asks for `Inter` (Latin), `Noto Sans CJK SC` (Chinese), and `DejaVu Sans Mono` (code). Install what is missing, then confirm with `typst fonts | grep -i noto`.

- Noto Sans CJK: `apt install fonts-noto-cjk`, `brew install --cask font-noto-sans-cjk-sc`, or download from fonts.google.com/noto. Windows and macOS users may prefer `Microsoft YaHei` or `PingFang SC`.
- Inter: fonts.google.com/specimen/Inter. If it is absent the CJK family supplies the Latin glyphs, which still looks fine.
- Edit `latin-sans`, `cjk-sans`, `mono-font` at the top of `assets/theme.typ` to whatever `typst fonts` lists. Each missing name prints one warning; fonts passed with `--font-path dir` are also found.
- A font-name typo shows up as boxes or odd glyphs in the PDF, so open the PDF once.

## First deck in five steps

1. Copy `assets/theme.typ` and one template (for example `assets/research-talk.typ`) into a new folder.
2. `typst compile research-talk.typ`. It writes `research-talk.pdf`.
3. Replace the placeholder text and the `figure-slot(...)` boxes with your own.
4. Run `scripts/build_deck.sh research-talk.typ`. It renders PNGs, and flags slides that spilled onto a second page.
5. Look at every PNG. For live editing use `typst watch research-talk.typ` beside a PDF viewer, or the Tinymist extension in VS Code.

If the template sits outside the folder you compile from, add `--root` with a parent that contains both.

## Sharing and confidentiality

Check the deck contains no private paths, names, unreleased numbers, or other customers' material before sharing the PDF. Typst puts `config-info` title and author into the PDF metadata. For client decks keep the confidentiality line in the footer, keep logo placeholders until you have the files cleared, and export only the PDF, not the source with comments.
