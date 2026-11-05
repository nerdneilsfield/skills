---
name: paper-search
description: "Use when the user asks to find papers on a question, gather related work, check whether something has been published, or track citations: expand the query, search several sources, follow references and citations, screen against stated criteria, and log the search so it can be rerun. Not for reading one paper closely (qi-read-paper) or writing the survey from the found sources (research-report)."
license: MIT
compatibility: Uses curl and jq for the source APIs, pdftotext for local PDFs. Semantic Scholar needs an API key above a low request rate; Crossref and arXiv do not.
metadata:
  author: DengQi
---

# Find the papers that answer a question

The output is a short list of papers plus the search log that produced it. A list without its queries cannot be trusted or repeated.

## 1. Turn the question into queries

Write the question in one sentence, then list its concepts. For each concept collect synonyms, the older and newer name, and the abbreviation, because the field renames things. Test each query against two or three papers you already know are relevant: if the query misses them, it is wrong, not the papers.

Search from the specific to the general. Start with the exact phrasing, then the concept without the method name, then the problem the method addresses.

## 2. Search several sources

If the user keeps papers in a local folder, search it through `paper-library`, which navigates by index and never reads a whole PDF. Then check the user's private library when the environment has it (an MCP tool that searches a personal paper collection). It is smaller and already filtered to their field, so a hit there is the cheapest good result. Search it with a semantic query and, if it exposes one, a keyword query; then use its outline and content-window calls to read the actual text of a hit. Do not conclude from a stored abstract. If the environment has no such tool, skip this step, say so in the log, and go straight to the public sources.

Then search at least two public sources, and record the exact query and the date for each.

Crossref, structured metadata, no key:

```sh
curl -sS -G 'https://api.crossref.org/works' \
  --data-urlencode 'query.bibliographic=graph SLAM loop closure' \
  --data 'rows=20' \
  --data-urlencode 'select=title,DOI,issued,container-title,author' \
| jq -r '.message.items[] | "\(.title[0]) | \(.issued["date-parts"][0][0]) | \(.DOI)"'
```

arXiv, preprints and the latest work:

```sh
curl -sS -G 'https://export.arxiv.org/api/query' \
  --data-urlencode 'search_query=all:"graph SLAM"' \
  --data 'max_results=20' -o search.xml
```

Pass every query through `--data-urlencode`; a raw `+` or space in the URL is silently mangled. Parse the Atom feed with `python3` and `xml.etree.ElementTree`, or read it with `rg -o '<title>.*</title>'`.

Add the venue proceedings, the authors' pages, and `gh search repos` or `gh api` when the work has code. Use the agent's own web search for coverage of blogs, theses, and venue sites; the APIs above do not index those.

Merge the private and public results, deduplicate by DOI and then by title and year, and mark each kept paper with the source that produced it. The retrieval step here is what `paper-compare`, `paper-to-code`, and the reading step of `qi-read-paper` reuse; only this skill owns the query log.

## 3. Follow references and citations

From the best two or three hits, read their reference lists and look up who cites them. Backward (references) finds the foundations; forward (citations) finds the corrections. Crossref reports citation counts as `is-referenced-by-count`; use a count to order reading, never to decide inclusion.

## 4. Screen with stated criteria

Decide the inclusion and exclusion criteria before screening, and write them down. Screen title, then abstract, then full text. Record a reason for every exclusion. Deduplicate by DOI, then by title and year; the same work appears under a preprint and a journal DOI.

Mark a paper you only saw as a snippet. A snippet is not a source, and a title is not evidence for a claim.

## 5. Stop deliberately

Stop when new queries stop returning papers not already in the list, and when the last round of citation chasing adds nothing. Report the number of rounds and the last query. "I stopped" is not a stopping rule; "two rounds added no new eligible paper" is.

## Search log

Keep one file, and append to it as you go:

```markdown
# Search log: <question>

Date: <YYYY-MM-DD>. Databases: <list>.

## Criteria
Include: ...
Exclude: ...

## Queries
- 2026-11-05 | Crossref | `graph SLAM loop closure` | 20 hits | 3 kept
- 2026-11-05 | arXiv | `all:"graph SLAM"` | 20 hits | 5 kept

## Included
- <title> | <year> | <DOI or arXiv id> | <why included>

## Excluded
- <title> | <reason>

## Gaps
- <what the search could not cover>
```

## Gotchas

- A search that cannot reproduce its own queries is not a search. Record the query, the source, and the date.
- arXiv and Crossref want `--data-urlencode`; a hand-built URL with `+` returns wrong or empty results without an error.
- Semantic Scholar returns HTTP 429 without a key. Fall back to Crossref and arXiv, and say which source was unavailable.
- Deduplicate by DOI first. The same work has a preprint id, a journal DOI, and sometimes two titles.
- A citation count is a popularity signal, not evidence of quality or correctness. It orders reading.
- Zero results from one source is not "no such paper". Say which sources were searched, including whether the private library was available.
- An abstract stored in a private library is still an abstract. Open the outline and the relevant content window before treating a claim as read.
- A title that matches the query is not a paper that answers the question. Read the abstract before including it.
- Do not report a paper you have not opened as if you had read it; mark it snippet-only.

## Report

State the question, the sources and queries used, how many papers were screened and included, the inclusion criteria, and what the search could not cover.
