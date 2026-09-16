"""ResearchX — Literature Analysis & Method Mining Tool

Analyzes paper data from web_search results to produce:
  - Method taxonomy & trend analysis
  - Research gap identification
  - Innovation scoring
  - Method evolution timelines
  - Cross-domain transfer opportunities

Usage:
    python scripts/analyze_methods.py --input papers.json --output report.json
    python scripts/analyze_methods.py --input papers.json --output report.json --format markdown

Input format: JSON array of paper objects with:
  {title, year, journal, method, result, limitation, dataset, innovation}
"""

import json, sys, argparse
from pathlib import Path
from collections import defaultdict
from datetime import datetime


# --------------- Data Loading ---------------

def load_papers(input_path: str) -> list:
    """Load paper data from JSON file, handling BOM."""
    raw = Path(input_path).read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        raw = raw[3:]
    data = json.loads(raw.decode("utf-8"))
    return data if isinstance(data, list) else [data]


# --------------- Core Analysis ---------------

def classify_years(papers: list) -> dict:
    by_year = defaultdict(list)
    for p in papers:
        year = str(p.get("year", "unknown"))
        by_year[year].append(p)
    return dict(sorted(by_year.items()))


def extract_method_families(papers: list) -> dict:
    families = defaultdict(list)
    for p in papers:
        method = (p.get("method") or "").strip()
        if method:
            families[method].append(p.get("title", "Untitled"))
    return dict(families)


def compute_trend_scores(by_year: dict) -> list:
    method_year_count = defaultdict(lambda: defaultdict(int))
    for year, papers in by_year.items():
        for p in papers:
            method = (p.get("method") or "unknown").strip()
            method_year_count[method][year] += 1

    trends = []
    for method, year_counts in method_year_count.items():
        years = sorted(year_counts.keys())
        counts = [year_counts[y] for y in years]
        if len(years) >= 2:
            mid = len(years) // 2
            first_half = sum(counts[:mid])
            second_half = sum(counts[mid:])
            trend = "emerging" if second_half > first_half else ("declining" if first_half > second_half else "stable")
        else:
            trend = "new"
        trends.append({
            "method": method,
            "year_counts": dict(year_counts),
            "trend": trend,
            "total": sum(counts)
        })
    return sorted(trends, key=lambda x: -x["total"])


def identify_gaps(papers: list) -> dict:
    all_limitations = []
    for p in papers:
        lim = (p.get("limitation") or "").strip()
        if lim:
            all_limitations.append({"paper": p.get("title", ""), "limitation": lim})

    keyword_map = {
        "generalization": ["generalization", "generalisation", "transfer", "domain shift"],
        "scalability": ["scalability", "scalable", "large-scale"],
        "robustness": ["robustness", "noise", "adversarial"],
        "labeled data": ["labeled data", "label", "annotation", "training data"],
        "computation": ["computational cost", "efficiency", "memory", "inference time"],
        "interpretability": ["interpretability", "explainability", "black box"],
        "data quality": ["data quality", "resolution", "cloud", "missing data"],
        "class imbalance": ["class imbalance", "long tail", "rare class"],
        "multi-modal fusion": ["multi-modal", "multi-source", "fusion", "heterogeneous"],
        "temporal dynamics": ["temporal", "time series", "seasonal", "dynamic"],
    }

    gap_counts = defaultdict(int)
    for item in all_limitations:
        text = item["limitation"].lower()
        for gap_key, keywords in keyword_map.items():
            if any(kw in text for kw in keywords):
                gap_counts[gap_key] += 1

    sorted_gaps = sorted(gap_counts.items(), key=lambda x: -x[1])
    return {
        "total_papers_with_limitations": len(all_limitations),
        "gap_frequency": [{"gap": k, "count": v} for k, v in sorted_gaps],
        "all_limitations": all_limitations
    }


def extract_datasets(papers: list) -> list:
    dataset_counts = defaultdict(int)
    for p in papers:
        ds = (p.get("dataset") or "").strip()
        if ds:
            for d in [x.strip() for x in ds.split(",")]:
                if d:
                    dataset_counts[d] += 1
    return sorted([{"dataset": k, "count": v} for k, v in dataset_counts.items()], key=lambda x: -x["count"])


def compute_innovation_scores(papers: list) -> dict:
    scores = defaultdict(list)
    for p in papers:
        innov = (p.get("innovation") or "").strip()
        if not innov:
            continue
        # Simple keyword-based scoring
        keywords = {
            "theoretical": ["theory", "theoretical", "mechanism", "framework"],
            "data": ["dataset", "data", "multi-source"],
            "model": ["model", "architecture", "network", "transformer", "cnn"],
            "application": ["application", "domain", "task", "problem", "novel"],
            "experimental": ["experiment", "ablation", "benchmark"]
        }
        for dim, kws in keywords.items():
            if any(kw in innov.lower() for kw in kws):
                scores[dim].append(p.get("title", ""))
    return dict(scores)


# --------------- Report Generation ---------------

