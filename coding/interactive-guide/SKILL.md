---
name: interactive-guide
description: "Use when the user wants an interactive page instead of a document: to see how a codebase works through animated call flows, or to learn a field from beginner to expert over many tabs, with quizzes, figures, formulas, and a knowledge graph. Also answers one question as a short page when the user asks for a page or the answer needs a picture. Builds one HTML file from an npm component template, with an optional 16:9 slide view. For one paper, use qi-read-paper. Not for a written repository map (code-reading), a report (research-report), or an answer that plain text serves."
license: MIT
compatibility: Needs python3, Node with npm, and network to build. Pages load libraries from a CDN unless built offline. The 3D view needs WebGL.
metadata:
  author: DengQi
---

# Build an interactive guide

`assets/app/` is a Vite project with ready components, not a page. You write data; the builder validates it, copies the project to a temporary directory, installs, and builds one HTML file. Keep the look, Japanese traditional colours and editorial type, unless the user asks otherwise. Never hand-write the HTML.

## 1. Intake

Before writing, list the facts the build depends on: the question or field, the reader's level, the sources (repository and commit, or materials), the language, and the output path. Find what you can yourself. For the rest, ask once, in one message, as a numbered list with a recommended default for each, then wait. Do not spread questions over several turns, and do not ask about what a default settles well.

If no user can reply, as in a scheduled or delegated run, decide, write each decision in `assumptions`, and continue. Never fill a missing fact with a guess: leave the field empty, and the page shows `⚠ 未指定`.

## 2. Choose the path

- **Code walkthrough:** use `code-reading` to trace real calls at a pinned commit. Pick one to three questions a reader would ask. Pages run overview, structure, call flow, then graph.
- **Quick answer:** one question, one short page, 2 to 4 blocks. Follow [the quick answer notes](references/quick-answer.md), which set when to ask and when to decide alone.
- **Learning path:** treat the reader as a complete beginner and aim to make them an expert. List what an expert can do, then work backwards through the prerequisites. For research material, use `paper-search` and cite what you read. Expect many tabs.

For a walkthrough or a learning path, go shallow to deep. Each page assumes only the pages before it. Set `level` to show progress, and end each stage with a `quiz` or a task that proves it was learned.

A guide of six or more pages, or one the user calls long, is a long guide: follow [the long-guide workflow](references/long-guide.md), whose checkpoints are plan, first spread, full build, and [a three-view final review](references/review.md). Shorter guides skip them.

## 3. Write the data

Read [the block catalogue](references/blocks.md), and compose pages from those blocks. [`assets/example.json`](assets/example.json) uses each one. Explain why, not what the line says. Excerpts are copied from the source, 12 lines at most. Write in the user's language.

Data is one JSON file, or for a long guide a directory: `guide.json` holds the metadata and lists its pages, and each section is its own `pages/NN-name.json`. Keep every image path relative to `guide.json`. List a page only once it is written, since a listed file that is missing stops the build. Add `assumptions` as a list of strings to show unconfirmed decisions under the summary.

## 4. Make the figures

Good guides lean on figures. Use a schematic and an architecture diagram in one image, in the style of recent paper figures: the intuition beside the components, with labelled parts and arrows.

Use `research-figure` to choose the backend and make each figure, whichever agent is running. Without that skill, use SVG or a `mermaid` block.

## 5. Build and check

```sh
python3 scripts/build_guide.py guide.json guide.html --repo /path/to/repo
```

Run from this skill's directory. The first argument may be a guide directory instead of a file. Omit `--repo` for a guide not about a repository. `--check` validates without building.

Warnings do not stop the build, but read each one: it names a field the page marks as missing, a page file not listed, or an image that is too large. PNGs over 800 KB go through the first of `pngquant`, `oxipng`, or `optipng` installed, and the source file stays as it was. With none installed, the original is embedded with a warning. Pass `--no-compress` when exact colours matter.

Images are always embedded as base64, so the file can be moved alone. Remote image URLs are rejected: download them first, and check their licence. Libraries come from pinned CDN URLs by default. Add `--offline` only when the user asks for a page that works without network.

For something the components cannot do, run with `--keep`, add React, Vue, three.js, or any npm package to the kept project with an exact version, and run `npm run build`. If a component is reusable, propose adding it to the template.

Open the page, or render it if you can. Walk every tab and flow, and check the console. Run [the browser acceptance list](references/browser-acceptance.md) only when the user asks for it or for a long guide. Use [the failure patterns](references/failure-patterns.md) when the page looks generated.

Add `?present` to the URL, or press 演示 in the toolbar, for 16:9 slides: a cover, then one block per click. Arrow keys and Space move, and Esc leaves. A tall block shrinks to fit, then scrolls.

## Gotchas

- Unverified calls are the main risk. Mark them `verified: false`; the page draws them dashed. Dynamic dispatch and callbacks hide the real target from search.
- The validator proves a location exists, not that it shows the claim. Reread each excerpt against its `line`.
- Image data makes the file large. Prefer SVG for diagrams. `pngquant` is lossy, so look at small labels after compressing.
- A slide shows one block, so a page of ten short blocks takes ten clicks. Merge blocks that make one point before presenting.
- A knowledge graph shows what relates, not what runs next. Keep call order in `flow` blocks.
- A beginner page full of jargon has failed. Introduce each term before using it, and test it in a quiz.
- Quizzes that restate the previous sentence teach nothing. Ask the reader to apply the idea.
- Code is syntax-coloured for C and C++, Python, JS and TS, Rust, Go, shell, CMake, JSON, YAML, TOML, and diffs. Set `lang` when a snippet has no `file`, or detection may guess wrong.
- Reader highlights live in that browser's local storage, keyed by the guide title. Keep the title stable when rebuilding, and tell the reader to use the export button to keep them.
- Default pages need network for graphs, formulas, and Mermaid. Say so when handing one over.
- Line numbers rot. Always record `commit`, and rebuild after a rebase.
- A page holds code excerpts. Do not publish one from a private repository without asking.

## Report

State the commit or sources, the pages and flows, how many steps are inferred, each figure's origin, any `⚠ 未指定` left and any assumptions, and the output path and size.
