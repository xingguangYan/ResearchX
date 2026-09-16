<div align="center">

<img src="assets/icon.svg" width="88" alt="ResearchX logo">

# ResearchX

**The research skill that refuses to invent a citation.**

Gap mining → methods → experiments → manuscript → peer review → submission — every reference checked
against Crossref, OpenAlex and arXiv before it reaches you.

[![release](https://img.shields.io/github/v/release/xingguangYan/ResearchX?style=flat-square&color=2563EB&label=release)](https://github.com/xingguangYan/ResearchX/releases)
[![validate](https://github.com/xingguangYan/ResearchX/actions/workflows/validate.yml/badge.svg)](https://github.com/xingguangYan/ResearchX/actions/workflows/validate.yml)
[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-spec--compliant-2563EB?style=flat-square)](https://agentskills.io/specification)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9%2B%20stdlib%20only-3776AB?style=flat-square&logo=python&logoColor=white)](skills/researchx/scripts)
[![PRs welcome](https://img.shields.io/badge/PRs-welcome-brightgreen?style=flat-square)](CONTRIBUTING.md)

**Install** · [Claude Code](#one-command-install) · [Codex](#other-agents--one-liners) · [Cursor](#other-agents--one-liners) · [Gemini CLI](#other-agents--one-liners) · [MCP](#mcp-clients) · [manual](#manual-install)

<img src="docs/assets/banner.png" alt="ResearchX — literature graph under verification" width="100%">

</div>

---

## Why this exists

Every AI research assistant can write a plausible paragraph. Almost none can **prove** the paragraph.
Ask a general model for references on a niche topic and you get convincing-looking DOIs that resolve to
nothing — the failure mode has a name (hallucinated/chimeric citation) and it now gets papers desk-rejected.

ResearchX makes that structurally impossible:

```
You:  "Find me a research gap in crop mapping and list the methods I should use."

ResearchX:
  1. searches OpenAlex / Crossref / arXiv for real records (not memory)
  2. builds the gap taxonomy and method landscape from those records
  3. verifies every reference it is about to write:
        python skills/researchx/scripts/verify_citations.py draft.md --format md
        → 34 references | 31 verified | 2 corrected | 1 unverified | 0 retracted
  4. labels the one it could not verify as [UNVERIFIED] instead of pretending
  5. ships the audit file so you can check it yourself
```

The rule is not "try not to hallucinate". The rule is **`NOT_FOUND` gets labelled, never invented.**

---

## One-command install

### Claude Code (plugin marketplace)

```bash
/plugin marketplace add xingguangYan/ResearchX
/plugin install researchx@researchx
```

### Other agents — one-liners

| Agent | Install |
|---|---|
| **Codex** (app or CLI) | `/plugins` → search **researchx** (plugin manifest: `.codex-plugin/plugin.json`), or `codex plugin marketplace add xingguangYan/ResearchX` |
| **Cursor** | `/add-plugin researchx` |
| **Gemini CLI** | `gemini extensions install https://github.com/xingguangYan/ResearchX` |
| **GitHub Copilot CLI** | `copilot plugin marketplace add xingguangYan/ResearchX` |
| **Antigravity** | `agy plugin install https://github.com/xingguangYan/ResearchX` |
| **Claude / any agent (manual)** | copy `skills/researchx/` into your skills directory (see below) |

### Download a release (no clone)

Every tag publishes deterministic archives with checksums:

| Artifact | Use |
|---|---|
| `researchx-skill-vX.Y.Z.zip` | unzip → copy the `researchx/` folder into your skills directory |
| `researchx-skill-vX.Y.Z.tar.gz` | same, tar flavour |
| `researchx-mcp-vX.Y.Z.tar.gz` | MCP server + the scripts it calls |
| `SHA256SUMS` | verify the download (`sha256sum -c SHA256SUMS`) |

See [Releases](https://github.com/xingguangYan/ResearchX/releases) and [`RELEASE-NOTES.md`](RELEASE-NOTES.md)
(what changed, how to upgrade, known limitations).

### Manual install

```bash
git clone https://github.com/xingguangYan/ResearchX
# Claude Code / Codex / most agents:
cp -r ResearchX/skills/researchx ~/.claude/skills/researchx     # or ~/.codex/skills/
# Windows (PowerShell):
# Copy-Item -Recurse ResearchX\skills\researchx $env:USERPROFILE\.codex\skills\researchx
```

Then just ask: *"find me a gap in [topic]"*, *"check my references"*, *"review this draft like a Q1 reviewer"*.

No Python packages to install: the bundled tools are standard library only.

### MCP clients

```json
{ "mcpServers": { "researchx": { "command": "python", "args": ["mcp-server/researchx_mcp_server.py"] } } }
```

Exposes `verify_citations`, `search_literature`, `prisma_screen`, `analyze_methods`, `generate_visuals`
plus the research workflow prompts. Details in [`docs/INSTALL.md`](docs/INSTALL.md).

---

## What it does — 12 modules, one loop

| # | Module | You get |
|---|---|---|
| M1 | **Paper analysis** | logic chain, why-this-approach, weaknesses, missing experiments, SOTA positioning, audit of *its* references |
| M2 | **Gap mining** | gap taxonomy + 5 topics with novelty, data, methods, venue, feasibility, scoop risk |
| M2b | **Novelty check** | claim-by-claim prior-art scan: novel / incremental / already published |
| M3 | **Method mining** | method families with reported performance *and the dataset it came from*, evolution, transfer ideas |
| M4 | **Experiment design** | baselines, ablations, sensitivity, generalisation, robustness, statistics, missing-experiment scan |
| M5 | **Manuscript writing** | journal-adapted sections, word budgets, figure plan, verified reference list |
| M6 | **Journal fit & upgrade** | ★-scores, ranked upgrade levers, 3 venue options with honest risk |
| M7 | **Adversarial peer review** | domain expert + methodologist + hostile Reviewer 2, severity, cheapest sufficient fix, response letter |
| M8 | **Visuals** | graphical-abstract prompts, poster layouts, Mermaid diagrams, figure specs (mm/DPI/font/colour-blind) |
| M9 | **Literature & systematic review** | thematic matrix, or full PRISMA 2020: counts, flow diagram, screening ledger, AI-use disclosure |
| M10 | **Grant proposal** | NSFC/国际 structure: rationale, scientific questions, technical route, innovation, risk, budget |
| M11 | **Citation audit** | 6 verdicts per reference, retraction flags, in-text↔list symmetry, correction list |
| M12 | **Reproducibility packaging** | data/code statements, 30-minute reproduction path, artifact README |

Cross-cutting: **integrity rules** (no invented numbers, no invented references, disclosure statements) and
**reproducibility** (every output records the queries, registries and date it came from).

---

## The tools behind it

```bash
# 1. Verify a bibliography (the headline tool)
python skills/researchx/scripts/verify_citations.py draft.md --format md --out citation_audit.md
python skills/researchx/scripts/verify_citations.py refs.bib --fail-on-unverified   # CI-friendly
python skills/researchx/scripts/verify_citations.py --doi 10.1038/s41586-023-06221-2

# 2. Search real literature, with citation chaining
python skills/researchx/scripts/search_literature.py \
    --query "crop mapping foundation model" --from-year 2023 --limit 30 --format json --out hits.json
python skills/researchx/scripts/search_literature.py --cited-by 10.1016/j.rse.2024.114123 --limit 50

# 3. PRISMA 2020 screening, reproducible
python skills/researchx/scripts/prisma_screen.py --input hits.json \
    --include "crop|yield" --exclude "review|editorial" --out-prefix review1
#   → review1_flow.md (Mermaid + counts), review1_ledger.csv (reason per record),
#     review1_counts.json, review1_included.json

# 4. Method landscape from a paper set
python skills/researchx/scripts/analyze_methods.py --input papers.json --format md --out methods.md

# 5. Diagrams and figure specs
python skills/researchx/scripts/generate_visuals.py workflow --topic "..." --palette colorblind
```

See a generated example (all six behaviours in one table): [`docs/example-citation-audit.md`](docs/example-citation-audit.md).

Verdicts you will see, and what they mean:

| Verdict | Meaning | Action |
|---|---|---|
| `VERIFIED` | registry record matches title + authors | cite it |
| `CORRECTED` | real work, drifted metadata | use the registry version |
| `PARTIAL` | grey literature / DOI-only match | check by hand |
| `NOT_FOUND` | no registry match — **not** proof of fabrication | label `[UNVERIFIED]` or drop the claim |
| `RETRACTED` | retraction notice exists | remove or cite as retracted |
| `ERROR` | lookup failed (offline/throttled) | retry, and say the check did not run |

---

## How it compares

| | General chat models | Reference managers | AI literature tools | **ResearchX** |
|---|---|---|---|---|
| Finds recent literature | model memory, often stale | no | yes | **yes — OpenAlex/Crossref/arXiv + web** |
| Citation verification | ✗ (hallucinates) | stores without checking | partial | **Crossref + OpenAlex + arXiv + DOI, retraction flags** |
| Experiment / ablation design | generic advice | ✗ | ✗ | **structured protocol + missing-experiment scan** |
| Peer-review simulation | soft | ✗ | ✗ | **3 personas incl. hostile reviewer + response letter** |
| Systematic review | ✗ | screening only | paid tiers | **PRISMA counts, ledger, flow diagram, disclosure** |
| Runs offline / no API keys | n/a | yes | ✗ | **`--offline` cache, stdlib only** |
| Where it runs | one app | one app | one app | **Claude Code, Codex, Cursor, Gemini CLI, Copilot, Antigravity, MCP, plain files** |
| Cost | subscription | licence | subscription | **free, MIT** |

---

## Design principles

1. **Retrieval before assertion.** Nothing about the literature is stated from model memory.
2. **The audit is the deliverable.** Outputs carry `citation_audit_*.md` with counts you can re-run.
3. **Unverifiable ≠ invented.** The tool reports what registries know and says what it does not know.
4. **Reproducible reviews.** Search strings, registries, dates and screening reasons are written down.
5. **Progressive disclosure.** `SKILL.md` stays under 500 lines; deep material loads only when needed.
6. **No dependencies.** Standard-library scripts, no keys, no service to trust.
7. **Honest limits.** Every module is required to state at least one weakness or threat to validity.

---

## Repository layout

```
skills/researchx/           the skill (this is what agents load)
├── SKILL.md                contract, task router, module summaries, quality gates
├── references/             modules · citation-verification · systematic-review-prisma ·
│                           journal-playbook · search-queries · research-design ·
│                           integrity-and-ethics · gotchas
├── scripts/                verify_citations · search_literature · prisma_screen ·
│                           analyze_methods · generate_visuals (+ rx_common)
├── assets/                 topic brief · experiment plan · manuscript skeleton ·
│                           review report · PRISMA flow · grant · artifact README
└── evals/                  trigger + behaviour cases
.claude-plugin/ .codex-plugin/ .cursor-plugin/ gemini-extension.json   install manifests
mcp-server/                 optional MCP server
scripts/                    repo tooling: version bump/check, release packaging, note extraction
tests/                      offline pytest suite + Agent Skills spec validator
platforms/                  rule files for Cursor, Cline, Continue, Windsurf, Copilot
docs/                       INSTALL · COMPARISON · ROADMAP · LAUNCH-KIT · DISCOVERY
RELEASE-NOTES.md            user-facing notes per release (the GitHub Release body)
CHANGELOG.md                developer history
```

---

## Quality gates in every output

Before anything is handed over: references verified or labelled · every number traceable · no vague
"several studies show" · at least one honest limitation · reproducibility record (queries + date) ·
saved as a file, not chat-only. The skill self-scores 0-100 and names its weakest component.

---

## FAQ

**Does it work in my field?** The retrieval, verification, review and integrity layers are domain-agnostic;
module templates cover the general lifecycle and adapt to your venue's conventions.

**What if a reference cannot be verified?** It is labelled `[UNVERIFIED]` with the reason, the claim resting
on it is downgraded, and you get a list to check by hand. The tool never asserts fabrication.

**Do I need an API key or a paid account?** No. Crossref, OpenAlex, arXiv and the DOI handle service are
open; the scripts identify themselves politely and cache every response.

**Can it run without network access?** Yes — `--offline` uses the local cache and reports that verification
did not run for uncached items.

**Is the systematic review PRISMA-compliant?** It follows PRISMA 2020 reporting (counts, flow, reasons per
record, search record) and PRISMA-trAIce disclosure for AI-assisted stages. The human decisions remain
yours — that is by design.

**Non-English research?** Query patterns, citation styles (e.g. GB/T 7714) and NSFC proposal structure are
supported; original-language titles are preserved with translations in brackets.

---

## Releasing

Version numbers live in eleven places and `scripts/bump_version.py` owns all of them:

```bash
python scripts/bump_version.py --check          # CI gate: everything must agree
python scripts/bump_version.py --set 4.1.0      # bump SKILL.md + manifests + constants
python scripts/package_skill.py --out dist      # deterministic zip/tar.gz + SHA256SUMS
git tag -a v4.1.0 -m "ResearchX v4.1.0" && git push origin v4.1.0
```

Pushing a `v*` tag runs `.github/workflows/release.yml`, which validates the skill, runs the test suite,
checks the tag against the version, builds the archives and publishes the GitHub Release using the notes
from `RELEASE-NOTES.md`. Full process: [`RELEASE-NOTES.md`](RELEASE-NOTES.md#release-process-maintainers).

## Contributing · License · Citation

Contributions welcome — especially new registry adapters, non-English workflows and evaluation cases:
[`CONTRIBUTING.md`](CONTRIBUTING.md) · [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) · [`SECURITY.md`](SECURITY.md).

MIT licensed. If ResearchX helped your research, cite it with [`CITATION.cff`](CITATION.cff).

<div align="center">

**Star it if it saved you from one fake citation.**

</div>
