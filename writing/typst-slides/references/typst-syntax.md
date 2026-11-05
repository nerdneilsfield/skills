# Typst and Touying syntax for slides

Checked against Typst 0.15.1 and Touying 0.8.0. Every block fenced as `typst` is compiled by `tests/test_typst_slides.py` inside a slide that uses `assets/theme.typ`, so it runs as written. Blocks fenced as `text` are deliberately wrong or partial.

Contents: deck skeleton, text and fonts, layout, images, tables, math, code, animation, notes, drawing, escapes, gotchas.

## Deck skeleton

```text
#import "theme.typ": *                       // the skill theme; or a Touying built-in theme
#show: jp-theme.with(
  config-info(title: [Title], author: [Name], date: datetime(year: 2026, month: 11, day: 5)),
  lang: "en", footer: [Short title],
)
#title-slide()
= Section name          // level 1: section divider slide
== An assertion title   // level 2: one slide per heading
body
```

`---` starts a new slide under the same heading. `#show: appendix` freezes the page count for backup slides. `#focus-slide[One sentence.]` is the single-claim slide.

## Text, lists, fonts

```typst
Plain text, *bold*, _italic_, `inline code`, and #text(fill: jp.vermilion)[coloured text].
- bullet
  - nested bullet
+ numbered
+ numbered again
/ Term: definition list
```

Fonts are set once, in `theme.typ` (`latin-sans`, `cjk-sans`, `mono-font`). Typst falls back per glyph, so a Latin family followed by a CJK family covers mixed text. Names must match `typst fonts` exactly: `Noto Sans CJK SC`, not `Noto Sans SC`. A name that is not installed prints `warning: unknown font family` and the glyphs may come out as boxes. Locally:

```typst
#text(font: "Noto Serif CJK SC", lang: "zh")[宋体标题 with Latin and 123]
```

## Layout

```typst
#grid(columns: (1.4fr, 1fr), column-gutter: 1.5em, row-gutter: 1em,
  [Left column text, with a #alert[highlight].],
  figure-slot("what the figure must show", height: 5cm),
)
#v(1fr)
#align(center)[Centred line]
#components.side-by-side(columns: (1fr, 2fr))[narrow][wide]
#utils.fit-to-width(100%)[One long line scaled to the slide width]
#block(fill: jp.indigo-fill, inset: 0.8em, radius: 4pt, width: 100%)[A panel]
```

Theme helpers: `callout(title:, kind: "note"|"good"|"key"|"warn")`, `stat(value, label)`, `stats(...)`, `source[...]`, `tag[...]`, `figure-slot(desc)`, `logo-slot()`. Do not call `#set page` inside a deck; use `config-page(...)` in the `#show: jp-theme.with(...)` call so Touying keeps control of headers and footers.

## Images and figures

```typst
#figure(image("example-figure.svg", width: 70%), caption: [Latency by batch size])
#image("example-figure.svg", height: 6cm, fit: "contain")
```

Paths are relative to the file that contains the `image(...)` call. A file outside the project root needs `typst compile --root /common/parent deck.typ`. Prefer SVG or PDF for diagrams and 200 dpi or more for PNG at the slide size. Put a logo in once through the theme's `logo:` argument.

## Tables

```typst
#table(columns: (2fr, 1fr, 1fr), align: (left, right, right),
  table.header([Method], [Latency], [Accuracy]),
  [Baseline], [118 ms], [81.2],
  [Ours], [#alert[74 ms]], [81.3],
  table.cell(colspan: 3)[Single seed; see appendix for variance.],
)
```

## Math

```typst
Inline $a^2 + b^2 = c^2$, display below (spaces inside the dollars):
$ L(theta) = 1/N sum_(i=1)^N ell(f_theta (x_i), y_i) + lambda norm(theta)_2^2 $
$ f(x) = cases(x &"if" x >= 0, -x &"otherwise") $
```

Greek letters and functions are written by name (`theta`, `sum`, `norm`). Multi-letter text needs quotes: `"if"`, `"latency"`.

## Code

````typst
```python
def decode(batch):
    return model(batch)   # keep slide code to 8 lines
```
#raw(read("example-figure.svg").slice(0, 60), lang: "xml", block: true)
````

## Animation (Touying)

