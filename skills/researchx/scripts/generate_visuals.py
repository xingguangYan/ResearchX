#!/usr/bin/env python3
"""ResearchX — diagrams, figure specifications and graphical-abstract prompts.

Deterministic text outputs: Mermaid diagrams, image-model prompts, poster layouts, chart
specifications. Nothing here invents data — the prompts are for figures whose numbers must come
from your own results, and the script says so in its output.

Subcommands
-----------
  workflow  --topic T [--steps "a,b,c"] [--out P]     Mermaid workflow diagram
  prisma    --topic T [--out P]                       PRISMA 2020 flow skeleton + commands
  abstract  --topic T [--style nature|science|cell|rse|isprs] [--out P]   graphical abstract prompts
  poster    --topic T [--format a0|a1|9:16|conference] [--out P]           poster layout
  figure    --kind map|line|bar|scatter|confusion [--palette colorblind|default] [--out P]

Examples
--------
  python skills/researchx/scripts/generate_visuals.py workflow --topic "crop mapping" --out fig_workflow.mmd
  python skills/researchx/scripts/generate_visuals.py abstract --topic "SAR rice mapping" --style rse
  python skills/researchx/scripts/generate_visuals.py figure --kind confusion --palette colorblind
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional

PALETTES = {
    "colorblind": ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#F0E442", "#56B4E9", "#000000"],
    "default": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#7f7f7f"],
}

FIGURE_SPECS = {
    "map": {
        "purpose": "study area or spatial result",
        "must_include": [
            "scale bar",
            "north arrow",
            "CRS and units in the caption",
            "legend with class names and units",
            "inset locator map",
        ],
        "avoid": ["rainbow ramps", "unlabelled classes", "mixing discrete and continuous legends"],
    },
    "line": {
        "purpose": "trend over time, training curves, sensitivity",
        "must_include": ["axis units", "uncertainty band or error bars", "number of runs (n=)", "log scale if the range spans >3 orders"],
        "avoid": ["truncated y-axis for small effects", "unlabelled multiple series"],
    },
    "bar": {
        "purpose": "comparison across methods, classes or ablations",
        "must_include": ["n per bar", "error bars with a stated definition", "individual points when n<10", "axis starting at zero"],
        "avoid": ["3D bars", "alphabetical ordering when a ranking is intended"],
    },
    "scatter": {
        "purpose": "relationship, agreement, predicted-vs-observed",
        "must_include": ["1:1 or fit line labelled", "density hint for many points", "correlation with CI"],
        "avoid": ["overplotting without transparency", "language implying causality"],
    },
    "confusion": {
        "purpose": "per-class error structure",
        "must_include": ["row-normalised values", "class support counts", "single sequential palette"],
        "avoid": ["overall accuracy hiding a collapsed class", "diagonal-only reporting"],
    },
}

STYLE_DESCRIPTIONS = {
    "nature": "clean minimalist scientific illustration, soft gradients, precise geometry, generous white space",
    "science": "bold high-contrast visual, strong focal point, restrained palette, dynamic composition",
    "cell": "detailed mechanistic illustration, structured multi-panel layout, annotated pathway style",
    "rse": "earth-observation aesthetic: satellite imagery, map panels, spectral signature motifs",
    "isprs": "geospatial/photogrammetry aesthetic: 3D surfaces, topographic lines, coordinate frameworks",
    "default": "professional scientific graphical abstract with a clear problem → method → result flow",
}


def generate_workflow(topic: str, steps: Optional[List[str]] = None) -> str:
    steps = steps or [
        "Data acquisition",
        "Preprocessing",
        f"{topic} method",
        "Training / estimation",
        "Validation",
        "Analysis & reporting",
    ]
    lines = ["```mermaid", "flowchart TD"]
    for index, step in enumerate(steps):
        node = f"S{index}"
        label = step.replace('"', "'")
        lines.append(f'    {node}["{label}"]')
        if index:
            lines.append(f"    S{index - 1} --> {node}")
    lines.append("```")
    lines.append("")
    lines.append("> Replace the step names with your real pipeline; keep one action per node.")
    return "\n".join(lines)


def prisma_skeleton(topic: str) -> str:
    return f"""## PRISMA 2020 flow skeleton — {topic}

