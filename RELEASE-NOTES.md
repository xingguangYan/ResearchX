# Release notes

User-facing notes for every ResearchX release: what changed, how to install or upgrade, and how to
verify the download. `CHANGELOG.md` is the developer-oriented history; this file is what goes into the
GitHub Release.

**Current release: [v4.0.0](#v400--2026-09-16) — the citation-integrity release.**

- [Installing a release](#installing-a-release)
- [Upgrading from v3](#upgrading-from-v3)
- [Verifying a download](#verifying-a-download)
- [Release process (maintainers)](#release-process-maintainers)

---

## v4.0.0 — 2026-09-16

**Headline: ResearchX now refuses to hand you a citation it could not verify.**

Every reference the assistant writes is checked against Crossref, OpenAlex, arXiv and the DOI handle
service and comes back with one of six verdicts — `VERIFIED`, `CORRECTED`, `PARTIAL`, `NOT_FOUND`,
`RETRACTED`, `ERROR`. Anything that cannot be confirmed is labelled `[UNVERIFIED]` with the reason
instead of being invented; retracted work is flagged; metadata drift (wrong year, wrong journal) is
corrected from the registry record. The audit is written to a file you can keep and re-run.

### Added

| Area | What you get |
|---|---|
| Citation integrity | `skills/researchx/scripts/verify_citations.py` — four-registry verification, retraction flags, correction suggestions, markdown + JSON reports, `--fail-on-unverified` for CI, disk cache, `--offline` |
| Literature retrieval | `scripts/search_literature.py` — OpenAlex/Crossref/arXiv search with year windows, multi-query merge, dedupe and forward/backward citation chaining |
| Systematic reviews | `scripts/prisma_screen.py` — dedupe, rule screening, human eligibility decisions, PRISMA 2020 counts, Mermaid flow diagram, screening ledger with a reason per record, AI-use disclosure |
| Method mining | `scripts/analyze_methods.py` — families, trends, recurring limitations, datasets, innovation dimensions, with a provenance warning in every report |
| New modules | M2b novelty check, M12 reproducibility packaging, M11 citation audit |
| Output templates | `assets/` — topic brief, experiment plan, manuscript skeleton, review report, PRISMA flow, grant proposal, artifact README, architecture diagrams |
| Platforms | One-command installs: Claude Code marketplace, Codex plugin, Cursor `/add-plugin`, Gemini CLI extension, Copilot CLI, Antigravity, and a zero-dependency MCP server (JSON-RPC over stdio, 6 tools + 5 prompts) |
| Quality gates | 51 offline tests against recorded registry fixtures, an Agent Skills spec validator, GitHub Actions on Python 3.9 and 3.12, a broken-link check, and version-consistency checks |
| Docs | `docs/INSTALL.md`, `docs/COMPARISON.md`, `docs/ROADMAP.md`, `docs/LAUNCH-KIT.md`, `docs/example-citation-audit.md` |

### Changed — breaking

- **The skill moved from `ResearchX/` to `skills/researchx/`** so the directory name matches the
  frontmatter `name`. Required by the Agent Skills specification, and what allows plugin marketplaces to
  load it. Update any copied path (see [Upgrading from v3](#upgrading-from-v3)).
- **`SKILL.md` rewritten** to the specification: imperative contract (three non-negotiable rules),
  a task router, module summaries M1–M12, and progressive disclosure — the body is 235 lines, deep
  material lives in `references/` and loads only when a module runs.
- **Non-standard frontmatter removed** (`trigger_terms`, `trigger_strategy`, `agents/openai.yaml`). Trigger
  keywords now live in `description`, which is the field every agent actually reads.
- **Scripts are standard-library only, non-interactive and documented**: every CLI accepts `--help`,
  emits JSON with `--format json`, and returns meaningful exit codes instead of tracebacks.

### Fixed

- References are no longer drawn from model memory; unverifiable ones are labelled.
- Hardcoded method lists removed from the methodology module (they were literature claims in disguise).
- A DOI that resolves but carries a wrong year is now reported as `CORRECTED` rather than accepted.
- Every output records its provenance (queries, registries, date) so a review can be re-run.

### Install

```bash
# Claude Code
/plugin marketplace add xingguangYan/ResearchX
/plugin install researchx@researchx

# Codex
codex plugin marketplace add xingguangYan/ResearchX

# Cursor
/add-plugin researchx

# Gemini CLI
gemini extensions install https://github.com/xingguangYan/ResearchX

# Manual / any agent
git clone https://github.com/xingguangYan/ResearchX
cp -r ResearchX/skills/researchx ~/.claude/skills/researchx
```

Or download an artifact from this release (`researchx-skill-v4.0.0.zip`) and drop the folder into your
skills directory — no clone, no build step.

### Verify

```bash
python skills/researchx/scripts/verify_citations.py --doi 10.1038/s41586-023-06221-2   # → VERIFIED
make check                                                                            # validator + 51 tests
python mcp-server/researchx_mcp_server.py --selftest
```

### Known limitations

- Verification depends on open registries: brand-new papers, books, theses and non-DOI proceedings
  legitimately return `NOT_FOUND`. The tool says so rather than guessing.
- No French/German/Spanish **registry** adapters yet; non-Latin title matching is heuristic (see the
  roadmap for PubMed, DBLP, Semantic Scholar and CNKI plans).
- Meta-analytic statistics (pooled effects, I²) are not automated — the protocol and counts are, the
  analysis is yours.
- `--offline` reports `ERROR` for uncached queries by design; treat that as "verification did not run".

---

## v3.0.0 — 2026-05 (historical)

- Multi-platform support: `CLAUDE.md`, `.cursorrules`, `.clinerules`, `.continuerules`, `.windsurfrules`,
  `PLATFORMS.md`, an MCP server and a GPT builder config.
- Modules for paper analysis, gap mining, method mining, experiment design, manuscript writing, SCI
  upgrade, peer review, visuals, literature review and grants.

## v2.0.0 — 2026-03 (historical)

- Module chaining (gap mining → method mining → manuscript), gap taxonomy, method landscape tables,
  experiment protocol, SCI upgrade scoring, peer-review simulation, visual prompts.

## v1.0.0 — 2026-01 (historical)

- Initial Codex skill: paper analysis, topic discovery, writing templates, search-query references.

---

## Installing a release

Download the artifact you need from the [Releases page](../../releases), then:

```bash
# skill (drop-in replacement for a cloned skills/researchx folder)
unzip researchx-skill-v4.0.0.zip -d /tmp/researchx
cp -r /tmp/researchx/researchx ~/.claude/skills/researchx     # or ~/.codex/skills/, .agents/skills/

# MCP server archive contains mcp-server/ plus the scripts it calls
tar -xzf researchx-mcp-v4.0.0.tar.gz
python researchx-mcp-4.0.0/mcp-server/researchx_mcp_server.py --selftest
```

No dependencies, no API keys, no account. Python 3.9+ is needed only for the tools.

## Upgrading from v3

1. If you copied the old folder, remove or replace it:
   `rm -rf ~/.claude/skills/ResearchX && cp -r skills/researchx ~/.claude/skills/researchx`
2. If you installed through a marketplace, re-run the install command (or
   `/plugin marketplace update researchx`).
3. Anything you wired to `ResearchX/scripts/*.py` or `ResearchX/references/*.md` must be repointed to
   `skills/researchx/scripts/*.py` and `skills/researchx/references/*.md`.
4. Re-run your drafts through the verifier once:
   `python skills/researchx/scripts/verify_citations.py yourdraft.md --format md --out citation_audit.md`

## Verifying a download

```bash
sha256sum -c SHA256SUMS           # or: shasum -a 256 -c SHA256SUMS
```

Every archive is built deterministically from the tagged commit (`scripts/package_skill.py`), so you can
rebuild it yourself and compare:

```bash
git checkout v4.0.0
python scripts/package_skill.py --out /tmp/rebuild
sha256sum /tmp/rebuild/*.zip /tmp/rebuild/*.tar.gz
```

## Release process (maintainers)

```bash
# 1. version everywhere (SKILL.md is authoritative) and confirm consistency
python scripts/bump_version.py --set 4.1.0
python scripts/bump_version.py --check

# 2. write the human-facing notes (CHANGELOG.md entry + a section here)
$EDITOR CHANGELOG.md RELEASE-NOTES.md

# 3. validate, then commit and tag (the tag must match the version)
make check
git commit -am "chore(release): v4.1.0"
git tag -a v4.1.0 -m "ResearchX v4.1.0"
git push origin main --follow-tags

# 4. or let CI do 4: pushing a v* tag runs .github/workflows/release.yml, which
#    validates, tests, checks the tag against the version, builds the artifacts,
#    extracts this release's section and publishes the GitHub Release
```

Manual path if CI is unavailable:

```bash
python scripts/package_skill.py --out dist
python scripts/extract_release_notes.py --current --out release_body.md
gh release create v4.1.0 --notes-file release_body.md dist/*
```
