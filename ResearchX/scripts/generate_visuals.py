"""ResearchX — Visual Generation Tool

Generates Mermaid code for research diagrams and produces prompts for
graphical abstracts and research posters.

Usage:
    python scripts/generate_visuals.py workflow --topic "<topic>" [--steps "s1,s2,s3,..."]
    python scripts/generate_visuals.py abstract --topic "<topic>" --style <style>
    python scripts/generate_visuals.py poster --topic "<topic>" --format <format>
"""

import argparse
import textwrap
import sys


def generate_workflow(topic: str, steps: list = None) -> str:
    """Generate Mermaid workflow diagram code."""
    if not steps:
        steps = [
            "Data Acquisition",
            "Preprocessing",
            f"{topic} Method",
            "Training & Optimization",
            "Validation & Testing",
            "Result Analysis",
            "Conclusion",
        ]

    mermaid = ["```mermaid", "graph TD"]
    for i, step in enumerate(steps):
        node_id = f"S{i}"
        safe_label = step.replace('"', "'")
        mermaid.append(f'    {node_id}["{safe_label}"]')
        if i > 0:
            mermaid.append(f"    S{i - 1} --> {node_id}")

    mermaid.append("```")
    return "\n".join(mermaid)


def generate_comparison_flow(topic: str, methods: list) -> str:
    """Generate Mermaid comparison/ablation diagram."""
    mermaid = ["```mermaid", "graph LR"]
    mermaid.append(f'    Input["Input Data"]')

    for i, method in enumerate(methods):
        safe = method.replace('"', "'")
        mermaid.append(f'    M{i}["{safe}"]')
        mermaid.append(f"    Input --> M{i}")
        mermaid.append(f'    M{i} --> R{i}["Result {i+1}"]')

    mermaid.append("```")
    return "\n".join(mermaid)


def generate_abstract_prompt(topic: str, style: str) -> str:
    """Generate AI image generation prompt for graphical abstract."""
    style_descriptions = {
        "nature": "Clean, minimalist scientific illustration style. Nature journal aesthetic. Soft gradients, precise geometric shapes, clear flow arrows.",
        "science": "Bold, impactful visual style with strong color contrast. Science journal aesthetic. Dynamic composition.",
        "cell": "Detailed mechanistic illustration style. Cell journal aesthetic. Multi-panel structured layout with annotations.",
        "rse": "Remote Sensing of Environment style. Earth observation focus. Maps, satellite imagery integration, spectral signatures.",
        "isprs": "ISPRS style. Geospatial and photogrammetry focus. 3D elements, topographic visualization.",
        "default": "Professional scientific graphical abstract. Clear left-to-right flow from problem to method to result.",
    }

    style_desc = style_descriptions.get(style.lower(), style_descriptions["default"])

    prompt = f"""## Graphical Abstract Prompt

**Style**: {style.upper()}

**Subject**: {topic}

**Visual Flow** (Left → Right):
- **Left panel**: Research problem / data input
- **Center panel**: Core methodology / workflow
- **Right panel**: Key results / demonstration

**Composition Guidelines**:
- {style_desc}
- Use arrows to indicate workflow direction
- Include 1-2 key data visualizations (charts, maps, or graphs)
- Keep text labels minimal (10-15 words total)

**Color Palette Recommendation**:
- Primary: Deep blue (#1a5276) or dark teal
- Secondary: Warm accent (orange/amber #e67e22)
- Background: White or very light gray
- Accent: Green for positive results, red for highlighting

**AI Platform Prompts**:

### For GPT Image:
"A professional graphical abstract showing {topic}. {style_desc} Left panel shows research input, center panel shows methodology workflow, right panel shows results. Clean scientific illustration style."

### For Midjourney:
"Scientific graphical abstract, {topic} research, professional journal style, clean composition, three-panel flow layout, technical illustration, white background, precise vector graphics --ar 16:9 --v 6"

### For Flux/Ideogram:
"Professional graphical abstract for {topic} research paper. Three-panel layout with problem-method-result flow. Scientific illustration style. Clean white background."
"""
    return prompt


def generate_poster(topic: str, fmt: str) -> str:
    """Generate research poster layout."""
    formats = {
        "a0": "841 × 1189 mm (portrait)",
        "a1": "594 × 841 mm (portrait)",
        "9:16": "Vertical format for mobile/social media",
        "conference": "Landscape, 36×48 inches or 1220×915 mm",
    }

    fmt_desc = formats.get(fmt.lower(), formats["a0"])

    poster = f"""## Research Poster Layout

**Topic**: {topic}
**Format**: {fmt.upper()} — {fmt_desc}

### Section Layout (Top to Bottom)

```
┌─────────────────────────────────────┐
│         TITLE + Authors             │
│    (Bold, 3-4 lines max)            │
├─────────────────────────────────────┤
│           Background                │
│    (1-2 sentences + 1 key figure)   │
├──────────────────┬──────────────────┤
│      Data        │    Method        │
│   (sources,      │  (core workflow  │
│    stats)        │   diagram)       │
├──────────────────┴──────────────────┤
│         Key Results                 │
│   (2-4 figures + short captions)    │
├─────────────────────────────────────┤
│    Innovation   │   Future Work     │
├─────────────────────────────────────┤
│   References + Acknowledgments      │
│   (QR Code to paper if available)   │
└─────────────────────────────────────┘
```

### Font Sizes (for A0 format)
- Title: 72-96pt, Bold
- Authors: 36-48pt
- Section Headers: 36-42pt, Bold
- Body Text: 24-28pt
- Figure Captions: 20-24pt

### Design Tips
- Use 2-3 color scheme consistent with your paper
- Figures should be readable from 1-2 meters away
- Include QR code linking to full paper/code
- Keep text density low — aim for 60% figures, 40% text
"""
    return poster


def main():
    parser = argparse.ArgumentParser(description="ResearchX Visual Generation Tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Workflow diagram
    wf = subparsers.add_parser("workflow", help="Generate Mermaid workflow diagram")
    wf.add_argument("--topic", "-t", required=True, help="Research topic")
    wf.add_argument("--steps", "-s", help="Comma-separated step names")

    # Abstract prompt
    ab = subparsers.add_parser("abstract", help="Generate graphical abstract prompt")
    ab.add_argument("--topic", "-t", required=True, help="Research topic")
    ab.add_argument(
        "--style", default="default", choices=["nature", "science", "cell", "rse", "isprs", "default"]
    )

    # Poster layout
    po = subparsers.add_parser("poster", help="Generate research poster layout")
    po.add_argument("--topic", "-t", required=True, help="Research topic")
    po.add_argument(
        "--format", default="a0", choices=["a0", "a1", "9:16", "conference"]
    )

    args = parser.parse_args()

    if args.command == "workflow":
        steps = args.steps.split(",") if args.steps else None
        print(generate_workflow(args.topic, steps))

    elif args.command == "abstract":
        print(generate_abstract_prompt(args.topic, args.style))

    elif args.command == "poster":
        print(generate_poster(args.topic, args.format))


if __name__ == "__main__":
    main()
