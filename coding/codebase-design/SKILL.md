---
name: codebase-design
description: "Use when designing or improving a module's interface, deciding where a seam goes, or making code more testable: work in terms of deep modules, place the seam where something actually varies, and change structure only when the evidence justifies it. Not for implementing the change (counterweight), reviewing a diff (code-review), or reading a repository you have never seen (code-reading)."
license: MIT
metadata:
  author: DengQi
---

# Design deep modules

A module is deep when a lot of behaviour sits behind a small interface. The aim is leverage for callers, locality for maintainers, and a test surface that is the same surface callers use.

## Vocabulary

Use these words exactly, and do not substitute "component", "service", or "boundary":

- **Module** — anything with an interface and an implementation: a function, a class, a package.
- **Interface** — everything a caller must know: the signature, the invariants, the ordering, the error modes, the required configuration.
- **Depth** — behaviour per unit of interface a caller must learn.
- **Seam** — the place where the interface lives, where behaviour can change without editing there.
- **Adapter** — a concrete thing that satisfies an interface at a seam.

## Ask these before changing anything

1. What is the smallest interface that exposes the needed behaviour?
2. What actually varies across this seam? One adapter is a hypothetical seam; two are a real one.
3. Can a caller or a test exercise the behaviour through the interface alone? If a test must reach past the interface, the module is the wrong shape.
4. What would happen if this module were deleted? If the complexity vanishes, it was a pass-through.

## Design rules

- Accept dependencies; do not create them inside the module.
- Return results; do not mutate a caller's state as the primary effect.
- Keep the surface small. Fewer methods means fewer tests and fewer ways to misuse it.
- Put the seam where the variation is, not where the layering diagram looks tidy.
- Internal seams are allowed and useful: a deep module can be built from small parts that only its own tests see.

## Change structure only with evidence

Structure changes are expensive and easy to get wrong. Bring one when a measured problem justifies it: duplicated logic that keeps diverging, a module edited for unrelated reasons, or a test that cannot be written without reaching past the interface.

Work with `counterweight`: the lightest change that resolves the evidence. A refactor proposed for elegance, with no failing case behind it, is not yet earned.

## Where to put a lesson

- A rule the whole repository must follow → the project instructions file.
- A convention about how modules are shaped here → the same instructions file, one line.
- A one-off preference of the moment → nowhere.

## Gotchas

- A seam with one adapter is hypothetical. Do not introduce it until a second implementation is real.
- The deletion test is the fastest check on a wrapper. If removing it spreads no complexity, remove it.
- An interface is not just the type signature. The invariants and error modes are part of it, and they are what callers actually get wrong.
- A module that returns a large mutable object has not really hidden anything; the caller still knows the structure.
- Deep is about the interface, not the file size. A long function behind a clear interface can be deep; a short wrapper can be shallow.
- Do not design for a future requirement that is not in the problem. Name it and leave it out.
- Changing a public interface breaks callers; count them before deciding, and migrate them in the same change.
- Tests written against internals lock the internals in. Test through the same seam the caller uses.

## Report

State the module and its interface, what varies across the seam, the evidence that justifies a structural change, and what was deliberately left unchanged.
