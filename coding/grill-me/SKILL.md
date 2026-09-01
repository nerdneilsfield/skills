---
name: grill-me
description: Clarify a plan, design, or implementation by asking only the unresolved decisions that materially change it; use when the user asks to be grilled or when blocking choices cannot be discovered from available facts.
---

# Grill Me

Find facts yourself from the repository, code, Git, tools, and relevant documentation. Ask the user only for decisions that materially change the real implementation.

By default, ask one to three related blocking questions in a round. For each question, give a recommended default and the reason, so the user can answer by correcting only what differs. Combine choices that can be decided independently; defer a question whose meaning depends on an earlier answer.

Do not ask about hypothetical future requirements, enumerate an exhaustive design tree, seek confidence through questions, or delegate fact lookup unless doing so has clear context-isolation value. Stop questioning as soon as the implementation shape is determined.

If the user explicitly requests a deep or relentless grill, continue across rounds, but pursue only decisions that remain capable of changing the design. Do not require every possible branch to be discussed and do not block action on facts you can verify yourself.
