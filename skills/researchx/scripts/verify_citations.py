#!/usr/bin/env python3
"""ResearchX — verify that every reference in a document is real.

Cross-checks each reference against Crossref, OpenAlex, arXiv and the DOI handle
service, then reports one verdict per reference:

  VERIFIED   found in a registry and the metadata matches
  CORRECTED  the work exists but the cited metadata drifted (year/journal/DOI/author)
  PARTIAL    plausible grey-literature match — confirm by hand
  NOT_FOUND  no registry match. NOT proof of fabrication (books, theses, brand-new or
             non-indexed venues) — it means "could not verify; treat as unverified"
  RETRACTED  the registry flags a retraction or withdrawal notice
  ERROR      the lookup itself failed (offline/timeout)

Exit codes: 0 = ran, 1 = --fail-on-unverified and problems were found,
            2 = usage/input error, 3 = every lookup failed (no verdicts available).

Examples
--------
  python scripts/verify_citations.py draft.md
  python scripts/verify_citations.py draft.md --format md --out citation_audit.md
  python scripts/verify_citations.py refs.bib --format json --fail-on-unverified
  python scripts/verify_citations.py --doi 10.1016/j.rse.2024.114123
  python scripts/verify_citations.py --title "Attention is all you need" --year 2017
  cat refs.txt | python scripts/verify_citations.py -

Options
-------
  --input PATH            document to audit (.md .txt .bib .json), or '-' for stdin
  --doi DOI               verify a single DOI (repeatable)
  --title TITLE           verify a single title (use with --author/--year)
  --author NAME           author hint for --title
  --year YEAR             year hint for --title
  --format md|json|text   report format (default: text summary + table)
  --out PATH              write the report to a file (default: stdout)
  --source LIST           crossref,openalex,arxiv,doi (default: all, in that order)
  --min-score FLOAT       title-similarity threshold for VERIFIED (default 0.80)
  --max-refs INT          stop after N references (default 60)
  --offline               use only cached responses (no network)
  --cache-dir PATH        cache location (default .researchx-cache)
  --timeout SECONDS       per-request timeout (default 20)
  --mailto EMAIL          polite-pool contact (or set RESEARCHX_MAILTO)
  --sleep SECONDS         delay between requests (be kind to registries)
  --fail-on-unverified    exit 1 when any reference is not VERIFIED
  --quiet                 suppress the progress line
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))

import rx_common as rx  # noqa: E402

STATUS_ORDER = [rx.RETRACTED, rx.ERROR, rx.NOT_FOUND, rx.PARTIAL, rx.CORRECTED, rx.VERIFIED]
STATUS_ICON = {
    rx.VERIFIED: "OK",
    rx.CORRECTED: "FIX",
    rx.PARTIAL: "CHECK",
    rx.NOT_FOUND: "UNVERIFIED",
    rx.RETRACTED: "RETRACTED",
    rx.ERROR: "ERROR",
}


# --------------------------------------------------------------------------- #
# Reference extraction                                                        #
# --------------------------------------------------------------------------- #


def blank_query(**overrides: Any) -> Dict[str, Any]:
    query = {
        "raw": "",
        "doi": None,
        "arxiv": None,
        "title": None,
        "surnames": [],
        "year": None,
        "venue": None,
    }
    query.update(overrides)
    return query


def guess_title(text: str) -> Optional[str]:
    """Best-effort title extraction from a bibliographic entry."""
    if not text:
        return None
    quoted = re.search(r"[\"\u201c\u201d\u2018\u2019']([^\"\u201c\u201d\u2018\u2019']{15,300})[\"\u201c\u201d\u2018\u2019']", text)
    if quoted:
        return quoted.group(1).strip(" .,")
    # "Authors (2024). Title. Venue" / "Authors, 2024. Title."
    after_year = re.search(r"\(\s*(?:19|20)\d{2}[a-z]?\s*\)[.\s]*([^.]{15,300})", text)
    if after_year:
        return after_year.group(1).strip(" .,")
    after_year2 = re.search(r"\b(?:19|20)\d{2}[a-z]?[.\s:)]+([^.]{15,300})", text)
    if after_year2:
        candidate = after_year2.group(1).strip(" .,")
        if not re.match(r"^(?:https?|doi|vol|pp|in\b)", candidate, re.I):
            return candidate
    # BibTeX-ish "Title of the work. Journal, 2024"
    first_sentence = re.split(r"(?<=[.?!])\s", text.strip())[0]
    if 20 <= len(first_sentence) <= 300 and not rx.find_dois(first_sentence):
        return first_sentence.strip(" .,")
    return None


def guess_surnames(text: str) -> List[str]:
    """Surnames from the leading author segment of an entry."""
    head = re.split(r"\(\s*(?:19|20)\d{2}", text)[0]
    if head == text:
        head = text[:120]
    if head.lower().startswith("http") or "arxiv" in head.lower():
        return []
    names = re.split(r"\s*(?:;|, and | and |&)\s*", head)
    out: List[str] = []
    for name in names:
        name = re.sub(r"^[\d\s\[\]().-]+", "", name).strip(" ,.")
        if not name or len(name) < 3:
            continue
        if "," in name:
            surname = name.split(",")[0]
        else:
            surname = name.split()[-1] if name.split() else name
        if surname and surname.lower() not in {"et", "al", "and", "the"}:
            out.append(surname)
    return out[:8]


SKIP_HEADER_RE = re.compile(
    r"^(?:#{1,6}\s*)?(?:references?|bibliography|literature\s+cited|works\s+cited|"
    r"citation(?:s)?|引用文献|参考文献(?:列表)?)\s*:?\s*$",
    re.I,
)


def looks_like_reference(entry: str) -> bool:
    """Reject headings, prose sentences and other non-bibliographic noise."""
    text = entry.strip()
    if len(text) < 25 or SKIP_HEADER_RE.match(text):
        return False
    if rx.find_dois(text) or rx.ARXIV_RE.search(text):
        return True
    if rx.YEAR_RE.search(text) and re.search(r"\(\s*(?:19|20)\d{2}|[,.]\s*(?:19|20)\d{2}", text):
        return True
    return len(text) >= 80


def parse_plain_entries(text: str) -> List[str]:
    lines = [line.rstrip() for line in text.splitlines()]
    entries, current = [], []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if current:
                entries.append(" ".join(current))
                current = []
            continue
        if SKIP_HEADER_RE.match(stripped):
            if current:
                entries.append(" ".join(current))
                current = []
            continue
        if re.match(r"^(?:\[\d+\]|\d+[.)]|[-*]\s+\[?\d*\]?)\s+\S", stripped) and current:
            entries.append(" ".join(current))
            current = [re.sub(r"^(?:\[\d+\]|\d+[.)]|[-*])\s*", "", stripped)]
            continue
        current.append(stripped)
    if current:
        entries.append(" ".join(current))

    # Fall back to one entry per line when paragraph splitting found nothing useful.
    if len(entries) <= 1 and len(lines) > 3:
        entries = [line.strip() for line in lines if len(line.strip()) > 40]
    return [entry for entry in entries if looks_like_reference(entry)]


def parse_bib(text: str) -> List[Dict[str, Any]]:
    refs: List[Dict[str, Any]] = []
    for block in re.findall(r"@\w+\s*\{[^@]*", text):
        fields: Dict[str, str] = {}
        for field in ("title", "author", "year", "journal", "booktitle", "doi", "eprint", "url", "date"):
            match = re.search(
                rf"\b{field}\s*=\s*[\{{\"](.+?)[\}}\"]\s*,?\s*\n", block + "\n", re.S | re.I
            )
            if match:
                fields[field] = re.sub(r"\s+", " ", match.group(1)).strip()
        if not fields:
            continue
        refs.append(
            blank_query(
                raw=block.strip().replace("\n", " ")[:400],
                doi=rx.clean_doi(fields["doi"]) if fields.get("doi") else None,
                arxiv=fields.get("eprint"),
                title=fields.get("title"),
                surnames=rx.extract_surnames(fields.get("author")),
                year=(fields.get("year") or fields.get("date", ""))[:4] or None,
                venue=fields.get("journal") or fields.get("booktitle"),
            )
        )
    return refs


def parse_json_refs(text: str) -> List[Dict[str, Any]]:
    data = json.loads(text)
    if isinstance(data, dict):
        data = data.get("references") or data.get("items") or data.get("results") or []
    refs = []
    for item in data:
        if not isinstance(item, dict):
            continue
        refs.append(
            blank_query(
                raw=json.dumps(item, ensure_ascii=False)[:400],
                doi=rx.clean_doi(str(item.get("doi") or item.get("DOI") or "")) or None,
                arxiv=str(item.get("arxiv") or "") or None,
                title=item.get("title"),
                surnames=rx.extract_surnames(item.get("authors") or item.get("author")),
                year=str(item.get("year") or item.get("date") or "")[:4] or None,
                venue=item.get("venue") or item.get("journal") or item.get("container_title"),
            )
        )
    return refs


def build_query_from_text(entry: str) -> Dict[str, Any]:
    dois = rx.find_dois(entry)
    arxiv = rx.ARXIV_RE.search(entry)
    years = rx.YEAR_RE.findall(entry)
    title = guess_title(entry)
    if title and rx.ARXIV_RE.search(title):
        title = rx.ARXIV_RE.sub("", title).strip(" .,")
    return blank_query(
        raw=entry.strip()[:400],
        doi=dois[0] if dois else None,
        arxiv=(arxiv.group(1) + (arxiv.group(2) or "")) if arxiv else None,
        title=title,
        surnames=guess_surnames(entry),
        year=rx.YEAR_RE.search(entry).group(0)[:4] if rx.YEAR_RE.search(entry) else (years[0] if years else None),
    )


def extract_queries(text: str, suffix: str = "") -> List[Dict[str, Any]]:
    suffix = (suffix or "").lower()
    if suffix == ".bib":
        refs = parse_bib(text)
        if refs:
            return refs
    if suffix == ".json":
        try:
            refs = parse_json_refs(text)
            if refs:
                return refs
        except json.JSONDecodeError:
            pass
    return [build_query_from_text(entry) for entry in parse_plain_entries(text) if entry.strip()]


# --------------------------------------------------------------------------- #
# Lookups                                                                     #
# --------------------------------------------------------------------------- #


def crossref_doi(net: rx.Net, doi: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    params = {"mailto": net.mailto} if net.mailto else None
    body, error = net.get_json(f"https://api.crossref.org/works/{rx.urllib.parse.quote(doi)}", params)
    if error:
        return None, error
    message = (body or {}).get("message")
    if not message:
        return None, "empty Crossref record"
    return rx.from_crossref(message), None


def openalex_doi(net: rx.Net, doi: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    params = {"mailto": net.mailto} if net.mailto else None
    body, error = net.get_json(
        f"https://api.openalex.org/works/doi:{rx.urllib.parse.quote(doi)}", params
    )
    if error:
        return None, error
    if isinstance(body, dict) and body.get("id"):
        return rx.from_openalex(body), None
    return None, "empty OpenAlex record"


def crossref_search(
    net: rx.Net, title: str, author: Optional[str] = None
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    if not title or len(title) < 8:
        return None, "not found (404)"
    blob = title if not author else f"{title} {author}"
    params = {"query.bibliographic": blob, "rows": 3, "select": "DOI,title,author,issued,container-title,type,update-to,is-referenced-by-count"}
    if net.mailto:
        params["mailto"] = net.mailto
    body, error = net.get_json("https://api.crossref.org/works", params)
    if error:
        return None, error
    items = ((body or {}).get("message") or {}).get("items") or []
    if not items:
        return None, "not found (404)"
    return rx.from_crossref(items[0]), None


def openalex_search(net: rx.Net, title: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    if not title or len(title) < 8:
        return None, "not found (404)"
    params = {"search": title, "per-page": 3}
    if net.mailto:
        params["mailto"] = net.mailto
    body, error = net.get_json("https://api.openalex.org/works", params)
    if error:
        return None, error
    results = (body or {}).get("results") or []
    if not results:
        return None, "not found (404)"
    return rx.from_openalex(results[0]), None


def parse_arxiv_entry(text: Optional[str]) -> Optional[Dict[str, Any]]:
    if not text:
        return None
    import xml.etree.ElementTree as ET

    ns = {"a": "http://www.w3.org/2005/Atom"}
    try:
        entries = ET.fromstring(text).findall("a:entry", ns)
    except ET.ParseError:
        return None
    if not entries:
        return None
    entry = entries[0]
    return rx.from_arxiv(
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


def arxiv_search(net: rx.Net, title: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    if not title or len(title) < 8:
        return None, "not found (404)"
    query = 'ti:"%s"' % re.sub(r'["\\]', " ", title)[:180]
    text, error = net.get_text(
        "https://export.arxiv.org/api/query",
        {"search_query": query, "start": 0, "max_results": 3},
    )
    if error:
        return None, error
    record = parse_arxiv_entry(text)
    return (record, None) if record else (None, "not found (404)")


def doi_exists(net: rx.Net, doi: str) -> bool:
    body, _ = net.get_json(f"https://doi.org/api/handles/{rx.urllib.parse.quote(doi)}")
    try:
        return bool(body) and body.get("responseCode") == 1
    except AttributeError:
        return False


def best_of(candidates: List[rx.Tuple[Optional[Dict[str, Any]], Optional[str]]], query: Dict[str, Any], min_score: float) -> Dict[str, Any]:
    best: Optional[Dict[str, Any]] = None
    for record, error in candidates:
        verdict = rx.judge(query, record, min_score=min_score, error=error)
        if best is None:
            best = verdict
            continue
        rank = lambda v: (
            -STATUS_ORDER.index(v["verdict"]) if v["verdict"] in STATUS_ORDER else -99,
            v["score"],
        )
        if rank(verdict) > rank(best):
            best = verdict
        elif verdict["verdict"] in {rx.VERIFIED, rx.CORRECTED} and best["verdict"] in {rx.NOT_FOUND, rx.ERROR}:
            best = verdict
    return best or rx.judge(query, None)


def verify_one(
    net: rx.Net,
    query: Dict[str, Any],
    sources: List[str],
    min_score: float,
) -> Dict[str, Any]:
    """Cascade a single reference through the configured registries."""
    candidates: List[Tuple[Optional[Dict[str, Any]], Optional[str]]] = []
    attempts: List[str] = []

    def record_attempt(label: str, outcome: Tuple[Optional[Dict[str, Any]], Optional[str]]) -> None:
        attempts.append(label)
        candidates.append(outcome)

    def not_found_ok(item: Optional[Dict[str, Any]], error: Optional[str]) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        if item is not None:
            return item, None
        if error and error.startswith("not found"):
            return None, "not found (404)"
        return None, error

    if query.get("doi") and "crossref" in sources:
        record_attempt("crossref:doi", not_found_ok(*crossref_doi(net, query["doi"])))
    if query.get("doi") and "openalex" in sources and not any(c[0] for c in candidates):
        record_attempt("openalex:doi", not_found_ok(*openalex_doi(net, query["doi"])))

    if query.get("doi") and "doi" in sources and not any(c[0] for c in candidates):
        attempts.append("doi:handle")
        if doi_exists(net, query["doi"]):
            return {
                "verdict": rx.PARTIAL,
                "score": 1.0,
                "record": rx.blank_record(
                    source="doi.org",
                    doi=query["doi"],
                    title=query.get("title"),
                    url=f"https://doi.org/{query['doi']}",
                ),
                "notes": ["DOI resolves but no metadata was retrieved — open the DOI to confirm"],
                "error": None,
                "attempts": attempts,
            }

    if query.get("arxiv") and "arxiv" in sources and not any(c[0] for c in candidates):
        attempts.append("arxiv:id")
        text, error = net.get_text(
            "https://export.arxiv.org/api/query",
            {"id_list": query["arxiv"], "max_results": 1},
        )
        record = parse_arxiv_entry(text) if text else None
        if record:
            candidates.append((record, None))
        elif error and not error.startswith("not found"):
            candidates.append((None, error))

    if query.get("title") and not any(c[0] for c in candidates):
        if "crossref" in sources:
            attempts.append("crossref:search")
            outcome = crossref_search(net, query["title"], (query.get("surnames") or [None])[0])
            candidates.append(not_found_ok(*outcome))
        if "openalex" in sources and not any(c[0] for c in candidates):
            attempts.append("openalex:search")
            candidates.append(not_found_ok(*openalex_search(net, query["title"])))
        if "arxiv" in sources and not any(c[0] for c in candidates):
            attempts.append("arxiv:search")
            candidates.append(not_found_ok(*arxiv_search(net, query["title"])))

    verdict = best_of(candidates, query, min_score)
    verdict["attempts"] = attempts

    if verdict["verdict"] == rx.NOT_FOUND and candidates:
        failures = [
            error for record, error in candidates
            if record is None and error and not str(error).startswith(("not found", "empty"))
        ]
        if failures and len(failures) == len(candidates):
            verdict["verdict"] = rx.ERROR
            verdict["notes"] = [f"all lookups failed ({failures[0]}) — likely offline or rate-limited"]
    return verdict


# --------------------------------------------------------------------------- #
# Reporting                                                                   #
# --------------------------------------------------------------------------- #


def format_citation(record: Optional[Dict[str, Any]]) -> str:
    if not record:
        return ""
    authors = record.get("authors") or []
    author_str = ", ".join(authors[:3]) + (" et al." if len(authors) > 3 else "")
    parts = [
        author_str or "Unknown authors",
        f"({record.get('year') or 'n.d.'})",
        record.get("title") or "Untitled",
    ]
    if record.get("venue"):
        parts.append(str(record["venue"]))
    if record.get("doi"):
        parts.append(f"https://doi.org/{record['doi']}")
    return ". ".join(parts) + "."


def summarise(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    counts = {status: 0 for status in STATUS_ORDER}
    for item in results:
        counts[item["verdict"]] = counts.get(item["verdict"], 0) + 1
    total = len(results)
    verified = counts.get(rx.VERIFIED, 0)
    usable = verified + counts.get(rx.CORRECTED, 0)
    return {
        "total": total,
        "verified": verified,
        "corrected": counts.get(rx.CORRECTED, 0),
        "partial": counts.get(rx.PARTIAL, 0),
        "not_found": counts.get(rx.NOT_FOUND, 0),
        "retracted": counts.get(rx.RETRACTED, 0),
        "error": counts.get(rx.ERROR, 0),
        "counts": counts,
        "verified_ratio": round(usable / total, 3) if total else 0.0,
    }


def report_text(results: List[Dict[str, Any]], summary: Dict[str, Any]) -> str:
    lines = []
    for index, item in enumerate(results, 1):
        label = STATUS_ICON.get(item["verdict"], item["verdict"])
        query = item["query"]
        shown = query.get("title") or query.get("doi") or query.get("raw", "")[:90]
        lines.append(f"[{label}] {index}. {shown}")
        lines.append(
            f"        source={item['source'] or '-'} score={item['score']:.2f} "
            f"doi={item['doi'] or '-'}"
        )
        for note in item["notes"][:3]:
            lines.append(f"        note: {note}")
    lines.append("")
    lines.append(
        f"{summary['total']} references | {summary['verified']} verified | "
        f"{summary['corrected']} correctable | {summary['partial']} check | "
        f"{summary['not_found']} unverified | {summary['retracted']} retracted | "
        f"{summary['error']} error | verified ratio {summary['verified_ratio']:.0%}"
    )
    return "\n".join(lines)


def report_markdown(results: List[Dict[str, Any]], summary: Dict[str, Any], source_label: str) -> str:
    today = datetime.now().strftime("%Y-%m-%d")
    out = [
        "# Citation Audit",
        "",
        f"- Run: {today}",
        f"- Input: `{source_label}`",
        f"- Registries: Crossref, OpenAlex, arXiv, doi.org",
        f"- References checked: **{summary['total']}** — verified {summary['verified']}, "
        f"corrected {summary['corrected']}, check {summary['partial']}, "
        f"unverified {summary['not_found']}, retracted {summary['retracted']}, error {summary['error']}",
        f"- Verified ratio (verified + corrected): **{summary['verified_ratio']:.0%}**",
        "",
        "> `NOT_FOUND` means not found in the registries — it is not proof of fabrication. Books, theses,",
        "> brand-new papers and unindexed venues legitimately fail. Treat these as unverified: confirm",
        "> each by hand, or remove the claim that depends on it.",
        "",
        "## Reference-by-reference",
        "",
        "| # | Cited work | Verdict | Score | Matched record | Registry | Notes |",
        "|---|-----------|---------|-------|----------------|----------|-------|",
    ]
    for index, item in enumerate(results, 1):
        query = item["query"]
        cited = (query.get("title") or query.get("doi") or query.get("raw", "")[:80]).replace("|", "/")
        record = item.get("record") or {}
        matched_title = (record.get("title") or "-").replace("|", "/")
        matched = matched_title
        if record.get("doi"):
            matched += f" [doi.org/{record['doi']}](https://doi.org/{record['doi']})"
        notes = "; ".join(item["notes"][:2]).replace("|", "/") or "-"
        out.append(
            f"| {index} | {cited} | **{item['verdict']}** | {item['score']:.2f} | {matched} | "
            f"{item.get('source') or '-'} | {notes} |"
        )
    corrections = [r for r in results if r["verdict"] == rx.CORRECTED]
    if corrections:
        out += ["", "## Suggested corrected citations", ""]
        for item in corrections:
            out.append(f"- **Cited:** {item['query'].get('title') or item['query'].get('raw', '')[:120]}")
            out.append(f"  **Use:** {format_citation(item.get('record'))}")
    unverified = [r for r in results if r["verdict"] in {rx.NOT_FOUND, rx.PARTIAL}]
    if unverified:
        out += [
            "",
            "## Needs a human check",
            "",
            "These did not resolve automatically. Before submission: open each one, or drop it and",
            "the claim that depends on it.",
            "",
        ]
        for item in unverified:
            out.append(f"- {item['query'].get('title') or item['query'].get('raw', '')[:140]}")
    retracted = [r for r in results if r["verdict"] == rx.RETRACTED]
    if retracted:
        out += ["", "## Retracted / withdrawn", ""]
        for item in retracted:
            out.append(
                f"- {item['query'].get('title') or item['query'].get('raw', '')[:140]} — "
                f"{'; '.join(item['notes'])}"
            )
    out.append("")
    return "\n".join(out)


# --------------------------------------------------------------------------- #
# CLI                                                                         #
# --------------------------------------------------------------------------- #


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="verify_citations.py",
        description="Verify references against Crossref, OpenAlex, arXiv and doi.org.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("path", nargs="?", default=None, help="document to audit (same as --input)")
    parser.add_argument("--input", "-i", default=None, help="document to audit (.md .txt .bib .json), or '-'")
    parser.add_argument("--doi", action="append", default=[], help="verify a single DOI (repeatable)")
    parser.add_argument("--title", default=None, help="verify a single title")
    parser.add_argument("--author", default=None, help="author hint for --title")
    parser.add_argument("--year", default=None, help="year hint for --title")
    parser.add_argument("--format", "-f", choices=["text", "md", "json"], default="text")
    parser.add_argument("--out", "-o", default=None, help="write the report to this file")
    parser.add_argument("--source", default="crossref,openalex,arxiv,doi", help="comma-separated registry order")
    parser.add_argument("--min-score", type=float, default=0.80, help="title similarity for VERIFIED (0-1)")
    parser.add_argument("--max-refs", type=int, default=60, help="maximum references to check")
    parser.add_argument("--offline", action="store_true", help="use only cached responses")
    parser.add_argument("--cache-dir", default=rx.DEFAULT_CACHE_DIR, help="cache directory")
    parser.add_argument("--timeout", type=float, default=rx.DEFAULT_TIMEOUT, help="per-request timeout (s)")
    parser.add_argument("--mailto", default=rx.env_mailto(), help="contact email for polite pools")
    parser.add_argument("--sleep", type=float, default=0.0, help="delay between registry requests (s)")
    parser.add_argument("--fail-on-unverified", action="store_true", help="exit 1 unless every reference is VERIFIED")
    parser.add_argument("--quiet", action="store_true", help="suppress progress output")
    return parser.parse_args(argv)


def build_queries(args: argparse.Namespace) -> List[Dict[str, Any]]:
    queries: List[Dict[str, Any]] = []
    if not args.input and args.path:
        args.input = args.path
    if args.doi:
        for doi in args.doi:
            queries.append(blank_query(raw=doi, doi=rx.clean_doi(doi)))
    if args.title:
        queries.append(
            blank_query(
                raw=args.title,
                title=args.title,
                surnames=rx.extract_surnames(args.author) if args.author else [],
                year=args.year,
            )
        )
    if args.input:
        if args.input == "-":
            text, suffix = sys.stdin.read(), ""
        else:
            path = Path(args.input)
            text, suffix = path.read_text(encoding="utf-8", errors="replace"), path.suffix
        queries.extend(extract_queries(text, suffix))
    return queries


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    queries = build_queries(args)
    if not queries:
        print("No references found. Pass --input, --doi or --title (see --help).", file=sys.stderr)
        return 2

    queries = queries[: max(1, args.max_refs)]
    sources = [s.strip().lower() for s in args.source.split(",") if s.strip()]
    net = rx.Net(
        cache_dir=args.cache_dir,
        offline=args.offline,
        timeout=args.timeout,
        mailto=args.mailto,
        sleep=args.sleep,
    )

    results: List[Dict[str, Any]] = []
    for index, query in enumerate(queries, 1):
        if not args.quiet:
            label = query.get("title") or query.get("doi") or query.get("raw", "")[:60]
            print(f"[{index}/{len(queries)}] checking {label}", file=sys.stderr)
        verdict = verify_one(net, query, sources, args.min_score)
        record = verdict.get("record") or {}
        results.append(
            {
                "query": query,
                "verdict": verdict["verdict"],
                "score": verdict.get("score", 0.0),
                "notes": verdict.get("notes", []),
                "attempts": verdict.get("attempts", []),
                "source": record.get("source"),
                "doi": record.get("doi"),
                "record": record,
                "evidence": record.get("url"),
            }
        )

    summary = summarise(results)
    summary["net_calls"] = net.calls
    summary["cache_hits"] = net.cache_hits
    summary["lookup_errors"] = net.errors[:10]

    if args.format == "json":
        report = json.dumps(
            {"summary": summary, "results": results, "generated": datetime.now().isoformat(timespec="seconds")},
            ensure_ascii=False,
            indent=2,
        )
    elif args.format == "md":
        report = report_markdown(results, summary, args.input or args.title or args.doi or "stdin")
    else:
        report = report_text(results, summary)

    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(report + "\n", encoding="utf-8")
        if not args.quiet:
            print(f"report written to {args.out}", file=sys.stderr)
    else:
        print(report)

    if summary["total"] and summary["error"] == summary["total"]:
        return 3
    if args.fail_on_unverified and summary["verified"] != summary["total"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
