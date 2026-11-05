# Modes

Choose one from the request. Name it at the start and say what you will produce.

## write

1. Run intake (`intake.md`).
2. Read `house-style.md`; if it has content, it overrides defaults here.
3. Fill the claim-evidence ledger (`sections.md`). Show it to the user if the claim and the evidence do not match.
4. Outline each section with one sentence per paragraph. Confirm the outline if the user is available.
5. Draft in the order: method and evaluation first, then introduction, related work, abstract, conclusion, title. Insert placeholders for anything missing.
6. Compile (if a template exists), run `scripts/check_paper.py`, and read for the final checks in the final check in SKILL.md.

## revise

The user has a draft. Preserve their claims, notation, and results. Improve structure, clarity, and fit to venue.

- Work by the highest-impact issue first: claim and evidence, then structure, then paragraphs, then sentences.
- Show changes as tracked edits or a diff when possible. Do not touch `\cite`, `\ref`, `\label`, equations, or numbers without saying so.
- If a result looks wrong or unsupported, report it; do not smooth it over.

## audit

Review as a reviewer would, and report; do not rewrite unless asked.

- Claim and evidence, novelty against the closest work, fairness of baselines and comparison table, missing conditions (see the two evaluation references), clarity, reproducibility, integrity, venue compliance.
- Run `scripts/check_paper.py` and compile; separate script findings from your judgement.
- Rank findings Critical (invalidates a claim or violates a rule), Major (a reviewer would likely reject for it), Minor. Give a location and a fix direction for each. Do not pad the list.
- Do not give a score as if it were a verdict; say what you could not check.

## respond

The user has reviews. Do not use unpublished or confidential reviews outside what the venue allows.

1. Sort comments: misunderstanding, missing experiment, missing explanation, disagreement, minor.
2. Decide the response per comment with the user: fix, explain, run, or decline with reasons. List the experiments that are needed and whether they exist.
3. Draft the response and the paper changes together so that each reply points to a real change (`bilingual-and-letters.md`).
4. Check that every promised change is in the revised paper, and that new numbers match the new tables.
