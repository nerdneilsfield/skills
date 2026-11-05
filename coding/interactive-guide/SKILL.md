---
name: interactive-guide
description: "Use when the user wants an interactive page instead of a document: to see how a codebase works through animated call flows, or to learn a field from beginner to expert over many tabs, with quizzes, figures, formulas, and a knowledge graph. Builds one HTML file from an npm component template. For one paper, use qi-read-paper. Not for a written repository map (code-reading), a report (research-report), or a single answer."
license: MIT
compatibility: Needs python3, Node with npm, and network to build. Pages load libraries from a CDN unless built offline. The 3D view needs WebGL.
metadata:
  author: DengQi
---

# Build an interactive guide

`assets/app/` is a Vite project with ready components, not a page. You write data; the builder validates it, copies the project to a temporary directory, installs, and builds one HTML file. Keep the look, Japanese traditional colours and editorial type, unless the user asks otherwise. Never hand-write the HTML.

## 1. Choose the path

- **Code walkthrough:** use `code-reading` to trace real calls at a pinned commit. Pick one to three questions a reader would ask. Pages run overview, structure, call flow, then graph.
- **Learning path:** treat the reader as a complete beginner and aim to make them an expert. List what an expert can do, then work backwards through the prerequisites. For research material, use `paper-search` and cite what you read. Expect many tabs.

Either way, go shallow to deep. Each page assumes only the pages before it. Set `level` to show progress, and end each stage with a `quiz` or a task that proves it was learned.

## 2. Write the data

Read [the block catalogue](references/blocks.md), and compose pages from those blocks. [`assets/example.json`](assets/example.json) uses each one. Explain why, not what the line says. Excerpts are copied from the source, 12 lines at most. Write in the user's language.

A long guide should be drafted page by page. Keep one data file as the single source.

## 3. Make the figures

Good guides lean on figures. Use a schematic and an architecture diagram in one image, in the style of recent paper figures: the intuition beside the components, with labelled parts and arrows.

Pick the first source available:

1. The running agent's own image generation tool. Agents such as Codex, Grok, and Antigravity have one; Claude Code does not.
2. Another available agent that has one: send it the prompt and an output path through `agent-brief`, then check the file.
3. The drawing MCP the user provides.
4. SVG or a `mermaid` block.

Use a generated image for explanation, never for data or exact numbers. Request a calm, flat style on an off-white ground, in indigo, vermilion, and ink. Keep labels short, since generated text is often wrong. Save each file beside the data, set `source` to the prompt or tool, and look at it before keeping it. Redraw as SVG if the labels stay wrong.

## 4. Build and check

```sh
python3 scripts/build_guide.py guide.json guide.html --repo /path/to/repo
```

Run from this skill's directory. Omit `--repo` for a guide not about a repository. `--check` validates without building.

Images are always embedded as base64, so the file can be moved alone. Remote image URLs are rejected: download them first, and check their licence. Libraries come from pinned CDN URLs by default. Add `--offline` only when the user asks for a page that works without network.

For something the components cannot do, run with `--keep`, add React, Vue, three.js, or any npm package to the kept project with an exact version, and run `npm run build`. If a component is reusable, propose adding it to the template.

Open the page, or render it if you can. Walk every tab and flow, and check the console.

## Gotchas

- Unverified calls are the main risk. Mark them `verified: false`; the page draws them dashed. Dynamic dispatch and callbacks hide the real target from search.
- The validator proves a location exists, not that it shows the claim. Reread each excerpt against its `line`.
- Image data makes the file large. Compress PNGs, and prefer SVG for diagrams.
- A knowledge graph shows what relates, not what runs next. Keep call order in `flow` blocks.
- A beginner page full of jargon has failed. Introduce each term before using it, and test it in a quiz.
- Quizzes that restate the previous sentence teach nothing. Ask the reader to apply the idea.
- Default pages need network for graphs, formulas, and Mermaid. Say so when handing one over.
- Line numbers rot. Always record `commit`, and rebuild after a rebase.
- A page holds code excerpts. Do not publish one from a private repository without asking.

## Report

State the commit or sources, the pages and flows, how many steps are inferred, each figure's origin, and the output path and size.
