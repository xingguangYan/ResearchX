# Citation Verification Protocol

Why this exists: language models produce references that *look* right. Studies of AI-assisted
manuscripts keep finding fabricated, chimeric (real DOI + wrong metadata) and retracted citations in
submitted work. Reviewers and editors increasingly check. A single hallucinated reference can trigger a
desk rejection or a misconduct inquiry — and it is trivially avoidable.

**Rule**: a reference is trustworthy when a registry confirms it, not when it sounds plausible.

---

## 1. The four-registry cascade

Run `scripts/verify_citations.py` — it queries, in order, and stops at the first confident match:

| Registry | Strength | Weakness |
|---|---|---|
| **Crossref** (`api.crossref.org`) | DOI metadata of record, retraction links, 150M+ works | weak on books/theses and some non-Western venues |
| **OpenAlex** (`api.openalex.org`) | 250M+ works, preprints, retraction flag, open-access status, citation counts | metadata quality varies, some duplicates |
| **arXiv** (`export.arxiv.org`) | preprints with exact titles | preprints only — not peer review |
| **doi.org handle service** | proves the DOI is registered *somewhere* | no metadata; a resolving DOI can still point to the wrong paper |

```bash
python skills/researchx/scripts/verify_citations.py draft.md --format md --out citation_audit.md
python skills/researchx/scripts/verify_citations.py refs.bib --format json --fail-on-unverified
python skills/researchx/scripts/verify_citations.py --doi 10.1038/s41586-023-06221-2
```

Always pass `--mailto you@institution.edu` (or set `RESEARCHX_MAILTO`) and `--sleep 0.5` for long lists:
polite-pool access is faster and avoids being throttled. Results are cached in `.researchx-cache/`, so
re-running is free and works with `--offline`.

---

## 2. Reading the verdicts

| Verdict | What it means | Action |
|---|---|---|
| `VERIFIED` | registry record matches title (≥0.80 similarity, usually ≫0.9) and authors | cite it |
| `CORRECTED` | the work exists; year/journal/author/DOI in the draft differs | replace the metadata with the registry version, then re-check the claim's tense ("in 2019, X showed…" becomes "in 2021, X showed…") |
| `PARTIAL` | plausible grey-literature or DOI-only match | open it and confirm by hand; grey literature (reports, standards, theses) rarely indexes cleanly |
| `NOT_FOUND` | no registry match | **not** proof of fabrication. Treat as unverified: check by hand, or drop the reference *and* the claim resting on it |
| `RETRACTED` | registry carries a retraction/withdrawal notice | remove, or keep only with an explicit note and the notice DOI |
| `ERROR` | network/offline/throttled | retry once with `--mailto` and `--sleep`; if it still fails, say the check did not run |

`NOT_FOUND` false positives are common for: very recent papers (weeks old), conference proceedings without
DOIs, books and chapters, non-English regional journals, standards, government reports, and theses. Before
declaring a reference dead, try: title-only search, author-year search, the publisher site, and the
authors' own pages. Then decide.

---

## 3. Fabrication patterns to recognise

1. **Phantom paper** — plausible title, plausible journal, no record exists.
2. **Chimera** — a real DOI attached to invented metadata (the dangerous kind: the DOI resolves).
3. **Author swap** — real paper, wrong author list.
4. **Temporal drift** — real paper, wrong year (commonly cited as more recent than it is).
5. **Venue inflation** — preprint described as a journal article, workshop paper as a conference paper.
6. **Numbers with no source** — "94.5% accuracy [12]" where [12] reports no such number.
7. **Retracted citing** — citing a withdrawn result as live evidence.
8. **Citation-context mismatch** — the source exists but does not support the sentence.

Checks 6 and 8 need the abstract or the paper itself, not just a registry: `search_literature.py` returns
abstracts for OpenAlex/arXiv records, which is enough to catch most mismatches.

---

## 4. When a reference cannot be verified

Options, in order of preference:

1. Replace it with a verified paper that supports the same claim.
2. Narrow the claim so it no longer needs that reference.
3. Keep it visibly marked: `[UNVERIFIED: author-provided, not in Crossref/OpenAlex as of YYYY-MM-DD]` — and
   tell the user in the handoff, not only in a footnote.
4. Drop it.

Never: silently delete the reference while keeping the claim, or "fix" a reference by inventing a DOI.

---

## 5. Pre-submission citation audit

Run this before any submission, and again after revisions:

1. `verify_citations.py draft.md --format md --out citation_audit.md --mailto you@inst.edu --sleep 0.5`
2. Fix every `CORRECTED` (registry metadata wins).
3. Investigate every `NOT_FOUND` and `PARTIAL` — the audit report lists them in one place.
4. Remove `RETRACTED` sources or mark them explicitly.
5. Check in-text ↔ reference-list symmetry (M11 in `modules.md`).
6. Confirm each in-text citation supports its sentence (spot-check the 10 most load-bearing claims).
7. Keep the audit report; some journals ask how references were checked.

---

## 6. Disclosing AI assistance

Journals and funders increasingly require an explicit statement; policies differ and change — check the
target venue's current author guidelines before writing the statement. Where AI use must be disclosed, a
working pattern is:

> Generative AI tools were used for literature retrieval support and language editing. All retrieved
> references were verified against Crossref/OpenAlex and manually checked; screening decisions and the
> final manuscript content were reviewed and approved by the authors, who take responsibility for the
> work. No AI tool is listed as an author.

For evidence syntheses, follow the PRISMA-trAIce style reporting of *which stages* were automated
(see `references/systematic-review-prisma.md`). Never let an AI tool be an author: authorship requires
accountability that a tool cannot carry (ICMJE; most publisher policies align).

---

## 7. Limitations to state honestly

- Registries lag publication by days to months; a brand-new paper may genuinely be absent.
- Coverage is biased toward English-language, DOI-issuing publishers.
- Metadata errors exist in registries too — a match is strong evidence, not absolute truth.
- Author matching here uses surname containment, which is a heuristic; common surnames need the paper itself.
- `verify_citations.py` never claims a reference is fabricated. It reports what the registries know.
