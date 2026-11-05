# Blocks

A guide is `{title, summary, repo, commit, pages[]}`. A page is `{id, title, level, intro, blocks[]}`, and each page becomes a tab. Set `type` on each block.

| type | Fields | Use for |
| --- | --- | --- |
| `text` | `md` | Markdown prose |
| `callout` | `md`, `title`, `kind` (`warn`, `check`, or empty) | The one thing to remember, or a trap |
| `code` | `code`, `file`, `line` | A short excerpt with its location |
| `figure` | `src`, `alt`, `caption`, `source`, `origin` (`paper`, `explain`), `ref` | A local image, always inlined as base64. `origin` shows whose figure it is |
| `figuretour` | `src`, `alt`, `caption`, `origin`, `ref`, `stops[{x, y, w, h, title, md}]` | Step through regions of one figure. Coordinates are percentages of the image |
| `papercode` | `items[{paper, where, file, line, code, status, note}]`, `status` is `match`, `differs`, or `unstated` | Paper-to-code comparison, with a filter by status |
| `claim` | `kind` (`author`, `evidence`, `inference`, `unknown`), `md`, `where` | Keep a claim, its evidence, and your inference visibly apart |
| `compare` | `headers[]`, `rows[][]` | Trade-offs |
| `steps` | `items[]` | An ordered procedure |
| `terms` | `items[{term, meaning}]` | Vocabulary |
| `quiz` | `question`, `options[]`, `answer` (index), `explain` | Check understanding before moving on |
| `formula` | `tex` | KaTeX display math |
| `mermaid` | `code` | A quick diagram |
| `flow` | `nodes[{id, label, layer, summary, file, line}]`, `edges[{from, to, verified}]`, `flows[{title, steps[{from, to, title, explain, code, file, line, verified}]}]` | Animated call or process flow. At most 12 nodes; `from` is `null` on the first step |
| `graph` | `nodes[{id, label, kind, summary, file, line}]`, `edges[{from, to, rel, verified}]` | Explorable knowledge graph, 2D with a 3D toggle |

To add a component, use `--keep`, write `render(block)` returning an element in `src/blocks/`, register it in `src/blocks/index.js`, and rebuild. Unknown types fail validation, so add reusable ones to this skill's template and to `BLOCKS` in the builder.

Every page also lets the reader select text to highlight it in three colours, add a note, and export all of it as Markdown. No data field is needed.

`assets/example.json` uses every block type.
