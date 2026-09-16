# ResearchX (Gemini CLI extension)

ResearchX is a research assistant skill for the full scientific lifecycle: literature mining with verified
citations, gap and method discovery, experiment design, manuscript writing, journal-fit upgrades,
adversarial peer review, PRISMA systematic reviews, figures, and grant proposals.

## Load the skill

Read `skills/researchx/SKILL.md` first — it contains the operating contract, the task router and the
quality gates. Load files from `skills/researchx/references/` only when the matching module runs.

## Hard requirements

1. Never emit a reference that has not been verified with
   `python skills/researchx/scripts/verify_citations.py` (or is explicitly tagged `[UNVERIFIED]`).
2. Never invent numbers, datasets or results; if data is missing, ask for the table.
3. Say when retrieval failed and switch to labelled first-principles reasoning.

## Useful commands

```bash
python skills/researchx/scripts/search_literature.py --query "..." --from-year 2023 --format md
python skills/researchx/scripts/verify_citations.py draft.md --format md --out citation_audit.md
python skills/researchx/scripts/prisma_screen.py --input hits.json --include "..." --out-prefix review1
python skills/researchx/scripts/analyze_methods.py --input papers.json --format md
python skills/researchx/scripts/generate_visuals.py workflow --topic "..." 
```