Generate the real diagram and counts with the screening script (never hand-count):

```bash
python skills/researchx/scripts/search_literature.py --query "{topic}" --from-year 2015 --format json --out hits.json
python skills/researchx/scripts/prisma_screen.py --input hits.json --include "..." --exclude "review|editorial" --out-prefix review1
```

```mermaid
flowchart TD
  subgraph ID["Identification"]
    S1["records from OpenAlex: n = ?"] --> Q["total identified: n = ?"]
    S2["records from Crossref: n = ?"] --> Q
    S3["other sources: n = ?"] --> Q
  end
  subgraph SC["Screening"]
    Q --> D["duplicates removed: n = ?"]
    D --> T["screened on title/abstract: n = ?"]
    T --> E["excluded: n = ? (reasons)"]
  end
  subgraph EL["Eligibility"]
    T --> F["full texts assessed: n = ?"]
    F --> H["excluded: n = ? (reasons)"]
  end
  subgraph IN["Included"]
    F --> I["studies in synthesis: n = ?"]
  end
```

Also record: search strings, registries, date of last search, screening rules, disagreement handling,
registration ID, and any AI assistance at any stage (PRISMA-trAIce)."""


def generate_abstract_prompt(topic: str, style: str) -> str:
    description = STYLE_DESCRIPTIONS.get(style.lower(), STYLE_DESCRIPTIONS["default"])
    return f"""## Graphical abstract — {topic}

**Style**: {style} — {description}
**Canvas**: 16:9 or 4:3 depending on the venue's template; check the author guidelines first.

### Composition (left → right)
- **Left — problem/input**: the data or phenomenon, represented truthfully (no invented numbers).
- **Centre — method**: the core mechanism as shapes and arrows; one idea per element.
- **Right — outcome**: what changed, with a real result shown qualitatively.

### Prompt — GPT Image / DALL·E style
"A professional graphical abstract about {topic}. {description}. Three-panel left-to-right flow:
problem, method, outcome. Minimal labels (≤10 words), no numbers, no fake charts, white background,
flat vector look, print-safe colours."

### Prompt — Midjourney
"scientific graphical abstract, {topic}, three-panel problem-method-result flow, {description},
clean flat vector illustration, white background, print ready --ar 16:9 --style raw --v 6"

### Prompt — Flux / Ideogram
"Clean scientific graphical abstract for a paper on {topic}. Left: input data. Centre: method diagram
with arrows. Right: qualitative result. Flat vector, high contrast, readable at 85 mm width, white
background, no text placeholders, no fabricated numbers."

### Rules (non-negotiable)
- No invented values, axes, or significance markers.
- No AI-generated image may be presented as primary data (microscopy, satellite, gels).
- Check the venue's policy on generated imagery before submission; disclose if required.
- Verify the final file at print size: labels ≥7 pt, greyscale legible."""


def generate_poster(topic: str, fmt: str) -> str:
    sizes = {
        "a0": "841 × 1189 mm (portrait)",
        "a1": "594 × 841 mm (portrait)",
        "9:16": "vertical digital/social format",
        "conference": "1220 × 915 mm landscape (48 × 36 in)",
    }
    return f"""## Research poster — {topic}

**Format**: {fmt.upper()} — {sizes.get(fmt.lower(), sizes['a0'])}

```
┌──────────────────────────────────────────┐
│ TITLE (≤ 2 lines) · Authors · Affiliations│
├──────────────────────────────────────────┤
│ Motivation (1-2 sentences) │ 1 key visual │
├───────────────────┬──────────────────────┤
│ Data & methods    │ Method schematic     │
├───────────────────┴──────────────────────┤
│ Key result (one hero figure, annotated)  │
├───────────────────┬──────────────────────┤
│ Interpretation    │ Limitations / next   │
├───────────────────┴──────────────────────┤
│ References (3-5) · QR to code/data       │
└──────────────────────────────────────────┘
```

