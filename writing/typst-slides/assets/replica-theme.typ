// Skeleton for reproducing another template in Touying. Fill `spec` from the JSON made by
// scripts/pptx_spec.py (or from measurements of a PDF/image template), then compile deck-replica.typ.
// Positions are percent of the slide, as printed by the extractor ("x%", "y%", "w%", "h%").
// Keep decor/logo as placeholders unless the user owns the artwork. See references/replicate-template.md.
#import "@preview/touying:0.8.0": *

#let spec = (
  size: (33.87cm, 19.05cm),        // slide_size.cm; point sizes below then match the original 1:1
  bg: rgb("#FFFFFF"),              // master background
  text: rgb("#222222"),            // bodyStyle colour
  title-color: rgb("#165E83"),     // master title colour, or slide title_run_style if the master is plain
  accent: rgb("#EB6101"),          // accent1 or the colour the template uses for emphasis
  font: ("Noto Sans CJK SC",),     // theme minor font; install it or pick the nearest installed one
  title-font: auto,                // auto = same as font
  title: (x: 5%, y: 5%, w: 90%, h: 14%, size: 28pt, weight: "bold"),
  body: (x: 5%, y: 24%, w: 90%, h: 62%, size: 20pt),
  cover-title: (x: 5%, y: 30%, w: 70%, h: 25%, size: 48pt),
  cover-subtitle: (x: 5%, y: 60%, w: 60%, h: 15%, size: 22pt),
  footer: (x: 5%, y: 92%, w: 40%, h: 4%, size: 10pt),
  number: (x: 88%, y: 92%, w: 8%, h: 4%, size: 10pt),   // shows "n / N"; keep the box wide enough
  decor: (),   // shapes behind every slide: (x: 0%, y: 0%, w: 100%, h: 3%, fill: rgb("#165E83"))
  logo: none,  // e.g. (x: 90%, y: 3%, w: 7%, content: image("logo.svg")), or a dashed placeholder
)

// A box placed at percent coordinates of the whole page.
#let at(box-spec, body) = place(top + left,
  dx: box-spec.x * spec.size.at(0), dy: box-spec.y * spec.size.at(1),
  box(width: box-spec.w * spec.size.at(0), height: box-spec.h * spec.size.at(1), body))

#let decor-layer = {
  for d in spec.decor { at((x: d.x, y: d.y, w: d.w, h: d.h), rect(width: 100%, height: 100%, fill: d.fill, stroke: none)) }
  if spec.logo != none { at((x: spec.logo.x, y: spec.logo.y, w: spec.logo.w, h: 10%), spec.logo.content) }
}

#let slide(config: (:), repeat: auto, setting: body => body, composer: auto, ..bodies) = touying-slide-wrapper(self => {
  let pos = spec.body
  let (W, H) = spec.size
  self = utils.merge-dicts(self,
    config-page(
      margin: (left: pos.x * W, top: pos.y * H,
               right: W - (pos.x + pos.w) * W, bottom: H - (pos.y + pos.h) * H),
      background: { decor-layer },
      foreground: {
        at(spec.footer, align(left + horizon, text(spec.footer.size, fill: spec.text.transparentize(30%), utils.call-or-display(self, self.store.footer))))
        at(spec.number, align(right + horizon, text(spec.number.size, fill: spec.text.transparentize(30%), context utils.slide-counter.display() + " / " + utils.last-slide-number)))
      },
    ),
    config-common(subslide-preamble: self.store.title-fn),
  )
  touying-slide(self: self, config: config, repeat: repeat, setting: setting, composer: composer, ..bodies)
})

#let title-slide(config: (:), ..args) = touying-slide-wrapper(self => {
  self = utils.merge-dicts(self, config-common(freeze-slide-counter: true),
    config-page(margin: 0pt, background: decor-layer, foreground: none))
  touying-slide(self: self, config: config, {
    at(spec.cover-title, align(left + bottom, text(spec.cover-title.size, weight: "bold", fill: spec.title-color, self.info.title)))
    if self.info.at("subtitle", default: none) != none {
      at(spec.cover-subtitle, align(left + top, text(spec.cover-subtitle.size, self.info.subtitle)))
    }
  })
})

/// Section divider for `=` headings: a plain slide showing the heading, no counter step.
#let section-slide(config: (:), body) = touying-slide-wrapper(self => {
  self = utils.merge-dicts(self, config-common(freeze-slide-counter: true),
    config-page(margin: 0pt, background: decor-layer, foreground: none))
  touying-slide(self: self, config: config, {
    at(spec.cover-title, align(left + horizon, text(spec.cover-title.size, weight: "bold", fill: spec.title-color,
      utils.display-current-heading(level: 1, numbered: false))))
    body
  })
})

#let replica-theme(footer: none, ..args, body) = {
  let (W, H) = spec.size
  let tx = spec.title
  let title-fn = self => {
    // The title sits at its own box; negative offsets are relative to the body area.
    let b = spec.body
    place(top + left, dx: (tx.x - b.x) * W, dy: (tx.y - b.y) * H,
      box(width: tx.w * W, height: tx.h * H,
        align(left + horizon, text(tx.size, weight: tx.weight, fill: spec.title-color, utils.display-current-heading(level: 2)))))
    v(0pt)
  }
  show: touying-slides.with(
    config-page(width: W, height: H, fill: spec.bg, margin: 0pt),
    config-common(slide-fn: slide, title-slide-fn: title-slide, new-section-slide-fn: section-slide, zero-margin-header: false, zero-margin-footer: false),
    config-methods(init: (self: none, body) => {
      set text(font: spec.font, size: spec.body.size, fill: spec.text)
      show heading.where(level: 1): set text(fill: spec.title-color)
      body
    }, alert: (self: none, it) => text(fill: spec.accent, weight: "bold", it)),
    config-colors(primary: spec.title-color, secondary: spec.accent),
    config-store(footer: footer, title-fn: title-fn),
    ..args,
  )
  body
}
