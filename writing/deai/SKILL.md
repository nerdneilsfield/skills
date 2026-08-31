---
name: deai
description: Use when editing, reviewing, or rewriting Chinese or English prose that feels AI-generated, templated, overly promotional, repetitive, vague, or chatbot-like; also when auditing AI-writing signals in LaTeX, Typst, Markdown, or plain text.
---

# De-AI writing assistant

Make prose less templated while preserving meaning, facts, format, and the writer's voice. Detector scores vary by tool and genre; never promise a score, plagiarism result, or “human” verdict.

## Rules

- Never add facts, numbers, dates, citations, sources, personal experiences, emotions, or opinions absent from the input or an explicitly supplied style sample.
- Preserve actors, targets, conditions, scope, negation, modality, completion state, direction, intensity, cause/effect, and responsibility.
- Protect code fences, inline code, URLs, paths, commands, environment variables, identifiers, LaTeX/Typst and math, citations/labels, quotations, names, versions, dates, ranges, units, status codes, metrics, and formal terms. Keep them byte-for-byte unless the user asks to edit them.
- A supplied writing sample is a voice constraint. Do not blanket-ban adverbs, passive voice, dashes, tricolons, headings, first person, or repetition when grammar, genre, technical meaning, quotation, or the sample supports them.

## Workflow

1. Parse target, `--lang zh|en|mixed|auto`, `--mode check|rewrite|audit|style-profile`, `--profile`, format, and explicit user constraints. Use the most conservative interpretation when text mixes languages or genres.
2. For `check` (default), run:

   ```bash
   python3 $SKILL_DIR/scripts/deai_check.py <file> --analyze --lang <zh|en|mixed|auto> --profile <generic|deepseek|claude|mixed>
   ```

   Report high-signal traces and actionable edits; a hit is a review cue, not an automatic rewrite.
3. For `rewrite`, first run `check`, then read `references/REWRITING_GUIDE.md` and the language reference (`PATTERNS_ZH.md` or `PATTERNS_EN.md`). Fix structure before vocabulary, prefer deletion and direct verbs, and change only flagged prose. Return one recommended version plus a compact change log with location, original, revision, action type, and reason. Reread for fidelity and residual traces.
4. For `audit`, record the baseline check, rewrite flagged prose, rerun the same check, then compare before/after traces, meaning, protected spans, and user-requested counts. Report `PASS`/`FAIL`; report tool scores only as tool-specific heuristics, never as proof of authorship.
5. For `style-profile`, run `style_profile.py` and use its output as a constraint, never as permission to clone signature phrases or invent personal detail.

## Coverage contract

Do not silently drop a detection family. Review: repeated skeletons; template openings, transitions, contrasts, lists, conclusions, and meta-commentary; empty praise and inflated significance; over-confident or unsupported authority claims; vague quantifiers; model-associated vocabulary and punctuation clusters; chatbot artifacts and sycophancy; excessive structure, uniform rhythm, false agency, synonym cycling, and decorative detail. Apply the false-positive and section/genre rules in the language references before recommending an edit.

Use these action labels in change logs; they are an audit vocabulary, not mandatory edits:

- `skeleton_vary`: change a repeated structure; `vary_parallelism`: break mechanical parallelism.
- `delete_empty`: remove empty wording; `delete_connector`: remove redundant signposting.
- `replace_template`: state the actual point directly; `replace_vocabulary`: use the natural word when meaning is unchanged.
- `add_specific`: use only source-provided detail; otherwise note the evidence gap.
- `downgrade_claim`: narrow certainty to what the evidence supports, without changing a sourced claim.
- `split_sentence`: split an overloaded sentence only when scope and logic remain intact.
- `merge_fragments`: join choppy fragments only when emphasis, order, and meaning remain intact.

## User constraints

- “Do not delete”, “keep sentence count”, or “preserve exactly”: do not delete, merge, or reorder sentences; edit wording in place.
- “Preserve length/保长度”: treat as a hard invariant. Use the user's metric and tolerance; if none is given, preserve Chinese character count, English word count, and sentence count exactly. Report metric, tolerance, before/after counts, and `PASS`/`FAIL`.
- Unsupported authority (“studies show”, “据研究”): never invent attribution. In technical, status, and academic text, flag it `audit-only` by default; in chat/public prose, remove the wrapper only when the remaining claim stands alone. Put `[PENDING]`/`[SOURCE NEEDED]` in notes, not final prose, unless explicitly requested.

Detailed patterns and format safeguards live in `references/REWRITING_GUIDE.md`, `references/PATTERNS_ZH.md`, and `references/PATTERNS_EN.md`.
