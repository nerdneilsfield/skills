// Shared Touying theme for the typst-slides skill.
// Palette follows research/research-figure/assets/themes/japanese.json (light).
// Needs Typst 0.15+ and @preview/touying:0.8.0 (downloaded on first compile).
#import "@preview/touying:0.8.0": *

#let jp = (
  bg: rgb("#FBFAF5"),       // kinari-iro, page
  ink: rgb("#2B2B2B"),      // kuro, body text
  muted: rgb("#595857"),    // sumi-iro, captions, footer
  indigo: rgb("#165E83"),   // ai-iro, primary
  indigo-fill: rgb("#E3ECF1"),
  green: rgb("#006E54"),    // moegi-iro, secondary
  green-fill: rgb("#DFEDE8"),
  purple: rgb("#745399"),   // edo-murasaki, tertiary
  purple-fill: rgb("#ECE7F2"),
  vermilion: rgb("#EB6101"),// shu-iro, accent: one or two things per slide
  vermilion-fill: rgb("#FBE6D9"),
  crimson: rgb("#D7003A"),  // kurenai, warnings only
  crimson-fill: rgb("#F9E0E6"),
  grey: rgb("#7B7C7D"),     // namari-iro
  grey-fill: rgb("#EDEDEB"),
  grid: rgb("#DCDDDD"),
)

// Font stacks: Typst falls back per glyph, so Latin comes first and CJK after.
// See references/setup.md for installing fonts.
// Every name listed but not installed prints a warning, so keep the lists short
// and edit them here to match the machine (fc-list / typst fonts).
#let latin-sans = ("Inter",)
#let cjk-sans = ("Noto Sans CJK SC",)
#let mono-font = ("DejaVu Sans Mono",)

// ---- small building blocks -------------------------------------------------

/// Dashed box standing in for a logo. Replace with image("logo.svg", height: 1.2em).
#let logo-slot(label: "LOGO", w: 4.2em) = box(
  width: w, height: 1.5em, stroke: (dash: "dashed", thickness: 0.8pt, paint: jp.grey),
  radius: 2pt, align(center + horizon, text(0.5em, fill: jp.grey, label)),
)

/// Dashed placeholder for a figure that does not exist yet. Say what it must show.
#let figure-slot(desc, height: 6cm) = block(
  width: 100%, height: height, stroke: (dash: "dashed", thickness: 1pt, paint: jp.grey),
  fill: jp.grey-fill, radius: 4pt, inset: 1em,
  align(center + horizon, text(0.7em, fill: jp.muted)[FIGURE TODO: #desc]),
)

/// Highlighted box. kind: "note" (indigo), "good" (green), "key" (vermilion), "warn" (crimson).
#let callout(title: none, kind: "note", body) = {
  let (fill, stroke) = (
    note: (jp.indigo-fill, jp.indigo), good: (jp.green-fill, jp.green),
    key: (jp.vermilion-fill, jp.vermilion), warn: (jp.crimson-fill, jp.crimson),
  ).at(kind)
  block(width: 100%, fill: fill, stroke: (left: 3pt + stroke), inset: (x: 0.8em, y: 0.6em), radius: (right: 3pt), {
    if title != none { text(weight: "bold", fill: stroke, title); linebreak() }
    body
  })
}

/// A big number with a label. Use one or two per slide.
#let stat(value, label, color: jp.indigo) = block(inset: 0.3em, {
  text(2.2em, weight: "bold", fill: color, value); linebreak()
  text(0.7em, fill: jp.muted, label)
})

/// Row of stat() blocks centred in the free height, for a slide that is only numbers.
#let stats(height: 62%, ..items) = block(width: 100%, height: height, align(horizon,
  grid(columns: items.pos().len() * (1fr,), column-gutter: 1em, ..items.pos())))

/// Source line at the bottom of a data slide.
#let source(label: "Source", body) = place(bottom + left, text(0.5em, fill: jp.muted)[#label: #body])

/// Small round tag, e.g. #tag[Q1] or #tag(color: jp.green)[done].
#let tag(color: jp.indigo, body) = box(
  fill: color.lighten(85%), stroke: 0.6pt + color, inset: (x: 0.5em, y: 0.15em), radius: 1em,
  text(0.6em, fill: color, weight: "medium", body),
)

// ---- slide functions -------------------------------------------------------

#let slide(config: (:), repeat: auto, setting: body => body, composer: auto, ..bodies) = touying-slide-wrapper(self => {
  let header(self) = none
  let footer(self) = {
    set text(size: 0.4em, fill: jp.muted)
    v(0.2em)
    line(length: 100%, stroke: 0.4pt + jp.grid)
    components.left-and-right(
      utils.call-or-display(self, self.store.footer),
      context utils.slide-counter.display() + " / " + utils.last-slide-number,
    )
  }
  let self = utils.merge-dicts(
    self,
    config-page(header: header, footer: footer),
    config-common(subslide-preamble: self.store.subslide-preamble),
  )
  touying-slide(self: self, config: config, repeat: repeat, setting: setting, composer: composer, ..bodies)
})

