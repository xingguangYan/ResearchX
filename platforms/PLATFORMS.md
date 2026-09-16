# Platform notes

ResearchX ships one skill (`skills/researchx/`) and thin per-platform wrappers. Prefer the plugin install
route when your agent supports it (`docs/INSTALL.md`); the rule files here are for agents that read a
project-root config file instead.

| Platform | File to copy to your project root | Notes |
|---|---|---|
| Claude Code | `.claude-plugin/` (in-repo manifests) | `/plugin marketplace add xingguangYan/ResearchX` |
| Codex | `.codex-plugin/plugin.json` | plugin browser, or copy `skills/researchx` to `~/.codex/skills/` |
| Cursor | `platforms/.cursorrules` | or `/add-plugin researchx` |
| Cline / Roo Code | `platforms/.clinerules` | or use the MCP server |
| Continue.dev | `platforms/.continuerules` | or use the MCP server |
| Windsurf | `platforms/.windsurfrules` | or MCP |
| Gemini CLI | `gemini-extension.json` + `GEMINI.md` | `gemini extensions install <repo-url>` |
| GitHub Copilot | `AGENTS.md` (repo root) | copied automatically in agentic modes |
| Any MCP client | `mcp-server/researchx_mcp_server.py` | stdio, zero dependencies |

## Keeping wrappers thin

Rule files must not duplicate the skill. They should say: read `skills/researchx/SKILL.md`, follow its
contract, load `references/*.md` on demand, and run the scripts for anything that touches references.
Duplicated instructions drift and the copies win — that is how agents end up ignoring the integrity rules.

## Verifying a wrapper

```bash
python tests/validate_skill.py --strict          # skill package
python -m pytest tests -q                        # offline suite
python mcp-server/researchx_mcp_server.py --selftest   # MCP transport
```

If a platform ignores the skill entirely, check that its skill directory name matches the frontmatter
`name` (`researchx`) and that `SKILL.md` starts with valid YAML frontmatter.
