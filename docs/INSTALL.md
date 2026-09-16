# Installation

ResearchX is a single skill folder (`skills/researchx/`) plus optional plugin manifests. Pick the route
for your agent — every route takes under a minute, and none of them require `pip install`.

Requirements: Python 3.9+ **only if** you want the bundled tools (citation verification, literature
search, PRISMA screening, method mining, diagrams). Everything is standard library, and the agent works
without them — it just loses the ability to verify citations against registries.

---

## Download a release instead of cloning

Prefer a packaged artifact? Take it from the [Releases page](https://github.com/xingguangYan/ResearchX/releases):

```bash
curl -LO https://github.com/xingguangYan/ResearchX/releases/latest/download/SHA256SUMS
curl -LO https://github.com/xingguangYan/ResearchX/releases/latest/download/researchx-skill-v4.0.0.zip
sha256sum -c SHA256SUMS || shasum -a 256 -c SHA256SUMS
unzip researchx-skill-v4.0.0.zip -d /tmp/researchx
cp -r /tmp/researchx/researchx ~/.claude/skills/researchx
```

## Claude Code

```bash
/plugin marketplace add xingguangYan/ResearchX
/plugin install researchx@researchx
```

Update later with `/plugin marketplace update researchx` (or reinstall). The plugin ships the skill plus
the scripts; no extra setup.

Manual alternative:

```bash
git clone https://github.com/xingguangYan/ResearchX
mkdir -p ~/.claude/skills && cp -r ResearchX/skills/researchx ~/.claude/skills/
```

## Codex (app or CLI)

- **App**: open **Plugins** in the sidebar, search **researchx**, click install.
- **CLI**: `codex plugin marketplace add xingguangYan/ResearchX` then install `researchx`.
- **Manual**: copy `skills/researchx` into `$CODEX_HOME/skills/` (default `~/.codex/skills/`):

```powershell
Copy-Item -Recurse ResearchX\skills\researchx $env:USERPROFILE\.codex\skills\researchx
```

## Cursor

```text
/add-plugin researchx
```

Or copy `platforms/.cursorrules` into your project root, and keep `skills/researchx/` in the repo so the
agent can read the reference files.

## Gemini CLI

```bash
gemini extensions install https://github.com/xingguangYan/ResearchX
gemini extensions update researchx
```

The extension uses `gemini-extension.json` + `GEMINI.md`.

## GitHub Copilot CLI

```bash
copilot plugin marketplace add xingguangYan/ResearchX
copilot plugin install researchx@researchx
```

## Antigravity

```bash
agy plugin install https://github.com/xingguangYan/ResearchX
```

## MCP clients (Claude Desktop, Cline, Continue, Zed, …)

Add to the client config (see `mcp-server/claude_desktop_config.json`):

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

Check it:

```bash
python mcp-server/researchx_mcp_server.py --selftest
python mcp-server/researchx_mcp_server.py --list
```

## Cline / Roo Code / Continue.dev / Windsurf

Copy the matching rule file from `platforms/` into your project root:

```bash
cp platforms/.clinerules ./.clinerules          # Cline / Roo Code
cp platforms/.continuerules ./.continuerules    # Continue.dev
cp platforms/.windsurfrules ./.windsurfrules    # Windsurf
```

## Any other agent (plain files)

Copy `skills/researchx/` into the agent's skills directory, or paste `SKILL.md` into the system prompt and
keep `references/` and `scripts/` next to it:

| Scope | Conventional path |
|---|---|
| User (interop) | `~/.agents/skills/researchx/` |
| User (Claude-compatible) | `~/.claude/skills/researchx/` |
| Project | `.claude/skills/researchx/` or `.agents/skills/researchx/` |

---

## Verify the installation

```bash
cd ResearchX
make check                                  # validator + offline tests + manifests
python tests/validate_skill.py --strict     # Agent Skills spec compliance
python skills/researchx/scripts/verify_citations.py --help
python mcp-server/researchx_mcp_server.py --selftest
```

A live smoke test (needs network):

```bash
python skills/researchx/scripts/verify_citations.py --doi 10.1038/s41586-023-06221-2
```

Expect `VERIFIED` with the registry record. If you see `ERROR`, the environment cannot reach
`api.crossref.org` — the skill still works, it will label references `[UNVERIFIED]` instead of pretending.

## Configuration

| Variable | Effect |
|---|---|
| `RESEARCHX_MAILTO` | Contact email for Crossref/OpenAlex polite pools (faster, fewer throttles). Recommended. |
| `--cache-dir` | Where responses are cached (default `.researchx-cache/` in the working directory). |
| `--offline` | Never touch the network; use the cache only. |

## Troubleshooting

| Symptom | Fix |
|---|---|
| `ERROR` verdicts for every reference | No network or registries throttling → add `--mailto`, `--sleep 0.5`, retry; or accept `[UNVERIFIED]` labels and say so in the write-up |
| `NOT_FOUND` for a paper you can open in a browser | Books, theses, standards and very new papers are often unindexed; try the title-only search, then mark `[UNVERIFIED]` and cite the publisher page |
| Script not found / import error | Run scripts with the repository root as the working directory, or pass the full path |
| MCP server not listed in the client | Use an absolute path in `args`, and confirm `python --version` is 3.9+ |
| Everything works but the agent ignores the skill | Make sure the folder is named `researchx` and contains `SKILL.md` with valid frontmatter (`python tests/validate_skill.py`) |