def generate_report(papers: list) -> dict:
    by_year = classify_years(papers)
    method_families = extract_method_families(papers)
    trends = compute_trend_scores(by_year)
    gaps = identify_gaps(papers)
    datasets = extract_datasets(papers)
    innovations = compute_innovation_scores(papers)
    top_methods = list(method_families.keys())[:8]
    emerging = [t for t in trends if t["trend"] in ("emerging", "new")]

    return {
        "report_metadata": {
            "generated_at": datetime.now().isoformat(),
            "total_papers": len(papers),
            "year_range": [min(by_year.keys()), max(by_year.keys())] if by_year else []
        },
        "year_distribution": {k: len(v) for k, v in by_year.items()},
        "method_families": {k: v for k, v in list(method_families.items())[:12]},
        "method_trends": trends,
        "emerging_methods": [t["method"] for t in emerging],
        "top_gaps": [g["gap"] for g in gaps["gap_frequency"][:8]],
        "gap_details": gaps["gap_frequency"][:8],
        "datasets_found": datasets[:8],
        "innovation_dimensions": innovations,
        "summary": {
            "total_papers": len(papers),
            "unique_methods": len(method_families),
            "dominant_methods": [{"method": k, "paper_count": len(v)} for k, v in list(method_families.items())[:5]],
            "emerging_trends": [t["method"] for t in emerging[:5]],
            "critical_gaps": [g["gap"] for g in gaps["gap_frequency"][:3]],
            "recommended_datasets": [d["dataset"] for d in datasets[:3]]
        }
    }


def format_markdown(report: dict) -> str:
    s = report["summary"]
    lines = [
        f"# ResearchX Method Analysis Report",
        f"",
        f"> Built from the paper set you supplied. Every family, trend and gap below inherits the",
        f"> quality of that file — if it came from `search_literature.py` (real registry records),",
        f"> these numbers are traceable; if it came from memory, they are not. Cite the DOIs.",
        f"",
        f"**Generated**: {report['report_metadata']['generated_at']}",
        f"**Papers Analyzed**: {s['total_papers']}",
        f"**Year Range**: {' - '.join(report['report_metadata']['year_range'])}",
        f"**Unique Methods Found**: {s['unique_methods']}",
        f"",
        f"## Dominant Methods",
    ]
    for m in s["dominant_methods"]:
        lines.append(f"- **{m['method']}** ({m['paper_count']} papers)")
    lines.extend([
        "",
        "## Emerging Trends",
    ])
    for t in s["emerging_trends"]:
        lines.append(f"- {t}")
    lines.extend([
        "",
        "## Critical Research Gaps",
    ])
    for g in s["critical_gaps"]:
        lines.append(f"- {g}")
    lines.extend([
        "",
        "## Recommended Datasets",
    ])
    for d in s["recommended_datasets"]:
        lines.append(f"- {d}")
    lines.extend([
        "",
        "## Method Trend Details",
    ])
    for t in report["method_trends"][:10]:
        icon = {"emerging": "↑", "declining": "↓", "stable": "→", "new": "🆕"}.get(t["trend"], "·")
        lines.append(f"- {icon} **{t['method']}**: total {t['total']} papers, {t['trend']}")
    return "\n".join(lines)


# --------------- CLI ---------------

def main():
    parser = argparse.ArgumentParser(
        prog="analyze_methods.py",
        description="ResearchX — method mining & trend analysis over a paper set (stdlib only)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Input: JSON array of {title, year, journal, method, result, limitation, dataset, innovation}",
    )
    parser.add_argument("--input", "-i", required=True, help="JSON paper set (see the format below)")
    parser.add_argument("--out", "-o", default=None, help="write the report here (default: stdout)")
    parser.add_argument("--format", "-f", choices=["json", "md", "markdown"], default="md",
                        help="md (default) or json")
    parser.add_argument("--quiet", "-q", action="store_true", help="suppress the summary line")
    args = parser.parse_args()

    if not Path(args.input).exists():
        print(f"error: input file not found: {args.input}", file=sys.stderr)
        return 2

    papers = load_papers(args.input)
    if not papers:
        print("error: no paper records in the input file", file=sys.stderr)
        return 3

    report = generate_report(papers)
    summary = report["summary"]

    output = format_markdown(report) if args.format in ("md", "markdown") else json.dumps(
        report, ensure_ascii=False, indent=2
    )

    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(output + "\n", encoding="utf-8")
        if not args.quiet:
            print(f"report written to {args.out}", file=sys.stderr)
    else:
        print(output)

    if not args.quiet:
        print("# ResearchX method analysis", file=sys.stderr)
        print(f"#   papers:   {summary['total_papers']}", file=sys.stderr)
        print(f"#   methods:  {summary['unique_methods']}", file=sys.stderr)
        print(f"#   trends:   {', '.join(summary['emerging_trends'][:3]) or '-'}", file=sys.stderr)
        print(f"#   gaps:     {', '.join(summary['critical_gaps'][:3]) or '-'}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
