---
name: grill-me
description: Stress-test a plan, design, or decision by surfacing unresolved choices that can materially change behavior, constraints, or implementation. Use when the user explicitly asks to be grilled or wants a plan pressure-tested.
---

# Grill Me

Find facts yourself from the repository, code, Git, tools, and relevant documentation. Ask the user only for decisions; do not turn missing confidence into questions.

Work in rounds. By default, ask one to three independent material questions whose prerequisites are already settled. Defer a question when its meaning depends on an earlier answer. For each question, give a recommended default and the reason, so the user can answer by correcting only what differs.

Challenge fuzzy or overloaded terms only when the ambiguity could change behavior or design. Cross-check important claims against the code and existing project guidance. When an abstract choice remains ambiguous, probe it with one concrete scenario or counterexample before expanding the question tree.

Do not ask about hypothetical future requirements, enumerate an exhaustive design tree, or ask for facts you can verify yourself. Stop when no unresolved decision can materially change the requested behavior, constraints, acceptance criteria, or implementation.

Stay stateless by default. If the user explicitly asks to preserve the outcome, prefer an existing task, spec, glossary, or decision artifact. Record only resolved terminology and decisions worth preserving. An ADR-like record earns existence only when the decision is hard to reverse, surprising without context, and the result of a real trade-off. Do not create a documentation system or write every answer down.

If the user explicitly requests a deep or relentless grill, continue across rounds under the same rules. Go deeper on material decisions, not wider into hypothetical branches.
