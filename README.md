# ResearchX — AI Research Operating System

**The world"s first literature-driven AI research assistant for the full scientific lifecycle.**

ResearchX is a Codex skill that transforms Codex into a scientific research operating system. Unlike traditional paper-reading tools, ResearchX:

- **Does NOT hardcode methods** — It searches the latest 3 years of literature via `web_search` to dynamically discover methods, innovations, and research gaps for YOUR specific topic.
- **Covers the full lifecycle** — From literature mining → gap discovery → method selection → experiment design → manuscript writing → visual generation → peer review → grant proposals.
- **Works across all scientific domains** — Remote sensing, ecology, agriculture, medicine, materials science, computer science, and more.

## Architecture

```
ResearchX/
├── SKILL.md                    # Core skill instructions (Codex entry point)
├── agents/
│   └── openai.yaml            # UI metadata for skill chip
├── scripts/
│   ├── analyze_methods.py     # Literature analysis & method mining
│   └── generate_visuals.py    # Workflow diagrams, abstract prompts, posters
├── references/
│   ├── 01_research_design.md  # Research question & experimental design guide
│   ├── 02_writing_templates.md # SCI writing templates & style guide
│   └── 03_search_queries.md   # Web search query templates
└── assets/                    # Reserved for templates & resources
```

## Key Innovation: Literature-Driven Methodology

Most AI research tools assume methods in advance (e.g., "CNN, Transformer, SAM"). ResearchX does the opposite:

1. User provides a **topic**
2. ResearchX searches **latest 3 years of literature** via `web_search`
3. Discovers **real methods** being used in current SOTA papers
4. Identifies **gaps** and **trends** from the literature
5. Proposes **innovations** grounded in actual research landscape

## Modules

| Module | Description |
|--------|-------------|
| Paper Analysis | Deep paper parsing with research logic chain extraction |
| Research Gap Mining | Find unsolved problems and generate 5 concrete SCI topics |
| Innovation Discovery | 10-dimension scoring + novelty level classification |
| Method Mining | Literature-driven method recommendation (not hardcoded) |
| Experiment Design | Baseline, ablation, generalization, robustness tests |
| Manuscript Writing | Journal-adapted abstract, intro, methods, results |
| Visual Generation | Graphical abstract prompts + research poster layouts |
| SCI Upgrade | Gap analysis from current level → Q1 publication |
| Peer Review | Multi-perspective review simulation + response letter |
| Grant Proposal | Full NSFC/grant proposal structure with literature support |
| Literature Review | Matrix table → coherent related work section |
| Research Trends | 3-horizon trend analysis from latest literature |

## Installation

### Method 1: Copy to Codex Skills (Local)

```powershell
# Copy the ResearchX folder to Codex skills directory
Copy-Item -Recurse ".\ResearchX" "$env:USERPROFILE\.codex\skills\ResearchX"
```

### Method 2: Install as Codex Plugin (for personal marketplace)

```bash
# Use the plugin-creator skill to register ResearchX as a personal plugin
```

### Method 3: Deploy from GitHub (Recommended)

1. Push this repo to GitHub
2. In Codex settings, add the GitHub repo as a custom skill source
3. Codex will auto-discover and install ResearchX

## Usage

Trigger ResearchX by mentioning any research-related term in your prompt:

- "I need to write a paper about [topic]"
- "Analyze this paper for research gaps"
- "Find innovations for my research on [topic]"
- "What methods are SOTA for [topic] in 2025?"
- "Design experiments for my study on [topic]"
- "Help me publish in Q1"
- "Generate a graphical abstract for my paper"

## Requirements

- Codex CLI or Codex desktop app
- `web_search` tool access (for literature discovery)
- Python 3.8+ (for helper scripts)

## Contributing

This is an open-source project designed to be the world"s best research tool.
Contributions, issues, and feature requests are welcome!

## License

MIT
