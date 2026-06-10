# 🔍 How to Find & Install ResearchX

ResearchX is available on multiple platforms and registries. Choose your platform below.

---

## 📦 Quick Install (Any Platform)

```bash
# Option 1: Direct from GitHub (recommended)
git clone https://github.com/xingguangYan/ResearchX.git
cd ResearchX

# Option 2: npm (for Node.js / MCP environments)
npx researchx-mcp

# Option 3: pip (for Python environments)
pip install researchx-mcp
```

---

## 🔎 Platform-Specific Discovery

### 1. Codex (OpenAI)

**Search in Codex**: Mention any research-related term → ResearchX auto-activates

| Method | Command |
|--------|---------|
| Install from marketplace | `codex plugin add researchx@personal` |
| Copy skill directly | `Copy-Item -Recurse "ResearchX" "$env:USERPROFILE\.codex\skills\ResearchX"` |
| Search on GitHub | [github.com/xingguangYan/ResearchX](https://github.com/xingguangYan/ResearchX) |

### 2. Claude Desktop (Anthropic)

**Search the MCP Ecosystem**: ResearchX is available as an MCP server

```bash
# Install from npm
npx researchx-mcp

# Or add to Claude Desktop config:
# Claude → Settings → Developer → MCP Servers → Add
# Name: researchx
# Command: npx researchx-mcp
```

Claude Desktop config (`claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "researchx": {
      "command": "npx",
      "args": ["researchx-mcp"]
    }
  }
}
```

### 3. Claude Code (Anthropic)

**CLAUDE.md auto-discovery**: Copy `platforms/CLAUDE.md` to your project root

```bash
cp platforms/CLAUDE.md ./CLAUDE.md
```

Claude Code auto-reads CLAUDE.md on project open.

### 4. Cline / Roo Code

**Search MCP Directory**: ResearchX is available in MCP format

```bash
# Install as MCP server
cp platforms/.clinerules ./.clinerules

# Or add MCP server:
# Cline Settings → MCP Servers → Add
# Name: researchx
# Command: npx researchx-mcp
```

### 5. Continue.dev

**Search the MCP Ecosystem**: Add to your Continue config

```json
{
  "mcpServers": {
    "researchx": {
      "command": "npx",
      "args": ["researchx-mcp"]
    }
  }
}
```

Also copy `.continuerules`:
```bash
cp platforms/.continuerules ./.continuerules
```

### 6. Cursor

**Install from GitHub or NPM**:

```bash
cp platforms/.cursorrules ./.cursorrules
```

### 7. Windsurf

```bash
cp platforms/.windsurfrules ./.windsurfrules
```

### 8. OpenAI GPT Store

**Search "ResearchX" in the GPT Store** (coming soon):

1. Go to [chat.openai.com/gpts](https://chat.openai.com/gpts)
2. Search: "ResearchX"
3. Click "ResearchX — AI Research Assistant"
4. Start using

Or build your own from the config:
```bash
cat mcp-server/gpt_builder.json
```

### 9. npm Registry

**Search**: `npm search researchx-mcp`

```bash
npm install researchx-mcp
npx researchx-mcp
```

Published package: [npmjs.com/package/researchx-mcp](https://npmjs.com/package/researchx-mcp)

### 10. PyPI (Python Package Index)

**Search**: `pip search researchx-mcp`

```bash
pip install researchx-mcp
researchx-mcp
```

Published package: [pypi.org/project/researchx-mcp](https://pypi.org/project/researchx-mcp)

---

## 🏪 Registry & Directory Listings

ResearchX is registered in these directories:

| Directory | Link | How to Find |
|-----------|------|-------------|
| **GitHub** | [xingguangYan/ResearchX](https://github.com/xingguangYan/ResearchX) | Search "ResearchX" or "AI research operating system" |
| **npm** | researchx-mcp | `npm search researchx` |
| **PyPI** | researchx-mcp | `pip search researchx-mcp` |
| **Codex Marketplace** | Personal marketplace | `codex plugin add researchx@personal` |
| **MCP Ecosystem** | researchx-mcp | MCP client settings → Add server |
| **OpenAI GPT Store** | ResearchX | Coming soon — search in GPT Store |

---

## 🏷 GitHub Topics

This repo uses these discoverability topics:

`research` `scientific-research` `research-paper` `literature-review` `mcp-server` `model-context-protocol` `ai-research` `paper-analysis` `research-agent` `academic-writing` `scri-journal` `research-tool`

---

## 📢 How to Recommend ResearchX

Share with colleagues:

```text
"Check out ResearchX — an AI research operating system that works with Codex, Claude, Cursor, and more!
It searches the latest literature to find methods and gaps, not hardcoded templates.
https://github.com/xingguangYan/ResearchX"
```

---

*ResearchX — Moving research assistance from "what I know" to "what the field knows."*