**Type scale (A0)**: title 72-96 pt bold · section headers 36-42 pt · body 24-28 pt · captions 20-24 pt.
**Layout rules**: 40% text / 60% figures · readable from 1.5 m · one message per panel · consistent
palette (use the figure spec palette) · QR code links to the paper, code and data.
**Ethics**: the poster shows published, verified results — no preliminary numbers presented as final."""


def figure_spec(kind: str, palette: str) -> str:
    spec = FIGURE_SPECS.get(kind, FIGURE_SPECS["line"])
    colours = " · ".join(PALETTES.get(palette, PALETTES["colorblind"]))
    must = "\n".join(f"- {item}" for item in spec["must_include"])
    avoid = "\n".join(f"- {item}" for item in spec["avoid"])
    return f"""## Figure spec — {kind}

**Purpose**: {spec['purpose']}
**Size**: 85 mm (single column) or 170 mm (double column); height ≤ 220 mm
**Format**: vector (PDF/SVG/EPS) for plots; 300-600 DPI raster for maps and imagery
**Fonts**: Helvetica/Arial, ≥7 pt at final size; panels labelled (a), (b) bold 8-9 pt
**Palette ({palette})**: {colours}
**Accessibility**: never encode meaning by colour alone; check the greyscale print

**Must include**
{must}

**Avoid**
{avoid}

**Caption pattern**: what is shown → data source → n and uncertainty definition → the conclusion

> The values must come from your results table. A generator must never invent numbers, and synthetic
> imagery must never be presented as measurement."""


def write_or_print(text: str, out: Optional[str], quiet: bool = False) -> None:
    if out:
        path = Path(out)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text + "\n", encoding="utf-8")
        if not quiet:
            print(f"written to {out}", file=sys.stderr)
    else:
        print(text)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="generate_visuals.py",
        description="ResearchX — diagrams, figure specs and graphical-abstract prompts (stdlib only)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    workflow = sub.add_parser("workflow", help="Mermaid workflow diagram")
    workflow.add_argument("--topic", "-t", required=True)
    workflow.add_argument("--steps", "-s", help="comma-separated step labels")
    workflow.add_argument("--out", "-o", default=None)

    prisma = sub.add_parser("prisma", help="PRISMA 2020 flow skeleton + the commands that fill it")
    prisma.add_argument("--topic", "-t", required=True)
    prisma.add_argument("--out", "-o", default=None)

    abstract = sub.add_parser("abstract", help="graphical abstract prompts (3 image platforms)")
    abstract.add_argument("--topic", "-t", required=True)
    abstract.add_argument("--style", default="default", choices=sorted(STYLE_DESCRIPTIONS))
    abstract.add_argument("--out", "-o", default=None)

    poster = sub.add_parser("poster", help="research poster layout")
    poster.add_argument("--topic", "-t", required=True)
    poster.add_argument("--format", default="a0", choices=["a0", "a1", "9:16", "conference"])
    poster.add_argument("--out", "-o", default=None)

    figure = sub.add_parser("figure", help="figure specification for a chart type")
    figure.add_argument("--kind", default="line", choices=sorted(FIGURE_SPECS))
    figure.add_argument("--palette", default="colorblind", choices=sorted(PALETTES))
    figure.add_argument("--out", "-o", default=None)

    args = parser.parse_args(argv)

    if args.command == "workflow":
        steps = [s.strip() for s in args.steps.split(",")] if args.steps else None
        write_or_print(generate_workflow(args.topic, steps), args.out)
    elif args.command == "prisma":
        write_or_print(prisma_skeleton(args.topic), args.out)
    elif args.command == "abstract":
        write_or_print(generate_abstract_prompt(args.topic, args.style), args.out)
    elif args.command == "poster":
        write_or_print(generate_poster(args.topic, args.format), args.out)
    elif args.command == "figure":
        write_or_print(figure_spec(args.kind, args.palette), args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
