---
name: deai
description: Use when editing, reviewing, or rewriting Chinese or English prose that feels AI-generated, templated, overly promotional, repetitive, vague, chatbot-like, bureaucratic, paternalistic, or governance-heavy; also when auditing AI-writing signals, defensive writing (ungrounded hedging, self-undermining, claim retraction, 防御性写作/自我削弱/心虚表述), or reviewer-prebuttal tone in LaTeX, Typst, Markdown, or plain text.
---

# De-AI writing assistant

Make prose less templated while preserving meaning, facts, format, and the writer's voice. Detector scores vary by tool and genre; never promise a score, plagiarism result, or “human” verdict.

## Rules

- Never add facts, numbers, dates, citations, sources, personal experiences, emotions, or opinions absent from the input or an explicitly supplied style sample.
- Preserve actors, targets, conditions, scope, negation, modality, completion state, direction, intensity, cause/effect, and responsibility.
- Protect code fences, inline code, URLs, paths, commands, environment variables, identifiers, LaTeX/Typst and math, citations/labels, quotations, names, versions, dates, ranges, units, status codes, metrics, and formal terms. Keep them byte-for-byte unless the user asks to edit them.
- A supplied writing sample is a voice constraint. Do not blanket-ban adverbs, passive voice, dashes, tricolons, headings, first person, or repetition when grammar, genre, technical meaning, quotation, or the sample supports them.

## Workflow

1. Parse target, language, scene, `--mode check|rewrite|audit|style-profile`, model profile, format, and explicit constraints. Choose the scene before judging a signal:

   | Scene | Default posture |
   |---|---|
   | Academic, technical, status, specification | Minimal edits; preserve conventions, evidence, terminology, and responsibility |
   | Short message, reply, review comment | Answer first; remove chatbot residue and needless framing |
   | Public article, blog, essay | Check stance, emphasis, paragraph purpose, and venue voice |
   | Narrative or creative prose | Preserve POV, characterization, and supplied scene detail; do not inject quirks or biography |

   For detailed scene rules and document-level checks, read `references/REWRITING_GUIDE.md`. Use the most conservative scene when text mixes genres.
2. Diagnose before editing. Run the candidate scanner:

   ```bash
   python3 $SKILL_DIR/scripts/deai_check.py <file> --analyze --lang <zh|en|mixed|auto> --profile <generic|deepseek|claude|mixed>
   ```

   The script finds lexical and measurable structural candidates; it does not assess authorship or replace document-level review. Inspect four layers in order: document architecture, paragraph/discourse flow, sentence structure, then vocabulary/punctuation. Quote the shortest evidence for each finding. Treat isolated low-signal hits as normal variation; act on unsupported high-signal defects or clusters.
3. For `check` (default), stop after diagnosis. Report scene, quoted findings by layer, legitimate exceptions, and a `clean|isolated|cluster` editorial verdict. Do not edit.
4. For `rewrite`, read the language reference (`PATTERNS_ZH.md` or `PATTERNS_EN.md`) after diagnosis; when the `defensive` category fires or the task is paper-level academic writing, also read `references/DEFENSIVE_WRITING.md` and run its claim audit on any LLM- or reviewer-shaped source text. Default to minimal in-place refactoring. Fix the deepest confirmed layer first and change only supported defects. Recreate the whole piece only when the user requests a full rewrite; first extract a fact/claim/intent ledger, then verify the result against it. Return one recommended version plus a compact change log with location, original, revision, action type, and reason.
5. For `audit`, record the baseline, perform the requested rewrite, rerun the same scanner, then compare findings, meaning, protected spans, and requested counts. Report `PASS`/`FAIL`; tool scores are tool-specific heuristics, never proof of authorship.
6. For `style-profile`, run `style_profile.py` and use its output as a constraint, never as permission to clone signature phrases or invent personal detail.

## Coverage contract

Do not silently drop a detection family. Review: overly neat or symmetrical document shape; paragraph-purpose and question-sequence repetition; repeated skeletons; template openings, transitions, contrasts, lists, conclusions, and meta-commentary; empty praise and inflated significance; over-confident or unsupported authority claims; vague quantifiers; model-associated vocabulary and punctuation clusters; chatbot artifacts and sycophancy; excessive structure, uniform rhythm, false agency, synonym cycling, decorative detail, and governance overreach (directive inflation, speech-policing, preventive rulemaking, or reader distrust outside a scene that requires it); defensive writing (ungrounded qualifications, self-undermining wording, apology framing, reviewer prebuttal, generic scope restrictions, and weakened, scoped, or retracted claims the source supports — see `references/DEFENSIVE_WRITING.md`; never fix it by adding confidence the evidence does not support). Apply scene, false-positive, quotation, and author-sample exceptions before recommending an edit.

Use these action labels in change logs; they are an audit vocabulary, not mandatory edits:

- `skeleton_vary`: change a repeated structure; `vary_parallelism`: break mechanical parallelism.
- `delete_empty`: remove empty wording; `delete_connector`: remove redundant signposting.
- `replace_template`: state the actual point directly; `replace_vocabulary`: use the natural word when meaning is unchanged.
- `add_specific`: use only source-provided detail; otherwise note the evidence gap.
- `downgrade_claim`: narrow certainty to what the evidence supports, without changing a sourced claim.
- `delete_hedge`: remove an ungrounded qualification, apology wrapper, or prebuttal sentence; keep any factual core.
- `restore_claim`: return a weakened, scoped, or retracted claim to the strength the source supports; audit against evidence, never automatic.
- `restate_scope`: convert "we do not claim X" and generic-scope hedges into one positive scope or limitation statement. (Scanner signal: `negative_scope`; not to be confused with `scope_restore`, which strips governance machinery from a document that never owned it.)
- `split_sentence`: split an overloaded sentence only when scope and logic remain intact.
- `merge_fragments`: join choppy fragments only when emphasis, order, and meaning remain intact.
- `scope_restore`: remove or relocate unrequested governance machinery and restate the underlying technical invariant once.

## User constraints

- “Do not delete”, “keep sentence count”, or “preserve exactly”: do not delete, merge, or reorder sentences; edit wording in place.
- “Preserve length/保长度”: treat as a hard invariant. Use the user's metric and tolerance; if none is given, preserve Chinese character count, English word count, and sentence count exactly. Report metric, tolerance, before/after counts, and `PASS`/`FAIL`.
- Unsupported authority (“studies show”, “据研究”): never invent attribution. In technical, status, and academic text, flag it `audit-only` by default; in chat/public prose, remove the wrapper only when the remaining claim stands alone. Put `[PENDING]`/`[SOURCE NEEDED]` in notes, not final prose, unless explicitly requested.

Detailed patterns and format safeguards live in `references/REWRITING_GUIDE.md`, `references/PATTERNS_ZH.md`, `references/PATTERNS_EN.md`, and `references/DEFENSIVE_WRITING.md`.