#let title-slide(config: (:), ..args) = touying-slide-wrapper(self => {
  let info = self.info + args.named()
  let body = {
    set align(left + horizon)
    block(width: 100%, {
      if self.store.logo != none { self.store.logo; v(1.2em) }
      line(length: 3em, stroke: 4pt + jp.vermilion)
      v(0.5em)
      text(1.8em, weight: "bold", fill: jp.indigo, info.title)
      if info.at("subtitle", default: none) != none {
        v(0.2em); text(0.9em, fill: jp.muted, info.subtitle)
      }
      v(1.6em)
      set text(0.65em, fill: jp.ink)
      if info.at("author", default: none) != none { info.author; linebreak() }
      if info.at("institution", default: none) != none { text(fill: jp.muted, info.institution); linebreak() }
      if info.at("date", default: none) != none {
        text(fill: jp.muted, utils.display-info-date(self))
      }
    })
  }
  self = utils.merge-dicts(self, config-common(freeze-slide-counter: true), config-page(footer: none))
  touying-slide(self: self, config: config, body)
})

/// Section divider. Heading level 1 creates one automatically.
#let section-slide(config: (:), body) = touying-slide-wrapper(self => {
  self = utils.merge-dicts(self, config-common(freeze-slide-counter: true), config-page(footer: none))
  touying-slide(self: self, config: config, align(left + horizon, {
    line(length: 2em, stroke: 4pt + jp.vermilion)
    v(0.4em)
    text(1.6em, weight: "bold", fill: jp.indigo, utils.display-current-heading(level: 1, numbered: false))
    body
  }))
})

/// One sentence on indigo. For the single claim the audience must keep.
#let focus-slide(config: (:), body) = touying-slide-wrapper(self => {
  self = utils.merge-dicts(self, config-common(freeze-slide-counter: true),
    config-page(fill: jp.indigo, margin: 3em, footer: none))
  touying-slide(self: self, config: config, setting: it => align(left + horizon, text(1.5em, weight: "bold", fill: jp.bg, it)), body)
})

#let notes(self: none, ..args) = touying-notes(
  self: self,
  header: self => pad(x: 32pt, y: 16pt, text(fill: jp.bg, utils.display-current-heading(depth: self.slide-level))),
  header-fill: jp.indigo,
  fill: jp.bg,
  ..args,
)

// ---- the theme -------------------------------------------------------------

/// Apply with #show: jp-theme.with(config-info(title: [...], author: [...]), lang: "en").
/// lang "zh" switches to the CJK font stack and Chinese hyphenation rules.
#let jp-theme(
  aspect-ratio: "16-9",
  lang: "en",
  footer: none,
  logo: none,       // e.g. image("logo.svg", height: 1.4em), or logo-slot() while waiting for the real one
  text-size: 22pt,
  ..args,
  body,
) = {
  let fonts = (..latin-sans, ..cjk-sans)
  show: touying-slides.with(
    config-page(
      ..utils.page-args-from-aspect-ratio(aspect-ratio),
      margin: (x: 2.2em, top: 1.6em, bottom: 2.4em),
      fill: jp.bg,
    ),
    config-common(
      slide-fn: slide,
      title-slide-fn: title-slide,
      new-section-slide-fn: section-slide,
      notes-fn: notes,
      zero-margin-header: false,
      zero-margin-footer: false,
    ),
    config-methods(
      init: (self: none, body) => {
        set text(font: fonts, size: text-size, fill: jp.ink, lang: lang, weight: "regular")
        set par(leading: 0.6em, spacing: 0.9em)
        set list(marker: text(fill: jp.vermilion)[•], spacing: 0.7em, indent: 0.2em)
        set enum(spacing: 0.7em)
        set table(stroke: (x, y) => if y == 0 { (bottom: 1pt + jp.indigo) } else { (bottom: 0.4pt + jp.grid) },
          inset: (x: 0.6em, y: 0.45em), fill: (x, y) => if y == 0 { jp.indigo-fill })
        set figure(gap: 0.6em)
        show figure.caption: set text(0.7em, fill: jp.muted)
        show raw: set text(font: mono-font, size: 0.8em)
        show raw.where(block: true): it => block(fill: jp.grey-fill, inset: 0.7em, radius: 4pt, width: 100%, it)
        show link: set text(fill: jp.indigo)
        show footnote.entry: set text(size: 0.6em)
        show heading.where(level: 1): set text(fill: jp.indigo)
        body
      },
      alert: (self: none, it) => text(fill: jp.vermilion, weight: "bold", it),
    ),
    config-colors(
      primary: jp.indigo, secondary: jp.green, tertiary: jp.purple,
      neutral-lightest: jp.bg, neutral-darkest: jp.ink, neutral-light: jp.grey,
    ),
    config-store(
      footer: footer,
      logo: logo,
      subslide-preamble: self => block(below: 0.9em, {
        text(1.15em, weight: "bold", fill: jp.indigo, utils.display-current-heading(level: 2))
      }),
    ),
    ..args,
  )
  body
}
