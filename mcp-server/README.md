# ResearchX MCP server

Exposes ResearchX to any Model Context Protocol client — Claude Desktop, Claude Code, Cline,
Continue, Zed, and anything else that speaks MCP.

**Zero dependencies.** The server implements JSON-RPC 2.0 over stdio directly, so there is nothing to
`pip install`; it calls the stdlib-only scripts in `../skills/researchx/scripts/`.

## Configure

```json
{
  "mcpServers": {
    "researchx": {
      "command": "python",
      "args": ["/absolute/path/to/ResearchX/mcp-server/researchx_mcp_server.py"],
      "env": { "RESEARCHX_MAILTO": "you@institution.edu" }
    }
  }
}
```

## Tools

| Tool | What it does |
|---|---|
| `verify_citations` | Crossref/OpenAlex/arXiv/doi.org lookup with verdicts VERIFIED/CORRECTED/PARTIAL/NOT_FOUND/RETRACTED/ERROR and retraction flags |
| `search_literature` | Keyword search with year windows and forward/backward citation chaining |
| `prisma_screen` | Dedupe, rule screening, PRISMA 2020 counts, flow diagram, screening ledger |
| `analyze_methods` | Method families, trends, recurring limitations, datasets, innovation dimensions |
| `generate_visuals` | Mermaid diagrams, figure specs, graphical-abstract prompts |
| `researchx_status` | Installation and cache self-check |

Prompts: `research_gap_mining`, `manuscript_review`, `systematic_review`, `citation_audit`, `grant_draft`.

## Verify it works

```bash
python researchx_mcp_server.py --selftest   # offline protocol check
python researchx_mcp_server.py --list       # print tools and prompts
```
