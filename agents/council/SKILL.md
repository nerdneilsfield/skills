---
name: council
description: "Use when a decision has several credible paths and no obvious winner, or the user asks for second opinions, dissent, or a go/no-go call: get independent positions from a skeptic, a pragmatist, and a critic before you commit, then surface the disagreement instead of hiding it. Not for code review, implementation, or a question with one defensible answer."
license: MIT
compatibility: Needs a way to start independent agents or fresh sessions, such as built-in subagents or an agent runtime. Works with any of them.
metadata:
  author: DengQi
disable-model-invocation: true
---

# Convene a council before committing

The value is not agreement. It is making the disagreement legible before the decision is made.

Use this for ambiguous choices: two architectures, ship or hold, simplify or keep breadth, one dependency or another. Do not use it for code review, implementation planning, or a factual question you can answer.

## 1. Reduce the decision to one question

Write down: what is being decided, which constraints bind, and what counts as success. If the question is still vague, ask one clarifying question first.

## 2. Write your own position before reading anyone else's

Record your initial position, the two or three strongest reasons for it, and the main risk in it. Do this first, so the synthesis cannot simply mirror the external voices.

## 3. Gather only the context the decision needs

The relevant files, numbers, and constraints, kept compact. Do not hand over the whole conversation.

## 4. Get three independent positions

Each voice gets the question, the compact context, and its own role, with no shared history between them. Start them independently, so none anchors on another.

- **Skeptic** — challenge the framing, question the assumptions, propose the simplest credible alternative.
- **Pragmatist** — optimize for shipping, effort, and operational reality.
- **Critic** — surface downside risk, edge cases, and how the plan fails.

Ask each for: position, reasoning, the biggest risk in its own recommendation, and one thing the others may miss.

Give them the evidence and the question, not your conclusion. A voice handed a conclusion returns it confirmed.

## 5. Synthesize without flattening

- Do not dismiss an external view without saying why.
- If a voice changed your position, say so explicitly.
- Always include the strongest dissent, even when you reject it.
- If two voices align against your initial position, treat that as a real signal, not noise.
- Keep the raw positions visible before the verdict.

```markdown
## Council: <decision>

**Your initial position:** ...

**Skeptic:** ...
**Pragmatist:** ...
**Critic:** ...

### Verdict
- Consensus:
- Strongest dissent:
- Premise check: did the skeptic challenge the question itself?
- Recommendation, and what would change it:
```

## Gotchas

- Handing the voices your conclusion gets it echoed back. Give the question and the evidence.
- A voice that only agrees has added nothing. Ask it again for the strongest case against.
- Hiding the dissent to keep the summary tidy defeats the exercise. Report it, even when overruled.
- Four voices on a decision with one defensible answer is waste. Answer directly when the answer is clear.
- Do not run this for code review or implementation; it is a decision tool, not a verification tool.
- The council advises; it does not authorize. Pushing, publishing, and deleting still need the user's word.
- Persisting the outcome is not automatic. Write it down only when the decision changes something real.
- If a voice cannot be started independently, say so and fall back to writing the three positions yourself, marked as such.

## Report

State the decision, the three positions, the strongest dissent, the recommendation, and what new evidence would change it.
