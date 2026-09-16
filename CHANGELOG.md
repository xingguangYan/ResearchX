# Changelog

All notable changes to this project. Versioning: semantic, per the skill and its plugin manifests.

## [4.0.0] — 2026-09-16

The citation-integrity release: layout, guarantees, tooling and packaging all change.

### Added
- **Citation integrity layer (M11)** — `scripts/verify_citations.py` verifies every reference against
  Crossref, OpenAlex, arXiv and the DOI handle service; returns `VERIFIED / CORRECTED / PARTIAL /
  NOT_FOUND / RETRACTED / ERROR`, flags retractions, and never claims a reference is fabricated.
- **Structured literature search** — `scripts/search_literature.py` with year windows, multi-query merge,
  dedupe, and forward/backward citation chaining.
- **Systematic review pipeline (M9)** — `scripts/prisma_screen.py` produces PRISMA 2020 counts, a Mermaid
  flow diagram, a screening ledger with a reason per record, and PRISMA-trAIce style AI-use disclosure.
- **Novelty check (M2b)**, **reproducibility packaging (M12)**, `references/integrity-and-ethics.md`,
  `references/gotchas.md`, `references/systematic-review-prisma.md`, `references/journal-playbook.md`.
- **Output templates** in `assets/` (topic brief, experiment plan, manuscript skeleton, review report,
  PRISMA flow, grant proposal, artifact README).
- **Tests + CI** — `tests/` (offline pytest suite against recorded registry fixtures) and
  `tests/validate_skill.py` (Agent Skills spec validator); GitHub Actions workflow runs both.
- **One-command installs** — plugin manifests for Claude Code (`.claude-plugin/`), Codex
  (`.codex-plugin/`), Cursor (`.cursor-plugin/`) and Gemini CLI (`gemini-extension.json`).
- `LICENSE` (MIT), `CITATION.cff`, `CONTRIBUTING.md`, `CHANGELOG.md`, `SECURITY.md`,
  `CODE_OF_CONDUCT.md`, `Makefile`, icon assets.

### Changed
- **Layout**: the skill moved from `ResearchX/` to `skills/researchx/` so the directory name matches the
  skill `name`, and so plugin marketplaces can load it directly. Update your install path.
- **SKILL.md** rewritten to the Agent Skills spec (portable frontmatter, imperative instructions, <500
  lines) with reference material moved into `references/` for progressive disclosure.
- Frontmatter no longer uses non-standard `trigger_terms` / `trigger_strategy`; trigger keywords now live
  in `description` and `metadata`, which is what agents actually read.
- Scripts are now stdlib-only, non-interactive, `--help`-documented, JSON-capable, with exit codes.
- The MCP server gains `verify_citations`, `search_literature`, `prisma_screen` and `citation_audit` tools.

### Fixed
- Emitted references are no longer taken from model memory; unverifiable ones are labelled `[UNVERIFIED]`.
- Removed hardcoded method lists from the methodology module (they were literature claims in disguise).
- Consistent file naming and a stated reproducibility header (queries, registries, date) for every output.

## [3.0.0] — earlier
- Multi-platform support: `CLAUDE.md`, `.cursorrules`, `.clinerules`, `.continuerules`, `.windsurfrules`,
  MCP server, GPT builder config, `PLATFORMS.md`.

## [2.0.0]
- Module chaining, gap taxonomy, method mining, experiment design, SCI upgrade, peer review, visuals.

## [1.0.0]
- Initial Codex skill: paper analysis, topic discovery, writing templates.
