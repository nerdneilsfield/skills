---
name: grill-me
description: "Use when the user explicitly asks to be grilled, stress-tested, or challenged on a plan, design, or decision. Surface unresolved choices that can change behavior, constraints, or implementation, each with a recommended default, and finish with a consensus summary. Not for implementing that plan (counterweight) or writing the design document."
license: MIT
metadata:
  author: DengQi
---

# Grill Me

Surface unresolved choices; do not implement the plan (`counterweight`) and do not write the design document from this skill.

Find facts yourself from the repository, code, Git, tools, and documentation that names the decision. Ask the user only for decisions; do not turn missing confidence into questions.

Work in rounds. By default, ask one to three independent material questions whose prerequisites are already settled. Defer a question when its meaning depends on an earlier answer. Number the questions when there is more than one, and settle the whole round before moving to the next, because each answer moves the frontier.

For each question, give a recommended default and the reason, so the user can answer by correcting only what differs. **Phrase the question so that answering "yes" accepts your recommendation.** "Should we use a queue here?" is answerable; "how should we handle delivery?" is not, and pushes the work back to the user.

Challenge fuzzy or overloaded terms only when the ambiguity could change behavior or design. Cross-check important claims against the code and existing project guidance. When an abstract choice remains ambiguous, probe it with one concrete scenario or counterexample before expanding the question tree.

Do not ask about hypothetical future requirements, enumerate an exhaustive design tree, or ask for facts you can verify yourself.

## When the session ends

The session ends only when the set of open questions is empty: every question that could change behavior, constraints, acceptance criteria, or implementation has an answer, and none is left silently assumed. A round that leaves a question unanswered is not finished; ask again.

Do not act on the plan until the user confirms the shared understanding.

## Consensus summary

When the questions are settled, write one short summary and offer to hand it to `spec`:

```markdown
# <Topic>

## Decided
- <decision> — <reason>

## Rejected
- <option> — <why not>

## Still open
- <question> — <who decides, or what would settle it>

## Constraints that bound the plan
```

Keep it to decisions and constraints, not the conversation. Record only what changes the plan; a question whose answer changed nothing does not belong.

Stay stateless otherwise. If the user explicitly asks to preserve the outcome, prefer an existing task, spec, glossary, or decision artifact. An ADR-like record earns existence only when the decision is hard to reverse, surprising without context, and the result of a real trade-off. Do not create a documentation system or write every answer down.

If the user explicitly requests a deep or relentless grill, continue across rounds under the same rules. Go deeper on material decisions, not wider into hypothetical branches.

## Gotchas

- A question the user cannot answer from memory is a fact-finding task, not a question. Look it up yourself and decide.
- A compound question ("should we do X and Y?") cannot be answered by one word. Split it so each part has its own default.
- A question with no recommended default pushes the work back to the user. Propose one even when you are unsure, and say what you are unsure about.
- A deferred question that is never revisited is a silently assumed answer. Close it explicitly before ending.
- If every recommendation is accepted without discussion, the questions were either obvious or not real choices. Say so rather than claiming a thorough grill.
- A question the code, tests, or documentation already answers is not a decision. Resolve it yourself.
- The consensus summary is not a spec. Hand it to `spec` rather than expanding it here.
- Do not act on the plan while a question that could change it is still open.
