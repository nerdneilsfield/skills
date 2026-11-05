# Scene templates

Each template in `assets/` is a runnable `.typ` that imports `theme.typ`. Copy `theme.typ` and the template into one folder. Every template compiles as shipped; replace the sample sentences and keep the page structure.

| Scene | File | Length | Structure |
|---|---|---|---|
| Research talk, group meeting | `research-talk.typ` | 15-20 min, about 12 slides | Claim with one number, problem and question, method diagram, results table, ablation, limits and next steps, takeaway, backup |
| Project review | `project-review.typ` | 10-15 min, 8 slides | Status and decision, milestone table with colour status, evidence, risks with owner, asks |
| Defence or proposal (Chinese) | `defense.typ` | 15-25 min, 9 slides | Conclusion, question and gap, contributions, method and results per contribution, limits, plan, closing, backup |
| Client demo or pitch | `client-demo.typ` | 10-20 min, 7 slides | Their problem, what changes, demo cue, reference proof, pilot plan, next step; confidentiality footer and logo placeholders |
| Technical sharing | `tech-share.typ` | 20-40 min, 7 slides | Symptom, options compared, design diagram, code, measured result, trade-off, takeaway |
| Teaching lecture | `lecture.typ` | 45 min, 6 slides plus reveals | Goals, recall, concept with equation, worked example, exercise with hidden answer, recap |

For a five-minute pitch, take `client-demo.typ` and keep the problem, the change, the proof, and the next step.

## Customising

- Title, author, date, footer: the `config-info(...)` and `footer:` arguments at the top.
- Language: `lang: "zh"` for Chinese; fonts are in `theme.typ`. `defense.typ` is the Chinese example.
- Logo: pass `logo: image("logo.svg", height: 1.4em)`; the templates default to `logo-slot()` placeholders.
- Aspect ratio: `aspect-ratio: "4-3"` if the room needs it.
- Figures: AI-generated images come from the `research-figure` skill (pick the backend there) and are inserted with `image(...)`; keep text, numbers, and labels in Typst, not baked into pictures. Diagrams are drawn with fletcher or CeTZ (see `references/typst-syntax.md`).

## Client decks

Mark confidentiality in the footer, keep the audience's name only where it is theirs, and remove speaker notes and TODO placeholders before sending. Logos belong to their owners: use the files they provide, never one scraped from the web. Statistics and reference customers need a source or written permission, as the template comments say.
