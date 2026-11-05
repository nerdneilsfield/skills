# Technical diagrams

Structure is the content here, so the source comes first. Mermaid covers most types; move to SVG or box JSON when layout needs control. An image backend may restyle a finished diagram only if every label and edge is then checked against the source. Each entry gives when to use it, what to ask, the layout, and what to avoid. Facts from code or configuration beat asking; cite the file.

## System architecture

Route: `image`, or SVG for review documents. Mermaid: `flowchart` with subgraphs. Excalidraw: yes.

- **Use when:** showing components, their boundaries, and how data moves between them. Not for one request's timing (sequence).
- **Ask:** audience and level of zoom; tiers or trust boundaries; components in each; protocols on key links; the path to emphasise.
- **Default:** 16:9, `paper-line` or `blueprint`, left to right or layered top to bottom, colour by role with a legend.
- **Layout:** dashed containers for boundaries. One zoom level per diagram. The main path is straight and drawn in the accent colour; secondary links are thin. Numbered circles walk through a flow.
- **Avoid:** vendor logos, mixing logical and physical views, unlabelled arrows, more than about fifteen boxes. Split instead.

## Sequence diagram

Route: `source`. Mermaid: `sequenceDiagram`. Excalidraw: Mermaid converters handle it, but check the result.

- **Use when:** order matters across participants: API calls, handshakes, transactions, retries.
- **Ask:** scenario; participants left to right; messages in order, with sync or async; failure and retry branches; numbering.
- **Default:** caller on the left, solid arrows for calls, dashed for returns, numbered when cited in prose.
- **Layout:** participant heads on top, parallel lifelines, activation bars, `alt` and `loop` frames with their conditions labelled.
- **Avoid:** implying order that the code does not guarantee, more than about eight participants, happy path only when failure is the point.

## State machine

Route: `source`. Mermaid: `stateDiagram-v2`. Excalidraw: use box JSON, because Mermaid state diagrams do not convert element by element.

- **Use when:** one entity, its lifetime, and what moves it between states.
- **Ask:** entity; states; initial and terminal states; transitions with event, guard, and action; nested or parallel states.
- **Default:** rounded states, `event [guard] / action` on arrows, top to bottom or left to right along the normal life.
- **Layout:** the common path is straight, with error and retry paths curving away from it. Self-loops sit on the state's outer side.
- **Avoid:** actions used as states, unlabelled transitions, dead-end states that the system does not have.

## Flowchart

Route: `source`. Mermaid: `flowchart`. Excalidraw: yes.

- **Use when:** steps and decisions: algorithms, procedures, triage. CONSORT and PRISMA flows also go here, with counts from the study and reconciled at every split.
- **Ask:** trigger and end; steps; each decision and its outcomes; failure paths; direction.
- **Default:** top to bottom, rectangles for steps, diamonds for decisions, rounded ends. Five to twelve nodes.
- **Layout:** main path on one axis, exceptions to the side, one exit per decision branch, every branch labelled.
- **Avoid:** unlabelled branches, diamonds used for steps, arrows crossing nodes, more than fifteen nodes. Split into subprocesses.

## ER diagram

Route: `source`. Mermaid: `erDiagram`. Excalidraw: use box JSON, for overview only.

- **Use when:** explaining a data model. Generate it from the schema or migrations if they exist.
- **Ask:** domain; entities; fields with key markers and types; relationships and cardinality; enums or constraints worth showing.
- **Default:** crow's foot notation, primary keys first, four to twelve entities.
- **Layout:** the central entity in the middle, with satellites around it. Join tables sit between what they join. Monospaced field rows.
- **Avoid:** relationships without cardinality, foreign keys without a target, stale fields when the schema is at hand.

## Network topology

Route: `source`. Mermaid: `flowchart` with subgraphs. Excalidraw: yes.

- **Use when:** showing hosts, zones, and links: VPCs, data centres, robot or sensor networks.
- **Ask:** site or scope; zones and subnets; devices; links with protocol and bandwidth; address ranges, and whether they may be published.
- **Default:** traffic enters from the top, one glyph per device kind, dashed zones.
- **Layout:** edge, then service, then data layers. Redundant pairs side by side. Link labels on the links.
- **Avoid:** vendor icons, real addresses or hostnames from private networks, inconsistent device glyphs, more than fifteen nodes.

## Mind map

Route: `source`. Mermaid: `mindmap`. Excalidraw: use box JSON.

- **Use when:** organising a field, a syllabus, or a stack as a hierarchy. Not for causality or sequence.
- **Ask:** central topic; four to eight main branches; children of each; depth; items to highlight.
- **Default:** radial, branch colour inherited by children, two levels shown, a third only where it matters.
- **Layout:** balance the branches around the centre. Sizes fall with depth. Keep related branches adjacent.
- **Avoid:** branches piled on one side, crossing links, full sentences in nodes, depth beyond three levels.
