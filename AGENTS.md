# ResearchX — Development & Contribution Guide

This repository contains the **ResearchX** Codex skill — an AI research operating system.

## Project Structure

- `ResearchX/SKILL.md` — Main skill instructions (Codex loads this when triggered)
- `ResearchX/scripts/` — Python helper scripts for literature analysis and visual generation
- `ResearchX/references/` — Reference documents for research design, writing, and search
- `ResearchX/agents/openai.yaml` — UI metadata for Codex skill chip

## Key Design Decisions

ResearchX is **literature-driven**, not method-hardcoded. This means:
- Methods are NEVER predefined — always discovered via `web_search` of latest 3 years literature
- The `SKILL.md` guides Codex to search, analyze, and synthesize — not to assume
- All modules are domain-agnostic (works for remote sensing, medicine, ecology, etc.)
- Innovation scoring is comparative (against real literature, not absolute)

## Development Workflow

1. Edit `ResearchX/SKILL.md` to modify core instructions
2. Add/update Python scripts in `ResearchX/scripts/`
3. Update reference docs in `ResearchX/references/`
4. Validate: run scripts to ensure they work
5. For installation: copy to `$env:USERPROFILE\.codex\skills\ResearchX`

## GitHub Deployment

```powershell
git init
git add .
git commit -m "Initial ResearchX skill release"
git remote add origin https://github.com/YOUR_USERNAME/ResearchX.git
git branch -M main
git push -u origin main
```
