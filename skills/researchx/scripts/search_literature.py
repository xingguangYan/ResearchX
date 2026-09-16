#!/usr/bin/env python3
"""ResearchX — structured literature search across OpenAlex, Crossref and arXiv.

Returns real records with DOIs instead of prose, so method landscapes and literature
matrices are built from retrievable metadata (and can be re-run identically later).

Modes
-----
  keyword      --query "crop mapping foundation model" --from-year 2023
  forward      --cited-by 10.1016/j.rse.2024.114123      (works that cite it)
  backward     --references-of 10.1016/j.rse.2024.114123 (works it cites)

Examples
--------
  python scripts/search_literature.py --query "remote sensing foundation model" --from-year 2023 --limit 25
  python scripts/search_literature.py --query "crop mapping" --query "yield prediction" --format json --out hits.json
  python scripts/search_literature.py --cited-by 10.1038/s41586-023-06221-2 --limit 40 --format md

Options
-------
  --query TEXT            keyword query (repeatable; results are merged and deduped)
  --cited-by DOI          forward citation chaining
  --references-of DOI     backward citation chaining
  --from-year INT         include works published in or after this year
  --to-year INT           include works published in or before this year
  --limit INT             max records per query (default 25, applies per source query)
  --source LIST           openalex,crossref,arxiv (default openalex,crossref)
  --min-citations INT     drop records below this citation count
  --open-access-only      keep only open-access records (OpenAlex data)
  --sort LIST             relevance,citations,year (default citations for chaining, year otherwise)
  --dedupe / --no-dedupe  merge duplicates by DOI/title (default on)
  --format md|json|csv    output format (default md)
  --out PATH              write to a file instead of stdout
  --abstracts             include abstracts in JSON output (truncated to 700 chars)
  --offline               use only cached responses
  --cache-dir PATH        cache location (default .researchx-cache)
  --mailto EMAIL          polite-pool contact (or set RESEARCHX_MAILTO)
  --timeout SECONDS       per-request timeout (default 20)
  --quiet                 suppress progress output
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))

import rx_common as rx  # noqa: E402


def invert_abstract(inverted: Optional[Dict[str, List[int]]]) -> str:
    if not inverted:
        return ""
    positions: List[tuple] = []
    for word, index_list in inverted.items():
        for position in index_list:
            positions.append((position, word))
    positions.sort()
    return " ".join(word for _, word in positions)


def openalex_query(
    net: rx.Net,
    query: str,
    from_year: Optional[int],
    to_year: Optional[int],
    limit: int,
    sort: str,
) -> List[Dict[str, Any]]:
    filters = []
    if from_year:
        filters.append(f"from_publication_date:{from_year}-01-01")
    if to_year:
        filters.append(f"to_publication_date:{to_year}-12-31")
    params: Dict[str, Any] = {
        "search": query,
        "per-page": min(200, max(1, limit)),
    }
    if filters:
        params["filter"] = ",".join(filters)
    if sort == "citations":
        params["sort"] = "cited_by_count:desc"
    elif sort == "year":
        params["sort"] = "publication_date:desc"
    if net.mailto:
        params["mailto"] = net.mailto
    body, error = net.get_json("https://api.openalex.org/works", params)
    if error or not body:
        return []
    records = []
    for work in body.get("results") or []:
        record = rx.from_openalex(work)
        record["open_access"] = bool((work.get("open_access") or {}).get("is_oa"))
        record["abstract"] = invert_abstract(work.get("abstract_inverted_index"))
        record["score"] = work.get("relevance_score")
        records.append(record)
    return records


def openalex_chained(
    net: rx.Net, anchor_doi: str, direction: str, limit: int, from_year: Optional[int], to_year: Optional[int]
) -> List[Dict[str, Any]]:
    anchor, error = net.get_json(
        f"https://api.openalex.org/works/doi:{rx.urllib.parse.quote(anchor_doi)}",
        {"mailto": net.mailto} if net.mailto else None,
    )
    if error or not isinstance(anchor, dict):
        return []
    anchor_id = (anchor.get("id") or "").rsplit("/", 1)[-1]
    if not anchor_id:
        return []
    filters = [f"cites:{anchor_id}" if direction == "cited-by" else f"cited_by:{anchor_id}"]
    if from_year:
        filters.append(f"from_publication_date:{from_year}-01-01")
    if to_year:
        filters.append(f"to_publication_date:{to_year}-12-31")
    params: Dict[str, Any] = {
        "filter": ",".join(filters),
        "per-page": min(200, max(1, limit)),
        "sort": "cited_by_count:desc",
    }
    if net.mailto:
        params["mailto"] = net.mailto
    body, error = net.get_json("https://api.openalex.org/works", params)
    if error or not body:
        return []
    records = []
    for work in body.get("results") or []:
        record = rx.from_openalex(work)
        record["open_access"] = bool((work.get("open_access") or {}).get("is_oa"))
        record["abstract"] = invert_abstract(work.get("abstract_inverted_index"))
        record["chained_from"] = anchor_doi
        record["chained_direction"] = direction
        records.append(record)
    return records


def crossref_query(
    net: rx.Net,
    query: str,
    from_year: Optional[int],
    to_year: Optional[int],
    limit: int,
    sort: str,
) -> List[Dict[str, Any]]:
    params: Dict[str, Any] = {
        "query.bibliographic": query,
        "rows": min(100, max(1, limit)),
        "select": "DOI,title,author,issued,container-title,type,is-referenced-by-count,abstract",
    }
    filters = []
    if from_year:
        filters.append(f"from-pub-date:{from_year}-01-01")
    if to_year:
        filters.append(f"until-pub-date:{to_year}-12-31")
    if filters:
        params["filter"] = ",".join(filters)
    if sort == "citations":
        params["sort"] = "is-referenced-by-count"
        params["order"] = "desc"
    elif sort == "year":
        params["sort"] = "published"
        params["order"] = "desc"
    if net.mailto:
        params["mailto"] = net.mailto
    body, error = net.get_json("https://api.crossref.org/works", params)
    if error or not body:
        return []
    records = []
    for item in (body.get("message") or {}).get("items") or []:
        record = rx.from_crossref(item)
        record["open_access"] = None
        abstract = item.get("abstract") or ""
        record["abstract"] = rx._SPACE.sub(" ", abstract)[:700] if abstract else ""
        records.append(record)
    return records


def arxiv_query(net: rx.Net, query: str, limit: int) -> List[Dict[str, Any]]:
    text, error = net.get_text(
        "https://export.arxiv.org/api/query",
        {"search_query": f"all:{query}", "start": 0, "max_results": min(100, limit)},
    )
    if error or not text:
        return []
    import xml.etree.ElementTree as ET

    ns = {"a": "http://www.w3.org/2005/Atom"}
    try:
        root = ET.fromstring(text)
    except ET.ParseError:
        return []
    records = []
    for entry in root.findall("a:entry", ns):
        record = rx.from_arxiv(
            {
                "id": (entry.findtext("a:id", default="", namespaces=ns) or "").strip(),
                "title": rx._SPACE.sub(
                    " ", (entry.findtext("a:title", default="", namespaces=ns) or "").strip()
                ),
                "published": (entry.findtext("a:published", default="", namespaces=ns) or "").strip(),
                "authors": [
                    (a.findtext("a:name", default="", namespaces=ns) or "")
                    for a in entry.findall("a:author", ns)
                ],
            }
        )
        record["abstract"] = rx._SPACE.sub(
            " ", (entry.findtext("a:summary", default="", namespaces=ns) or "").strip()
        )[:700]
        record["open_access"] = True
        records.append(record)
    return records


def dedupe(records: List[Dict[str, Any]], threshold: float = 0.92) -> List[Dict[str, Any]]:
    kept: List[Dict[str, Any]] = []
    seen_dois = set()
    for record in records:
        doi = (record.get("doi") or "").lower()
        if doi and doi in seen_dois:
            continue
        duplicate = False
        for existing in kept:
            if rx.title_similarity(record.get("title"), existing.get("title")) >= threshold:
                duplicate = True
                break
        if duplicate:
            continue
        if doi:
            seen_dois.add(doi)
        kept.append(record)
    return kept


def enrich_sources(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    for record in records:
        if not record.get("url") and record.get("doi"):
            record["url"] = f"https://doi.org/{record['doi']}"
    return records


def render_markdown(records: List[Dict[str, Any]], meta: Dict[str, Any]) -> str:
    out = [
        "# Literature Search",
        "",
        f"- Query: {meta.get('query')}",
        f"- Registries: {', '.join(meta.get('sources', []))}",
        f"- Window: {meta.get('from_year') or 'any'}–{meta.get('to_year') or 'any'}",
        f"- Retrieved: {meta.get('retrieved')} records → {len(records)} unique after dedupe",
        f"- Run: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "| # | Title | Year | Venue | Cites | DOI | OA |",
        "|---|-------|------|-------|------:|-----|----|",
    ]
    for index, record in enumerate(records, 1):
        title = (record.get("title") or "Untitled").replace("|", "/")
        venue = (record.get("venue") or "-").replace("|", "/")
        doi = record.get("doi") or ""
        doi_cell = f"[{doi}](https://doi.org/{doi})" if doi else (record.get("url") or "-")
        open_access = {True: "yes", False: "no", None: "?"}.get(record.get("open_access"), "?")
        out.append(
            f"| {index} | {title} | {record.get('year') or '-'} | {venue} | "
            f"{record.get('cited_by') if record.get('cited_by') is not None else '-'} | {doi_cell} | {open_access} |"
        )
    out += [
        "",
        "## How to use this",
        "",
        "1. Screen the table against your inclusion criteria (or feed the JSON into `prisma_screen.py`).",
        "2. Verify anything you intend to cite: `python scripts/verify_citations.py hits.json --format md`.",
        "3. Cite the DOI, and re-run the same command later to update the landscape.",
        "",
    ]
    return "\n".join(out)


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="search_literature.py",
        description="Structured literature search (OpenAlex/Crossref/arXiv) with citation chaining.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--query", "-q", action="append", default=[], help="keyword query (repeatable)")
    parser.add_argument("--cited-by", default=None, help="forward chaining: works citing this DOI")
    parser.add_argument("--references-of", default=None, help="backward chaining: works cited by this DOI")
    parser.add_argument("--from-year", type=int, default=None)
    parser.add_argument("--to-year", type=int, default=None)
    parser.add_argument("--limit", type=int, default=25)
    parser.add_argument("--source", default="openalex,crossref", help="comma-separated: openalex,crossref,arxiv")
    parser.add_argument("--min-citations", type=int, default=None)
    parser.add_argument("--open-access-only", action="store_true")
    parser.add_argument("--sort", choices=["relevance", "citations", "year"], default=None)
    parser.add_argument("--dedupe", dest="dedupe", action="store_true", default=True)
    parser.add_argument("--no-dedupe", dest="dedupe", action="store_false")
    parser.add_argument("--format", "-f", choices=["md", "json", "csv"], default="md")
    parser.add_argument("--out", "-o", default=None)
    parser.add_argument("--abstracts", action="store_true", help="include abstracts in JSON output")
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--cache-dir", default=rx.DEFAULT_CACHE_DIR)
    parser.add_argument("--mailto", default=rx.env_mailto())
    parser.add_argument("--timeout", type=float, default=rx.DEFAULT_TIMEOUT)
    parser.add_argument("--sleep", type=float, default=0.0)
    parser.add_argument("--quiet", action="store_true")
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    if not args.query and not args.cited_by and not args.references_of:
        print("Pass --query, --cited-by or --references-of (see --help).", file=sys.stderr)
        return 2

    sources = [s.strip().lower() for s in args.source.split(",") if s.strip()]
    sort = args.sort or ("citations" if (args.cited_by or args.references_of) else "year")
    net = rx.Net(
        cache_dir=args.cache_dir,
        offline=args.offline,
        timeout=args.timeout,
        mailto=args.mailto,
        sleep=args.sleep,
    )

    records: List[Dict[str, Any]] = []
    jobs = len(args.query) + (1 if args.cited_by else 0) + (1 if args.references_of else 0)
    done = 0
    for query in args.query:
        for source in sources:
            if source == "openalex":
                records += openalex_query(net, query, args.from_year, args.to_year, args.limit, sort)
            elif source == "crossref":
                records += crossref_query(net, query, args.from_year, args.to_year, args.limit, sort)
            elif source == "arxiv":
                records += arxiv_query(net, query, args.limit)
            done += 1
            if not args.quiet:
                print(f"[{done}/{jobs}] {source}: {query}", file=sys.stderr)
    anchor = args.cited_by or args.references_of
    if anchor:
        direction = "cited-by" if args.cited_by else "references-of"
        records += openalex_chained(net, anchor, direction, args.limit, args.from_year, args.to_year)
        if not args.quiet:
            print(f"[{done + 1}/{jobs}] openalex: {direction} {anchor}", file=sys.stderr)

    retrieved = len(records)
    if args.min_citations is not None:
        records = [r for r in records if (r.get("cited_by") or 0) >= args.min_citations]
    if args.open_access_only:
        records = [r for r in records if r.get("open_access")]
    if args.dedupe:
        records = dedupe(records)
    records = enrich_sources(records)
    if sort == "citations":
        records.sort(key=lambda r: -(r.get("cited_by") or 0))
    elif sort == "year":
        records.sort(key=lambda r: -(int(r.get("year") or 0) if str(r.get("year") or "").isdigit() else 0))

    meta = {
        "query": " | ".join(args.query) or (f"{'cited-by' if args.cited_by else 'references-of'} {anchor}"),
        "sources": sources,
        "from_year": args.from_year,
        "to_year": args.to_year,
        "retrieved": retrieved,
        "unique": len(records),
        "sort": sort,
        "generated": datetime.now().isoformat(timespec="seconds"),
    }

    if args.format == "json":
        payload = dict(meta)
        payload["results"] = [
            {k: v for k, v in record.items() if k != "abstract" or args.abstracts} for record in records
        ]
        output = json.dumps(payload, ensure_ascii=False, indent=2)
    elif args.format == "csv":
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(["title", "year", "venue", "doi", "authors", "cited_by", "open_access", "url"])
        for record in records:
            writer.writerow(
                [
                    record.get("title"),
                    record.get("year"),
                    record.get("venue"),
                    record.get("doi"),
                    "; ".join(record.get("authors") or []),
                    record.get("cited_by"),
                    record.get("open_access"),
                    record.get("url"),
                ]
            )
        output = buffer.getvalue()
    else:
        output = render_markdown(records, meta)

    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(output + "\n", encoding="utf-8")
        if not args.quiet:
            print(f"{len(records)} records written to {args.out}", file=sys.stderr)
    else:
        print(output)

    if not records:
        return 3  # nothing retrievable: caller must say so instead of inventing results
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