```typst
First point
#pause
Second point appears on the next step
#meanwhile
Shown from the first step again
#uncover("2-")[Reserves space, visible from step 2]
#only(2)[Takes no space until step 2]
#alternatives[Draft][Final]
#effect(text.with(fill: red), "2-")[Turns red at step 2]
#item-by-item[
- first
- second
]
```

`#pause` also works inside `#grid` cell bodies. It does not work inside `context` blocks or custom show-rule functions; use `#slide(repeat: 3, self => [...])` with `utils.methods(self)` there. Each step is one PDF page, so a talk with many pauses has more pages than slides.

## Speaker notes and presenter view

```typst
#speaker-note[
  Say the result first. Then the baseline. 45 seconds.
]
```

Notes are invisible in the normal PDF. Passing `config-common(show-notes-on-second-screen: right)` to `jp-theme.with(...)` doubles the page width and puts the notes beside each slide (for a dual-screen viewer such as pympress); `config-common(show-only-notes: true)` makes a notes view with the slide as a thumbnail. Both compiled here. Build the normal PDF for the audience and a notes PDF for yourself. pdfpc metadata is on by default (`enable-pdfpc`); write the `.pdfpc` file with `typst eval --in deck.typ 'query(<pdfpc-file>).first().value' > deck.pdfpc` (output verified as JSON with the notes).

## Drawing: CeTZ and fletcher

```typst
#import "@preview/cetz:0.5.3"
#cetz.canvas({
  import cetz.draw: *
  rect((0, 0), (3, 1.5), fill: jp.indigo-fill, stroke: jp.indigo)
  content((1.5, 0.75), [Encoder])
  line((3, 0.75), (5, 0.75), mark: (end: ">"))
})
```

```typst
#import "@preview/fletcher:0.5.8" as fletcher: diagram, node, edge
#align(center, diagram(node-stroke: 1pt + jp.indigo, node-fill: jp.indigo-fill, node-inset: 8pt,
  node((0, 0), [Input]), edge("-|>"), node((1, 0), [Model]), edge("-|>"), node((2, 0), [Output])))
```

Animated drawings need Touying's reducer, and `(pause,)` inside CeTZ, bare `pause` inside fletcher:

```typst
#import "@preview/cetz:0.5.3"
#let cetz-canvas = touying-reducer.with(reduce: cetz.canvas, cover: cetz.draw.hide.with(bounds: true))
#cetz-canvas({
  import cetz.draw: *
  rect((0, 0), (3, 1.5))
  (pause,)
  circle((5, 0.75), radius: 0.7)
})
```

CeTZ is LGPL-3.0, fletcher MIT; both are imported, not copied. For plots use `cetz-plot` or an image from the data script; keep charts native where numbers matter.

## Escapes

```typst
Costs \$5, mail me\@example.org, issue \#3, tag \<a>, 50\% is fine.
```

## Gotchas

- Colours are `rgb("#165E83")` or `jp.indigo`; `fill: #fff` is an error.
- Lengths need units: `size: 20pt`, not `20`. `1fr` works only in `grid`, `stack`, and `columns`, not in `block(width: 1fr)`.
- A one-item array needs a trailing comma: `(1,)`; `(1)` is just the number 1.
- In math, unknown words are variables: `$latency$` fails; write `$"latency"$`.
- In markup `$`, `@`, `#`, `<` start something. Escape them as `\$`, `\@`, `\#`, `\<` (currency, emails, hashtags, `<tag>`).
- Content is `[...]`, text is `"..."`. `text(fill: red)[hi]` and `text(fill: red, "hi")` both work.
- `=` makes a section slide and `==` makes a slide. Putting the title in a `#text` line instead of a heading loses outline, bookmarks, and the footer.
- Touying 0.8.0 needs Typst 0.15; older compilers refuse the package. Older answers quote 0.6 or 0.7 syntax (for example `touying-slides.with` options) that has since changed. Check the version in `typst.toml` of the cached package.
- `#pause` is not supported inside `context` (Touying docs). Check the page count after adding animation.
- Unknown font names warn and fall back; look for the warning, then compare with `typst fonts`.
- Do not hand-position boxes with `#place` for ordinary layout; use `grid`. Reserve `place` for stamps such as the source line.
- Text overflow is not an error. A slide whose body is too tall continues on a second page. Run `scripts/build_deck.sh` and look at the pages.
