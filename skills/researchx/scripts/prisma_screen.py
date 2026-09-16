#!/usr/bin/env python3
"""ResearchX — reproducible screening for literature/systematic reviews (PRISMA 2020).

Turns a raw hit list into an auditable screening ledger plus PRISMA counts and a
flow diagram. Screening decisions are rule-based first, human decisions second:
every inclusion/exclusion records *why*, so the review can be reproduced and the
PRISMA numbers can be regenerated instead of hand-counted.

Stages
------
  1. identification  records as retrieved, per source
  2. deduplication   DOI match, then title similarity >= --title-threshold
  3. screening       --include / --exclude regex rules, year window, type filter
  4. eligibility     your --decisions file (JSON: id -> {decision, reason})
  5. included        final set, written out for extraction

Examples
--------
  python scripts/prisma_screen.py --input hits.json --include "crop|yield" --exclude "review|editorial"
  python scripts/prisma_screen.py --input hits.json --decisions decisions.json --out-prefix review1
  python scripts/prisma_screen.py --input hits.csv --from-year 2020 --include "remote sensing" --format json

Options
-------
  --input PATH            hits from search_literature.py (.json, .csv) or a list of dicts
  --include REGEX         keep records matching any pattern (repeatable, case-insensitive)
  --exclude REGEX         drop records matching any pattern (repeatable)
  --from-year / --to-year publication window
  --type LIST             keep only these record types (e.g. article,review)
  --title-threshold FLOAT dedupe similarity (default 0.92)
  --decisions PATH        JSON {record_id: {"decision": "include|exclude", "reason": "..."}}
  --out-prefix PATH       prefix for outputs (default: prisma)
  --format md|json|text   stdout format (default md)
  --max-reasons INT       keep this many example reasons per exclusion bucket (default 5)

Outputs (when --out-prefix is used)
  <prefix>_flow.md            PRISMA 2020 flow diagram (Mermaid) + counts
  <prefix>_ledger.csv         one row per record with stage, decision and reason
  <prefix>_counts.json        machine-readable PRISMA numbers
  <prefix>_included.json      the final included set (input for extraction)
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))

import rx_common as rx  # noqa: E402


def load_records(path: str) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
    """Return (records, per-source identification counts)."""
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    records: List[Dict[str, Any]] = []
    if path.lower().endswith(".csv"):
        for row in csv.DictReader(text.splitlines()):
            records.append(
                {
                    "id": row.get("doi") or row.get("title"),
                    "title": row.get("title"),
                    "doi": (row.get("doi") or "").strip() or None,
                    "year": (row.get("year") or "").strip() or None,
                    "venue": row.get("venue"),
                    "source": row.get("source") or "csv",
                    "type": row.get("type"),
                    "abstract": row.get("abstract") or "",
                    "authors": [a for a in re.split(r"\s*;\s*", row.get("authors") or "") if a],
                }
            )
    else:
        data = json.loads(text)
        if isinstance(data, dict):
            records = data.get("results") or data.get("records") or data.get("references") or []
        else:
            records = data
    normalised = []
    for index, record in enumerate(records, 1):
        if not isinstance(record, dict):
            continue
        authors = record.get("authors")
        if isinstance(authors, str):
            authors = [a for a in re.split(r"\s*(?:;|, and | and |&)\s*", authors) if a]
        record = dict(record)
        record["authors"] = authors or []
        record.setdefault("source", record.get("registry") or "unknown")
        record["id"] = str(
            record.get("id") or record.get("doi") or record.get("title") or f"record-{index}"
        )
        normalised.append(record)
    counts: Dict[str, int] = {}
    for record in normalised:
        counts[record["source"]] = counts.get(record["source"], 0) + 1
    return normalised, counts


def match_any(patterns: List[str], text: str) -> Optional[str]:
    for pattern in patterns:
        if re.search(pattern, text, re.I):
            return pattern
    return None


def rule_stage(
    records: List[Dict[str, Any]],
    include: List[str],
    exclude: List[str],
    from_year: Optional[int],
    to_year: Optional[int],
    types: List[str],
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Returns (included, excluded, undecided)."""
    kept, excluded, undecided = [], [], []
    for record in records:
        blob = " ".join(
            str(record.get(field) or "")
            for field in ("title", "abstract", "venue", "keywords", "type")
        )
        year = None
        try:
            year = int(str(record.get("year"))[:4])
        except (TypeError, ValueError):
            year = None
        if from_year and year and year < from_year:
            excluded.append({**record, "reason": f"published before {from_year}", "rule": "year"})
            continue
        if to_year and year and year > to_year:
            excluded.append({**record, "reason": f"published after {to_year}", "rule": "year"})
            continue
        hit = match_any(exclude, blob)
        if hit:
            excluded.append({**record, "reason": f"excluded by pattern /{hit}/", "rule": "exclude"})
            continue
        if types:
            record_type = str(record.get("type") or "").lower()
            if record_type and not any(t.lower() in record_type for t in types):
                excluded.append({**record, "reason": f"type '{record_type}' not in {types}", "rule": "type"})
                continue
        if include:
            if match_any(include, blob):
                kept.append(record)
            else:
                undecided.append(
                    {**record, "reason": "no inclusion criterion matched — human screen needed", "rule": "include"}
                )
        else:
            kept.append(record)
    return kept, excluded, undecided


