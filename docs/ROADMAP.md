# Roadmap

Direction: make the verification layer broader, the review pipeline more rigorous, and the skill usable in
more fields, languages and agents. Items marked ⭐ are the ones most likely to help users today — votes via
issues are welcome.

## v4.1 — retrieval depth
- ⭐ **PubMed / Europe PMC adapter** for citation verification and search (biomedical coverage).
- ⭐ **DBLP + ACL Anthology adapters** for computer science conference papers (poor Crossref coverage).
- **Semantic Scholar + DataCite** as extra verification sources (datasets, software, preprints).
- **RIS / EndNote XML import** for `prisma_screen.py` (exchange with reference managers).
- Abstract-aware screening: use abstracts (already retrieved) for keyword rules, not titles alone.

## v4.2 — review rigour
- Risk-of-bias templates as data: RoB 2, ROBINS-I, QUADAS-2, NOS, JBI.
- Meta-analysis helpers: effect-size extraction table, forest-plot data emission, heterogeneity reporting.
- Screening workbench: `--decisions` round-trip with a reviewable HTML/Markdown list for human decisions.
- Search recall audit: PRESS-style peer review of the search strategy.

## v4.3 — fields and languages
- Clinical reporting checklists (CONSORT, STROBE, PRISMA-P) as module templates.
- Materials science, chemistry and social-science module variants.
- Chinese workflows: CNKI/万方 query patterns, GB/T 7714 output, NSFC reviewer expectations.
- Spanish/Portuguese/Arabic/Japanese query pattern packs; non-Latin title matching improvements.

## v4.4 — agent integration
- Subagent orchestration recipes (scout → screener → extractor → critic → writer) for platforms that
  support them.
- Optional hooks: pre-submission gate that blocks emitting `[UNVERIFIED]` references without a note.
- Evaluation harness in CI: trigger accuracy, verdict accuracy vs a labelled fixture set, hallucination
  regression tests.
- Editor integrations (VS Code, Zotero plugin) that shell out to the same scripts.

## Non-goals
- Generating images presented as data.
- Writing references it cannot verify, ever.
- Becoming a paid SaaS with a proprietary corpus.

## Contributing to the roadmap
Open an issue describing the research workflow you are missing, the field/language you work in, and the
registries you rely on. Small, testable pull requests move fastest — see `CONTRIBUTING.md`.
