# Chinese and English, and letters

## Language choice

- Write the paper in the language of the venue. Write the first draft in the language in which the author thinks most precisely, then translate with care; a machine translation pass without checking is a risk to terminology and claims.
- Keep one term per concept in both languages. Build a small glossary (Chinese term, English term, abbreviation) before drafting and use it throughout.
- Chinese thesis or journal articles follow the institution's or journal's rules (for example GB/T 7714 references, university templates); read them from the template and the school's current guide. This skill gives the paper-writing logic; the template governs layout.
- Chinese academic prose: plain, specific sentences; avoid padded openings, stacked nominalisations, and slogans. Numbers and units follow the venue's convention; keep English terms where the field uses them and give the Chinese term on first use.
- English academic prose: active voice for contributions, past tense for what was done, present for what holds. Avoid inflated adjectives and vague "significantly" without a test. Run `deai` on the finished prose if it reads templated; do not let a de-AI pass change numbers, claims, citations, or math.

## Cover letter

Short, factual, one page. Content: title and article type; the problem and the contribution in two or three sentences; why this venue; confirmation that the work is original and not under review elsewhere; disclosure of overlapping prior work (conference version, preprint, thesis) with a pointer to how the new paper differs; conflicts of interest and suggested or excluded reviewers if the venue asks; data and code availability; generated-content disclosure if required. No superlatives. Never state a fact that is not true.

## Revision letter or response to reviewers

Structure:

1. A short opening: thanks in one sentence, summary of the main changes.
2. For each reviewer, each comment, quoted or numbered, followed by the response and the exact change (section, page, line, or the new text).
3. A list of other changes and a diff or highlighted PDF when requested.

Rules:

- Answer every comment. Do not skip those you disagree with.
- Be specific: what was changed, where, with the result. Add experiments to address the concern when they are needed and available; do not promise results you do not have.
- When disagreeing, give evidence and the reasoning in a calm sentence. Concede a point you cannot refute and say what you changed.
- Do not reveal identity in a blind process. Do not argue about the reviewer's competence.
- When the reviewer misreads, treat that as a clarity problem and fix the text.
- Tone: plain and professional. No defensive pre-emptions ("as the reviewer will certainly agree") or flattery. Use `deai` and its defensive-writing reference if the draft turns apologetic or combative.
- Word-limited rebuttals (conference): put the strongest new evidence first; one short paragraph per shared concern; do not exceed the stated format; check if new results are allowed.

Template for each comment:

```
R1.3  [reviewer's comment, quoted or condensed without changing meaning]
Response: [one to three sentences: agree, partly agree, or disagree and why.]
Change: [Section V-B, paragraph 2; Table IV now includes baseline C; added sentence "..."]
```

## Journal-extension letter

State the conference paper, list the new technical content, new experiments, and sections that overlap, and give the percentage or the list if the journal asks for it. Add the similarity-report summary if requested.
