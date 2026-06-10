"""ResearchX — Literature Search & Method Analysis Tool

This script helps process structured literature data obtained via web_search.
It does NOT perform web searches itself (use the SKILL.md workflow for that).
Instead, it takes raw literature search results and produces structured analysis.

Usage:
    python scripts/analyze_methods.py --input <json-file> [--output <json-file>]

Input format: Array of paper objects with {title, year, journal, method, result, limitation}
Output format: Method taxonomy, trend analysis, gap report
"""

import json
import sys
import argparse
from pathlib import Path
from collections import defaultdict


def load_papers(input_path: str) -> list:
    """Load paper data from JSON file."""
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, list) else [data]


def classify_years(papers: list) -> dict:
    """Group papers by publication year."""
    by_year = defaultdict(list)
    for p in papers:
        year = p.get("year", "unknown")
        by_year[str(year)].append(p)
    return dict(by_year)


def extract_method_families(papers: list) -> dict:
    """Extract and categorize method families from papers.

    Each paper should have a "method" field describing the approach.
    Returns a dict of method_family -> [paper_titles].
    """
    families = defaultdict(list)
    for p in papers:
        method = p.get("method", "").strip()
        if not method:
            continue
        # Simple family extraction: take the first noun phrase or key tech name
        # In practice, this would use NLP; for CLI we use the raw method string
        families[method].append(p.get("title", "Untitled"))
    return dict(families)


def compute_trend_scores(by_year: dict) -> list:
    """Compute which methods are trending (increasing) vs declining."""
    method_year_count = defaultdict(lambda: defaultdict(int))
    for year, papers in by_year.items():
        for p in papers:
            method = p.get("method", "unknown")
            method_year_count[method][year] += 1

    trends = []
    for method, year_counts in method_year_count.items():
        years = sorted(year_counts.keys())
        if len(years) >= 2:
            first_half = sum(year_counts[y] for y in years[: len(years) // 2])
            second_half = sum(year_counts[y] for y in years[len(years) // 2 :])
            trend = "emerging" if second_half > first_half else "declining"
        else:
            trend = "stable"
        trends.append({"method": method, "year_counts": dict(year_counts), "trend": trend})
    return trends


def identify_gaps(papers: list) -> dict:
    """Extract reported limitations and unsolved problems as research gaps."""
    all_limitations = []
    for p in papers:
        limitation = p.get("limitation", "").strip()
        if limitation:
            all_limitations.append({"paper": p.get("title", ""), "limitation": limitation})

    # Count common limitation themes
    limitation_keywords = defaultdict(int)
    for item in all_limitations:
        lim = item["limitation"].lower()
        for keyword in [
            "generalization",
            "generalisation",
            "scalability",
            "robustness",
            "interpretability",
            "data scarcity",
            "labeled data",
            "computational cost",
            "transferability",
            "domain shift",
            "class imbalance",
            "noise",
            "resolution",
            "temporal",
            "spatial",
            "multi-source",
            "fusion",
        ]:
            if keyword in lim:
                limitation_keywords[keyword] += 1

    sorted_gaps = sorted(limitation_keywords.items(), key=lambda x: -x[1])
    return {
        "total_limitations": len(all_limitations),
        "top_gaps": [{"gap": k, "frequency": v} for k, v in sorted_gaps[:10]],
        "detailed_limitations": all_limitations,
    }


def generate_report(papers: list) -> dict:
    """Generate comprehensive analysis report."""
    by_year = classify_years(papers)
    method_families = extract_method_families(papers)
    trends = compute_trend_scores(by_year)
    gaps = identify_gaps(papers)

    report = {
        "total_papers": len(papers),
        "year_distribution": {k: len(v) for k, v in by_year.items()},
        "method_families": method_families,
        "method_trends": trends,
        "gaps": gaps,
        "summary": {
            "dominant_methods": list(method_families.keys())[:5],
            "emerging_trends": [t["method"] for t in trends if t["trend"] == "emerging"],
            "top_gaps": [g["gap"] for g in gaps["top_gaps"][:5]],
        },
    }
    return report


def main():
    parser = argparse.ArgumentParser(description="Analyze literature search results for method mining")
    parser.add_argument("--input", "-i", required=True, help="Input JSON file with paper data")
    parser.add_argument("--output", "-o", default="analysis_report.json", help="Output JSON file")
    args = parser.parse_args()

    if not Path(args.input).exists():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    papers = load_papers(args.input)
    report = generate_report(papers)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"=== ResearchX Method Analysis Report ===")
    print(f"Papers analyzed: {report['total_papers']}")
    print(f"Year range: {min(report['year_distribution'].keys())} - {max(report['year_distribution'].keys())}")
    print(f"Dominant methods: {', '.join(report['summary']['dominant_methods'])}")
    print(f"Emerging trends: {', '.join(report['summary']['emerging_trends'])}")
    print(f"Top gaps: {', '.join(report['summary']['top_gaps'])}")
    print(f"\nFull report saved to: {args.output}")


if __name__ == "__main__":
    main()
