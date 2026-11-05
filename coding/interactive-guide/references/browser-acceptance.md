# Browser acceptance

Run this for a long guide, or when the user asks for acceptance, browser testing, or a responsive check. A request to build or polish does not trigger it. Say what you actually ran; an item you could not reach is unverified, not passed.

## Setup

Use browser tooling already available. Open the built file directly, so that the page proves it needs no server. Keep any scratch install in a temporary directory, and delete it afterwards. If screenshots hang, assert on the DOM instead and say so.

Default widths: 390 by 844, 768 by 1024, and 1440 by 900. For slides, add 1280 by 720 and one window with a different shape.

## Runtime

- No uncaught errors or console errors on any page. Sort CDN failures from page bugs.
- No failed local request. Every image has a non-zero `naturalWidth`.
- An `--offline` build makes no network request.

## Layout

- `document.documentElement.scrollWidth` is at most the window width at each width.
- Tabs scroll on a phone and the active tab stays reachable.
- Wide tables, code, and formulas scroll inside their own box.
- A single-page guide and an answer page show no tabs or pager.
- `⚠ 未指定` is visible wherever a fact is missing, and `assumptions` appear under the summary.

## Interaction

- Every tab opens, the hash follows, and reload returns to the same page.
- Flows: step, play, pause, switch flow, arrow keys, and the last step.
- Quiz: right and wrong answers both respond and show the explanation.
- Graph: nodes appear in a non-zero container, search filters, a tap fills the side panel, and the 3D toggle works where WebGL exists.
- Figure tour: the highlight stays on the image at each stop.
- Highlights: select, colour, note, reload, export, delete.

## Slides

- `?present` opens on the cover, and the toolbar button opens at the current page.
- Clicking blank space, arrows, Space, Home, and End all move; a click on a control does not.
- The stage stays 16:9 at every window shape, with nothing stretched.
- A flow on a slide still works by keyboard, and Esc returns to the page last shown.

## Preferences

- With reduced motion set, flows finish and nothing depends on animation.
- Light and dark colour schemes both stay readable.
- Keyboard focus is visible on tabs, flow nodes, and quiz options.

## Report

List the file, browser, widths, and the result per section. Fix what fails in scope, rerun that section, and name what stayed unverified.
