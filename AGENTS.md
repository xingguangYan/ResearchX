# ResearchX — Research Skill for Codex

## Repository Structure

```
ResearchX/                    # Codex skill (copy to $CODEX_HOME/skills/)
├── SKILL.md                  # Core instructions — Codex entry point
├── agents/
│   └── openai.yaml           # UI metadata
├── scripts/
│   ├── analyze_methods.py    # Literature method mining & trend analysis
│   └── generate_visuals.py   # Mermaid diagrams, abstract prompts, posters
├── references/
│   ├── 01_research_design.md # FINER/PICO frameworks
│   ├── 02_writing_templates.md # SCI writing style guide
│   └── 03_search_queries.md  # web_search query templates
└── assets/
    └── architecture_diagrams.md # Mermaid architecture diagrams
README.md                     # This file
AGENTS.md                     # This file
.gitignore
```

## Key Design Principles

- **Literature-driven**: Methods come from `web_search` of latest 3 years, never hardcoded
- **Module chaining**: Auto-detect user intent and chain modules together (e.g., gap mining → method mining → manuscript)
- **Domain-agnostic**: Works for all scientific fields
- **File-first**: Every module saves structured markdown output files
- **Quality gates**: Self-evaluation before presenting results

## Development

1. Edit `ResearchX/SKILL.md` for core behavior
2. Edit `ResearchX/scripts/*.py` for analysis/visualization logic
3. Test scripts: `python ResearchX/scripts/analyze_methods.py --input test.json --output test_report.json`
4. Update `README.md` and `AGENTS.md` as needed
5. Deploy: Copy to `$env:USERPROFILE\.codex\skills\ResearchX`

## GitHub Deployment

```powershell
git add .
git commit -m "[description of changes]"
git push
```
