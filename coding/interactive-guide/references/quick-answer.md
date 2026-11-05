# Quick answer page

One question, one short page. Use it when the user asks for a page, or when a relation, flow, or comparison is hard to follow as text. A plain answer in chat is better for everything else.

## Decide alone or ask

Decide alone, and put the choice in `assumptions`, when a reasonable reader would accept the default, or when you can check the fact yourself. Reader level, language, and output path are nearly always of this kind.

Ask, once and in one message, only when two plausible readings of the question give different answers, or when the answer rests on a fact only the user has. In an unattended run, answer the likelier reading and record it in `assumptions`.

There are no plan or first-spread stops, and no final review.

## Shape

```json
{
  "mode": "answer",
  "title": "The question, in the reader's words",
  "summary": "The answer in one or two sentences.",
  "assumptions": ["Assumes the default build; a static build differs."],
  "blocks": [
    {"type": "mermaid", "code": "flowchart LR; A-->B"},
    {"type": "callout", "md": "The one trap worth remembering."}
  ]
}
```

The builder requires 2 to 4 blocks. `assets/example-answer.json` is a full example. The answer goes in `summary`, so a reader who stops there still has it. Then give what supports it: usually one figure, `compare`, `flow`, or `mermaid`, and one `text` or `callout`.

If the answer needs a fifth block, either cut it or make a normal guide. Do not add a quiz, a graph, or a list of terms for bulk.