def apply_decisions(
    records: List[Dict[str, Any]], decisions: Dict[str, Any]
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    included, excluded = [], []
    for record in records:
        decision = decisions.get(record["id"]) or decisions.get(str(record.get("doi"))) or {}
        verdict = str(decision.get("decision", "")).lower()
        if verdict.startswith("incl"):
            included.append({**record, "reason": decision.get("reason", "included at eligibility")})
        elif verdict.startswith("excl"):
            excluded.append(
                {**record, "reason": decision.get("reason", "excluded at eligibility"), "rule": "eligibility"}
            )
        elif record.get("_rule_included"):
            included.append({**record, "reason": "passed title/abstract screening rules"})
        else:
            included.append({**record, "reason": "human decision pending — provisionally included"})
    return included, excluded


def build_counts(
    identified: Dict[str, int],
    duplicates: List[Dict[str, Any]],
    screened: int,
    excluded_rules: List[Dict[str, Any]],
    undecided: List[Dict[str, Any]],
    eligibility_excluded: List[Dict[str, Any]],
    included: List[Dict[str, Any]],
    assessed: int = 0,
) -> Dict[str, Any]:
    rule_buckets: Dict[str, int] = {}
    for record in excluded_rules:
        rule_buckets[record.get("rule", "rule")] = rule_buckets.get(record.get("rule", "rule"), 0) + 1
    return {
        "identified_total": sum(identified.values()),
        "identified_by_source": identified,
        "duplicates_removed": len(duplicates),
        "records_screened": screened,
        "records_excluded_at_screening": len(excluded_rules) + len(undecided),
        "excluded_by_rule": rule_buckets,
        "awaiting_human_screen": len(undecided),
        "assessed_for_eligibility": assessed or len(undecided),
        "excluded_at_eligibility": len(eligibility_excluded),
        "included": len(included),
        "generated": datetime.now().isoformat(timespec="seconds"),
    }


def render_flow(counts: Dict[str, Any], examples: Dict[str, List[str]]) -> str:
    identified = counts["identified_total"]
    duplicates = counts["duplicates_removed"]
    screened = counts["records_screened"]
    excluded = counts["records_excluded_at_screening"]
    eligibility = counts["assessed_for_eligibility"]
    eligibility_excluded = counts["excluded_at_eligibility"]
    included = counts["included"]
    source_rows = "\n".join(
        f"      S{i}[\"{name}: n = {value}\"]" for i, (name, value) in enumerate(counts["identified_by_source"].items())
    )
    reason_rows = "\n".join(
        f"      R{i}[\"{reason}: n = {value}\"]" for i, (reason, value) in enumerate(examples.items())
    )
    return f"""# PRISMA 2020 flow — generated

```mermaid
flowchart TD
  subgraph IDENT["Identification"]
{source_rows or '      S0["no source metadata"]'}
      Q["Records identified: n = {identified}"]
  end
  subgraph SCREEN["Screening"]
      D["Duplicates removed: n = {duplicates}"]
      T["Records screened (title/abstract): n = {screened}"]
      E["Records excluded: n = {excluded}"]
{reason_rows}
      F["Reports sought for retrieval: n = {eligibility}"]
  end
  subgraph ELIG["Eligibility"]
      G["Reports assessed for eligibility: n = {eligibility}"]
      H["Reports excluded at eligibility: n = {eligibility_excluded}"]
  end
  subgraph INCL["Included"]
      I["Studies included in synthesis: n = {included}"]
  end
  S0 --> Q
  Q --> D --> T
  T --> E
  T --> F --> G
  G --> H
  G --> I
```

## Counts

| Stage | n |
|-------|---:|
| Records identified | {identified} |
| Duplicates removed | {duplicates} |
| Records screened | {screened} |
| Excluded at title/abstract | {excluded} |
| Assessed for eligibility | {eligibility} |
| Excluded at eligibility | {eligibility_excluded} |
| **Included in synthesis** | **{included}** |

## Reproducibility note

Record the search strings, registries, date of search and the exact command you ran here:

```
python scripts/search_literature.py --query "..." --from-year {datetime.now().year - 3} --format json --out hits.json
python scripts/prisma_screen.py --input hits.json --include "..." --exclude "..."
```

If an LLM assisted the screening, disclose it (PRISMA-trAIce): which stages were automated,
which model/tool, how many records it touched, and how a human verified a sample.
"""


def render_markdown(counts: Dict[str, Any], examples: Dict[str, List[str]], files: Dict[str, str]) -> str:
    lines = [
        "# PRISMA screening summary",
        "",
        f"- Records identified: **{counts['identified_total']}** "
        f"({', '.join(f'{k}: {v}' for k, v in counts['identified_by_source'].items())})",
        f"- Duplicates removed: **{counts['duplicates_removed']}**",
        f"- Screened: **{counts['records_screened']}** → excluded **{counts['records_excluded_at_screening']}**",
        f"- Awaiting human screen: **{counts['awaiting_human_screen']}**",
        f"- Excluded at eligibility: **{counts['excluded_at_eligibility']}**",
        f"- Included: **{counts['included']}**",
        "",
    ]
    if examples:
        lines += ["## Exclusion reasons (examples)", ""]
        for reason, items in examples.items():
            lines.append(f"- **{reason}**")
            for item in items:
                lines.append(f"  - {item}")
        lines.append("")
    if files:
        lines += ["## Files", ""]
        for label, path in files.items():
            lines.append(f"- {label}: `{path}`")
        lines.append("")
    return "\n".join(lines)


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="prisma_screen.py",
        description="Reproducible screening + PRISMA 2020 counts for a review.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--input", "-i", required=True, help="hits JSON/CSV from search_literature.py")
    parser.add_argument("--include", action="append", default=[], help="regex that keeps a record (repeatable)")
    parser.add_argument("--exclude", action="append", default=[], help="regex that drops a record (repeatable)")
    parser.add_argument("--from-year", type=int, default=None)
    parser.add_argument("--to-year", type=int, default=None)
    parser.add_argument("--type", default="", help="comma-separated record types to keep")
    parser.add_argument("--title-threshold", type=float, default=0.92)
    parser.add_argument("--decisions", default=None, help="JSON {id: {decision, reason}}")
    parser.add_argument("--out-prefix", default=None, help="prefix for flow/ledger/counts outputs")
    parser.add_argument("--format", "-f", choices=["md", "json", "text"], default="md")
    parser.add_argument("--max-reasons", type=int, default=5)
    parser.add_argument("--quiet", action="store_true")
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    if not Path(args.input).exists():
        print(f"input not found: {args.input}", file=sys.stderr)
        return 2
    try:
        records, identified = load_records(args.input)
    except (json.JSONDecodeError, OSError) as exc:
        print(f"could not read {args.input}: {exc}", file=sys.stderr)
        return 2
    if not records:
        print("no records in input — nothing to screen", file=sys.stderr)
        return 3

    # stage 2 — dedupe
    seen_dois, unique, duplicates = set(), [], []
    for record in records:
        doi = (record.get("doi") or "").lower()
        if doi and doi in seen_dois:
            duplicates.append({**record, "reason": f"duplicate DOI {doi}", "rule": "duplicate"})
            continue
        twin = next(
            (
                existing
                for existing in unique
                if rx.title_similarity(record.get("title"), existing.get("title")) >= args.title_threshold
            ),
            None,
        )
        if twin is not None:
            duplicates.append(
                {
                    **record,
                    "reason": f"title duplicate of '{str(twin.get('title'))[:80]}'",
                    "rule": "duplicate",
                }
            )
            continue
        if doi:
            seen_dois.add(doi)
        unique.append(record)

    # stage 3 — rules
    kept, excluded_rules, undecided = rule_stage(
        unique,
        args.include,
        args.exclude,
        args.from_year,
        args.to_year,
        [t.strip() for t in args.type.split(",") if t.strip()],
    )

    # stage 4 — human decisions
    decisions = {}
    if args.decisions:
        try:
            decisions = json.loads(Path(args.decisions).read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            print(f"could not read decisions file: {exc}", file=sys.stderr)
            return 2
    pool = [{**record, "_rule_included": True} for record in kept] + [
        {**record, "_rule_included": False} for record in undecided
    ]
    included, eligibility_excluded = apply_decisions(pool, decisions)
    included = [{k: v for k, v in record.items() if k != "_rule_included"} for record in included]

    counts = build_counts(
        identified, duplicates, len(unique), excluded_rules, undecided, eligibility_excluded, included,
        assessed=len(kept) + len(undecided),
    )
    examples: Dict[str, List[str]] = {}
    for record in (excluded_rules + duplicates + eligibility_excluded):
        bucket = record.get("reason", "other")
        examples.setdefault(bucket, [])
        if len(examples[bucket]) < args.max_reasons:
            examples[bucket].append(str(record.get("title") or record.get("id"))[:120])

    files: Dict[str, str] = {}
    if args.out_prefix:
        prefix = Path(args.out_prefix)
        prefix.parent.mkdir(parents=True, exist_ok=True)
        flow_path = Path(f"{prefix}_flow.md")
        ledger_path = Path(f"{prefix}_ledger.csv")
        counts_path = Path(f"{prefix}_counts.json")
        included_path = Path(f"{prefix}_included.json")

        flow_path.write_text(render_flow(counts, examples) + "\n", encoding="utf-8")
        counts_path.write_text(json.dumps(counts, ensure_ascii=False, indent=2), encoding="utf-8")
        included_path.write_text(
            json.dumps({"counts": counts, "results": included}, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        with ledger_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(["id", "title", "year", "doi", "source", "stage", "decision", "reason"])
            for record in duplicates:
                writer.writerow([record["id"], record.get("title"), record.get("year"), record.get("doi"),
                                 record.get("source"), "deduplication", "exclude", record.get("reason")])
            for record in excluded_rules:
                writer.writerow([record["id"], record.get("title"), record.get("year"), record.get("doi"),
                                 record.get("source"), "title/abstract", "exclude", record.get("reason")])
            for record in undecided:
                writer.writerow([record["id"], record.get("title"), record.get("year"), record.get("doi"),
                                 record.get("source"), "eligibility", "pending-human", record.get("reason")])
            for record in eligibility_excluded:
                writer.writerow([record["id"], record.get("title"), record.get("year"), record.get("doi"),
                                 record.get("source"), "eligibility", "exclude", record.get("reason")])
            for record in included:
                writer.writerow([record["id"], record.get("title"), record.get("year"), record.get("doi"),
                                 record.get("source"), "included", "include", record.get("reason", "")])
        files = {
            "PRISMA flow": str(flow_path),
            "screening ledger": str(ledger_path),
            "counts": str(counts_path),
            "included set": str(included_path),
        }

    if args.format == "json":
        print(json.dumps({"counts": counts, "examples": examples, "files": files}, ensure_ascii=False, indent=2))
    elif args.format == "text":
        print(
            f"identified={counts['identified_total']} duplicates={counts['duplicates_removed']} "
            f"screened={counts['records_screened']} excluded={counts['records_excluded_at_screening']} "
            f"pending={counts['awaiting_human_screen']} included={counts['included']}"
        )
    else:
        print(render_markdown(counts, examples, files))

    if not args.quiet and args.out_prefix:
        print(f"wrote {args.out_prefix}_flow.md / _ledger.csv / _counts.json / _included.json", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
