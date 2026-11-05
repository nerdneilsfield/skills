# Venue conventions

Rules change each year and by track. Page limits, anonymity, template version, and policy come from the current call or author instructions, fetched now and linked in the report. Never from memory, and never from last year's call. If you cannot fetch it, say so and mark every venue-specific number unverified.

## Procedure

1. Get the venue, track, and year. Find the call for papers and author instructions on the official site. Record the URL and date read.
2. Extract: page limit and what it excludes (references, appendix, acknowledgements), template and class options, blind or not, abstract and keyword limits, supplementary material rules, generated-content disclosure, prior-publication and overlap rules, artifact or checklist requirements, camera-ready differences.
3. Use the official template for that year. Do not change fonts, margins, or spacing to fit.
4. After compiling, check the page count by the call's definition and run `scripts/check_paper.py`.

## Families, in general terms

These describe habits, not rules.

| Family | Habits to confirm against the call |
|---|---|
| IEEE conferences and journals (TCAS, TCAD, TVLSI, JSSC, ICRA, IROS) | IEEEtran; two columns; numbered references; IEEE Author Center rules; journals often have a longer page count and allow overlength fees; keywords and index terms |
| IEEE RA-L | Straight-to-journal letter with an option to present at ICRA or IROS; the ICRA and IROS option has its own deadlines and video rules |
| ACM (DAC-adjacent, ASPLOS, ISCA, MICRO, FPGA, SIGGRAPH) | acmart with venue-specific options (`sigconf`, `anonymous`, `review`); rights block, CCS concepts, ACM reference format; per-venue artifact badges |
| CVF (CVPR, ICCV, WACV) | Own style files; anonymous review; supplementary material and rebuttal rules; ethics and reproducibility checklists |
| ISSCC | Short papers with a strong measured-silicon expectation and comparison table; double-blind review; strict length |
| DAC, ICCAD, DATE | Design-automation conferences; DAC research track is double-blind with abstract then manuscript stages; do not name authors, self-cite in third person |
| FCCM, FPGA, FPL | FPGA and reconfigurable computing; typically double-blind, artifact encouraged, resource tables expected |
| Machine-learning venues (NeurIPS, ICML, ICLR) | Checklist, reproducibility and broader-impact statements; page limit counts main text only |

## Conference versus journal

Conferences reward a sharp central idea in a tight page budget, with deadlines and rebuttals. Journals allow a complete treatment, more experiments, proofs, and a longer related-work, and review in rounds. A journal extension needs new content (see `paper-types.md`).

## Double-blind

- Remove names, affiliations, funding with identifying text, and acknowledgements.
- Self-citation in third person ("Chen et al. [3] show"); do not write "anonymous" for references to own work unless the call tells you to; do not cite own unpublished work as if from others.
- Scrub PDF metadata, file names, and figure text. Strip identifying paths from screenshots and logs.
- Links to code must be anonymous, if allowed at all. Do not contact the committee.
- Preprints: follow the call's policy on arXiv; some venues forbid advertising during review.
- Hardware: chip photos with logos, lab names, and tool license strings can identify authors.

## Page limits

Count the way the call counts. Typical choices: main text only, references excluded; references counted; appendix allowed or not; extra pages for a fee at camera-ready. Do not shrink figures to illegible size or use negative `\vspace` tricks to squeeze under the limit.

## Snapshot read on 2026-11-05 (verify at the source)

Search-engine results, not the primary pages. They show why a check is needed:

- IEEE: secondary sources cite the IEEE editorial rules as requiring disclosure of AI-generated text, figures, images, and code in the acknowledgments, with light grammar editing generally exempt. Confirm in the IEEE Author Center.
- ACM: AI cannot be an author; disclosure expectations changed recently (a conference page quotes the update as dropping disclosure for writing assistance while requiring methods disclosure when AI is part of the research). Confirm on acm.org.
- ICRA: limits differ by year in results (6 pages plus references for 2025; 8 for 2026 and 2027, per search results) and RA-L has its own limit. Read the year's page.
- DAC: research manuscript stage double-blind; names only allowed in references if needed. ISSCC: double-blind, length strictly enforced, measured results expected.

Do not copy these into a submission checklist. Fetch the call.
