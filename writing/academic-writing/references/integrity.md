# Integrity

These rules hold in every mode. A fluent draft is not evidence.

## Never invent

- Data, results, measurements, tables, error bars, ablations, or the conditions they were taken under.
- Citations, authors, years, DOIs, page numbers, quotations, or the claim a paper supports.
- Methods that were not carried out, tool versions that were not used, or datasets not used.
- Approvals, funding, conflicts of interest, author roles, acknowledgements, or availability statements.

When a fact is missing, leave a visible placeholder and list it for the user. Reproduce numbers from the user's files; if you compute a derived number, show the formula and the inputs.

## Citations

Every citation is verified before it enters the bibliography:

1. Find the paper in an indexed source (publisher page, DOI resolver, Crossref, DBLP, arXiv, or the user's library; `paper-search` finds papers).
2. Take the BibTeX from that source; do not write it from memory.
3. Confirm the paper says what you cite it for (read the relevant part).
4. Record unresolved items as `[CITATION NEEDED]` and report them.

Search snippets and another paper's bibliography help discovery but are not verification. Run `scripts/check_paper.py` to catch keys that do not resolve; it does not prove that a reference exists.

## Generated text and figures

- A language model or image tool cannot be an author or take responsibility. The human authors answer for every sentence, number, and figure.
- Follow the venue's current policy on disclosure of generated text, figures, images, and code, and whether it asks for a statement in acknowledgements or methods. Fetch the policy; do not assume. Record the venue's rule and the date in the report.
- Do not upload unpublished manuscripts, reviews, or confidential data to an external service unless the policy and the data owners allow it. Reviews of other people's manuscripts are confidential; do not feed them to a tool unless the venue permits.
- Figures that look like measurements (plots, die photos, waveforms) must come from real data. A generated schematic is allowed only if the venue allows it and the disclosure rule is met; never generate a data plot from imagined numbers.

## Reuse of own work

- Text overlap with your own earlier papers, theses, or preprints is still overlap. Cite it, quote it, or rewrite it, and follow the venue's similarity policy.
- A journal extension needs disclosed overlap and new content. Reusing figures needs permission or a licence from the copyright holder (including the publisher of your own paper).
- Do not submit the same work to two venues at once. Do not split one result across papers to inflate counts.
- Third-party figures, tables, and text need permission or a licence and credit.

## Fair reporting

Report baselines fairly, include results that do not favour you, and do not cherry-pick seeds, sequences, or workloads. State when a result is from simulation. Describe limitations. Do not remove an outlier without saying so.

## Confidential and company material

For industry authors: check employer review and release rules, patent filing, and customer or vendor NDAs before disclosing designs, process data, or code. Foundry PDK data and tool outputs are often under NDA; check what can be published. Never paste private rules into the skill's tracked `references/house-style.md`; keep them in the paper repository's `.house-style.md`.
