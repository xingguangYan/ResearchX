# ResearchX (project rules)

Use the ResearchX skill for any research task. Read `skills/researchx/SKILL.md` first — it holds the
operating contract, the task router and the quality gates. Load a file from `skills/researchx/references/`
only when its module runs.

Hard requirements:

1. No reference without verification — run `python skills/researchx/scripts/verify_citations.py`, or label
   the reference `[UNVERIFIED]` with the reason. Never invent a DOI, title, author or year.
2. No invented numbers — every figure traces to a retrieved source or the user's own results.
3. Say when retrieval failed, and switch to labelled first-principles reasoning.

Common commands:

```bash
python skills/researchx/scripts/search_literature.py --query "..." --from-year 2023 --format md
python skills/researchx/scripts/verify_citations.py draft.md --format md --out citation_audit.md
python skills/researchx/scripts/prisma_screen.py --input hits.json --include "..." --out-prefix review1
```

Deliverables are files (`analysis_*.md`, `topics_*.md`, `methods_*.md`, `manuscript_*.md`,
`citation_audit_*.md`, …), not chat-only answers.
