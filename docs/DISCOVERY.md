# Discovery — how people find and install ResearchX

## Registries and directories

| Channel | Where | Status |
|---|---|---|
| GitHub | [xingguangYan/ResearchX](https://github.com/xingguangYan/ResearchX) | source of truth |
| GitHub topics | `research`, `agent-skills`, `citation-verification`, `literature-review`, `prisma`, `systematic-review`, `manuscript`, `peer-review`, `grant`, `mcp-server`, `claude-code`, `codex`, `academic-writing`, `ai4science` | set on the repo |
| Claude Code plugin marketplace | `/plugin marketplace add xingguangYan/ResearchX` | `.claude-plugin/marketplace.json` |
| Codex plugins | plugin manifest `.codex-plugin/plugin.json` | install via the Codex plugin browser |
| Cursor | `/add-plugin researchx` | `.cursor-plugin/plugin.json` |
| Gemini CLI | `gemini extensions install https://github.com/xingguangYan/ResearchX` | `gemini-extension.json` |
| GitHub Copilot CLI | `copilot plugin marketplace add xingguangYan/ResearchX` | repo manifests |
| Antigravity | `agy plugin install https://github.com/xingguangYan/ResearchX` | repo manifests |
| MCP clients | `mcp-server/researchx_mcp_server.py` (stdio, zero dependencies) | `mcp-server/` |
| Agent Skills spec | `skills/researchx/SKILL.md` is spec-valid | validated in CI |

## Search keywords that should lead here

`research assistant agent skill`, `citation verification agent`, `hallucinated references checker`,
`PRISMA systematic review agent`, `literature review skill`, `Crossref OpenAlex agent tool`,
`manuscript writing skill`, `peer review simulation`, `grant proposal generator`, `ResearchX skill`.

If a search for these does **not** surface the repo, that is a bug worth fixing — open an issue with the
query.

## What makes it shareable

1. **One command per platform** — the plugin manifests mean no file copying.
2. **A single sharp promise** — "every reference is checked against Crossref/OpenAlex/arXiv".
3. **A demo that takes 10 seconds** — `verify_citations.py draft.md` prints verdicts and corrections.
4. **No dependencies, no keys, no account** — nothing to sign up for, nothing to pay.
5. **A real failure story** — a corrected year or a caught retraction is more convincing than a feature list.

## Where to submit (curated lists and directories)

| List / directory | Entry format |
|---|---|
| `karanb192/awesome-claude-skills` | short description + link (see `docs/LAUNCH-KIT.md`) |
| `travisvn/awesome-claude-skills` | tool row with one-line description |
| `jqueryscript/awesome-claude-code` | agent-skills section entry |
| `GetBindu/awesome-claude-code-and-skills` | "Domain-specific skills → research" entry |
| `anthropics/skills` (community references) | only if it fits their contribution guide |
| Model Context Protocol server lists | MCP server entry with the stdio command |
| Research-software directories (e.g. SciPy/awesome-scientific-python style lists) | tool entry mentioning the citation-verification capability |

Keep submissions factual, one per list, and always link the install command — directories exist to save
people time, so make the install obvious.

## Measurement

Track weekly: stars, install-method issues, verdicts reported wrong (the most valuable metric — each one
should become a test fixture), and the ratio of `NOT_FOUND` to `VERIFIED` on real drafts. A rising
`NOT_FOUND` rate usually means a missing registry adapter, not growing fraud.
