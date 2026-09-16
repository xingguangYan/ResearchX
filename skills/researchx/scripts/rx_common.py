#!/usr/bin/env python3
"""ResearchX shared helpers — HTTP with cache, text normalisation, record matching.

Standard library only (urllib). No API keys are required for any registry used here.

Design rules for everything in this directory:
  * non-interactive, `--help` documented, structured output on stdout
  * network failures are reported as data (never raised at the user as a traceback)
  * results are cached on disk so the same query is never paid for twice
"""

from __future__ import annotations

import difflib
import hashlib
import json
import os
import re
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple

VERSION = "4.0.0"
USER_AGENT = (
    f"ResearchX/{VERSION} (citation-verifier; "
    "+https://github.com/xingguangYan/ResearchX)"
)
DEFAULT_CACHE_DIR = ".researchx-cache"
DEFAULT_TIMEOUT = 20

# --------------------------------------------------------------------------- #
# Cache                                                                       #
# --------------------------------------------------------------------------- #


def cache_key(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest()[:32]


def read_cache(cache_dir: Optional[str], url: str) -> Optional[Any]:
    if not cache_dir:
        return None
    path = Path(cache_dir) / f"{cache_key(url)}.json"
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return payload.get("body")


def write_cache(cache_dir: Optional[str], url: str, body: Any) -> None:
    if not cache_dir or body is None:
        return
    directory = Path(cache_dir)
    try:
        directory.mkdir(parents=True, exist_ok=True)
        (directory / f"{cache_key(url)}.json").write_text(
            json.dumps({"url": url, "body": body}, ensure_ascii=False),
            encoding="utf-8",
        )
    except Exception:
        pass  # cache is a nicety; never fail the run because of it


class Net:
    """Tiny HTTP client: polite headers, disk cache, explicit error values."""

    def __init__(
        self,
        cache_dir: Optional[str] = DEFAULT_CACHE_DIR,
        offline: bool = False,
        timeout: float = DEFAULT_TIMEOUT,
        mailto: Optional[str] = None,
        sleep: float = 0.0,
        transport: Optional[Callable[[str], Any]] = None,
    ) -> None:
        self.cache_dir = cache_dir
        self.offline = offline
        self.timeout = timeout
        self.mailto = mailto
        self.sleep = sleep
        self.transport = transport  # injectable for tests
        self.calls = 0
        self.cache_hits = 0
        self.errors: List[str] = []

    def get_json(self, url: str, params: Optional[Dict[str, Any]] = None) -> Tuple[Optional[Any], Optional[str]]:
        """Return (body, error). One of the two is always None."""
        if params:
            sep = "&" if "?" in url else "?"
            url = url + sep + urllib.parse.urlencode(params)

        cached = read_cache(self.cache_dir, url)
        if cached is not None:
            self.cache_hits += 1
            return cached, None
        if self.offline:
            return None, "offline: no cached response"

        if self.transport is not None:
            try:
                body = self.transport(url)
                write_cache(self.cache_dir, url, body)
                return body, None
            except Exception as exc:  # pragma: no cover - test hook
                self.errors.append(f"{url}: {exc}")
                return None, str(exc)

        if self.sleep:
            time.sleep(self.sleep)

        headers = {
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
        }
        if self.mailto:
            headers["X-Requested-With"] = self.mailto
        request = urllib.request.Request(url, headers=headers)
        self.calls += 1
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                raw = response.read().decode("utf-8", errors="replace")
            body = json.loads(raw)
            write_cache(self.cache_dir, url, body)
            return body, None
        except urllib.error.HTTPError as exc:
            message = f"HTTP {exc.code}"
            if exc.code == 404:
                message = "not found (404)"
            self.errors.append(f"{url}: {message}")
            return None, message
        except urllib.error.URLError as exc:
            self.errors.append(f"{url}: {exc.reason}")
            return None, f"network error: {exc.reason}"
        except json.JSONDecodeError:
            return None, "invalid JSON response"
        except Exception as exc:  # timeouts, TLS issues, ...
            self.errors.append(f"{url}: {exc}")
            return None, str(exc)

    def get_text(self, url: str, params: Optional[Dict[str, Any]] = None) -> Tuple[Optional[str], Optional[str]]:
        if params:
            sep = "&" if "?" in url else "?"
            url = url + sep + urllib.parse.urlencode(params)
        cached = read_cache(self.cache_dir, url)
        if cached is not None:
            self.cache_hits += 1
            return cached if isinstance(cached, str) else json.dumps(cached), None
        if self.offline:
            return None, "offline: no cached response"
        if self.transport is not None:
            try:
                body = self.transport(url)
                if not isinstance(body, str):
                    body = json.dumps(body)
                write_cache(self.cache_dir, url, body)
                return body, None
            except Exception as exc:  # pragma: no cover - test hook
                return None, str(exc)
        if self.sleep:
            time.sleep(self.sleep)
        request = urllib.request.Request(
            url, headers={"User-Agent": USER_AGENT, "Accept": "application/atom+xml, text/xml"}
        )
        self.calls += 1
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                text = response.read().decode("utf-8", errors="replace")
            write_cache(self.cache_dir, url, text)
            return text, None
        except urllib.error.HTTPError as exc:
            return None, f"HTTP {exc.code}"
        except Exception as exc:
            return None, str(exc)


# --------------------------------------------------------------------------- #
# Normalisation & similarity                                                  #
# --------------------------------------------------------------------------- #

_PUNCT = re.compile(r"[^\w\s]", re.UNICODE)
_SPACE = re.compile(r"\s+")
_LATEX = re.compile(r"\\[a-zA-Z]+\{?|\}|\$")


def normalise(text: Optional[str]) -> str:
    """Lowercase, strip LaTeX/markup, punctuation and collapse whitespace."""
    if not text:
        return ""
    text = _LATEX.sub(" ", str(text))
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.lower()
    text = _PUNCT.sub(" ", text)
    return _SPACE.sub(" ", text).strip()


def tokens(text: Optional[str]) -> List[str]:
    return [t for t in normalise(text).split() if len(t) > 1]


def title_similarity(a: Optional[str], b: Optional[str]) -> float:
    """Blend of character ratio and token coverage; robust to subtitle/format drift."""
    na, nb = normalise(a), normalise(b)
    if not na or not nb:
        return 0.0
    ratio = difflib.SequenceMatcher(None, na, nb).ratio()
    ta, tb = set(tokens(a)), set(tokens(b))
    if not ta or not tb:
        return ratio
    coverage = len(ta & tb) / min(len(ta), len(tb))
    return round(max(ratio, 0.65 * ratio + 0.35 * coverage), 4)


_SURNAME_STOPWORDS = {
    "the", "and", "for", "with", "from", "van", "von", "de", "del", "der", "la", "le",
    "jr", "sr", "ii", "iii", "et", "al", "university", "institute", "department",
}


def surname_match(candidate_surnames: Sequence[str], record_authors: Sequence[str]) -> bool:
    """True when any candidate surname appears in the record's author list."""
    if not candidate_surnames or not record_authors:
        return False
    record_blob = normalise(" ".join(record_authors))
    for surname in candidate_surnames:
        pieces = [p for p in normalise(surname).split() if p not in _SURNAME_STOPWORDS and len(p) > 2]
        if pieces and any(piece in record_blob for piece in pieces):
            return True
    return False


_INITIALS_RE = re.compile(r"^(?:[A-Z]\.?\s*)+$")


def split_author_string(text: str) -> List[str]:
    """Split an author string into individual authors.

    Handles 'Chen, W., Kumar, A.' (APA-ish), 'Chen and Kumar', 'Chen; Kumar'.
    """
    parts = re.split(r"\s*(?:;|, and | and |&)\s*", text)
    if len(parts) > 1:
        return [p for p in parts if p.strip()]
    chunks = [chunk.strip() for chunk in text.split(",") if chunk.strip()]
    authors: List[str] = []
    for chunk in chunks:
        if _INITIALS_RE.match(chunk) or len(chunk) <= 2:
            continue  # initials belong to the preceding surname
        authors.append(chunk)
    return authors or [p for p in parts if p.strip()]


def extract_surnames(authors: Any) -> List[str]:
    """Accept 'Family, Given', 'Given Family', or lists/dicts."""
    if not authors:
        return []
    if isinstance(authors, dict):
        authors = [authors]
    if isinstance(authors, str):
        authors = split_author_string(authors)
    out: List[str] = []
    for entry in authors:
        if isinstance(entry, dict):
            family = entry.get("family") or entry.get("name") or entry.get("literal")
            if family:
                out.append(str(family))
            continue
        text = str(entry).strip()
        if not text:
            continue
        if "," in text:
            out.append(text.split(",")[0].strip())
        else:
            parts = text.split()
            out.append(parts[-1] if parts else text)
    return out


def years_apart(a: Optional[Any], b: Optional[Any], tolerance: int = 1) -> bool:
    try:
        ya, yb = int(str(a)[:4]), int(str(b)[:4])
    except (TypeError, ValueError):
        return True  # unknown year is not evidence of a mismatch
    return abs(ya - yb) <= tolerance


# --------------------------------------------------------------------------- #
# Registry record normalisation                                               #
# --------------------------------------------------------------------------- #


def blank_record(**overrides: Any) -> Dict[str, Any]:
    record: Dict[str, Any] = {
        "source": None,
        "id": None,
        "doi": None,
        "title": None,
        "authors": [],
        "year": None,
        "venue": None,
        "type": None,
        "url": None,
        "retracted": False,
        "retraction_doi": None,
        "cited_by": None,
        "abstract": None,
    }
    record.update(overrides)
    return record


def from_crossref(message: Dict[str, Any]) -> Dict[str, Any]:
    title = (message.get("title") or [None])[0]
    issued = message.get("issued", {}).get("date-parts", [[None]])
    year = issued[0][0] if issued and issued[0] else None
    authors = extract_surnames(message.get("author") or [])
    retracted = False
    retraction_doi = None
    for update in message.get("update-to") or []:
        if "retraction" in str(update.get("type", "")).lower():
            retracted = True
            retraction_doi = update.get("DOI")
    if str(message.get("type", "")).lower() in {"retraction", "withdrawal"}:
        retracted = True
    return blank_record(
        source="crossref",
        id=message.get("DOI"),
        doi=message.get("DOI"),
        title=title,
        authors=[a for a in authors if a],
        year=year,
        venue=(message.get("container-title") or [None])[0],
        type=message.get("type"),
        url=f"https://doi.org/{message.get('DOI')}" if message.get("DOI") else message.get("URL"),
        retracted=retracted,
        retraction_doi=retraction_doi,
        cited_by=message.get("is-referenced-by-count"),
    )


def from_openalex(work: Dict[str, Any]) -> Dict[str, Any]:
    authors: List[str] = []
    for authorship in work.get("authorships") or []:
        name = (authorship.get("author") or {}).get("display_name")
        if name:
            authors.append(name.split()[-1])
    doi = work.get("doi")
    if doi and doi.startswith("https://doi.org/"):
        doi = doi[len("https://doi.org/"):]
    return blank_record(
        source="openalex",
        id=work.get("id"),
        doi=doi,
        title=work.get("title") or work.get("display_name"),
        authors=authors,
        year=work.get("publication_year"),
        venue=((work.get("primary_location") or {}).get("source") or {}).get("display_name"),
        type=work.get("type"),
        url=work.get("doi") or work.get("id"),
        retracted=bool(work.get("is_retracted")),
        cited_by=work.get("cited_by_count"),
    )


def from_arxiv(entry: Dict[str, Any]) -> Dict[str, Any]:
    return blank_record(
        source="arxiv",
        id=entry.get("id"),
        doi=entry.get("doi"),
        title=entry.get("title"),
        authors=extract_surnames(entry.get("authors") or []),
        year=(entry.get("published") or "")[:4] or None,
        venue="arXiv preprint",
        type="preprint",
        url=entry.get("id"),
    )


# --------------------------------------------------------------------------- #
# Verdict logic                                                               #
# --------------------------------------------------------------------------- #

VERIFIED = "VERIFIED"
CORRECTED = "CORRECTED"
PARTIAL = "PARTIAL"
NOT_FOUND = "NOT_FOUND"
RETRACTED = "RETRACTED"
ERROR = "ERROR"

_GREY_TYPES = {
    "book", "book-chapter", "monograph", "edited-book", "dissertation", "thesis",
    "report", "dataset", "posted-content", "standard", "reference-entry",
}


def judge(
    query: Dict[str, Any],
    record: Optional[Dict[str, Any]],
    min_score: float = 0.80,
    correction_score: float = 0.60,
    error: Optional[str] = None,
) -> Dict[str, Any]:
    """Compare a query reference to a retrieved record and decide a verdict."""
    result: Dict[str, Any] = {
        "verdict": NOT_FOUND,
        "score": 0.0,
        "record": record,
        "notes": [],
        "error": error,
    }
    if record is None:
        if error and not str(error).startswith(("not found", "empty", "offline")):
            result.update(verdict=ERROR, notes=[f"lookup failed: {error}"])
        else:
            result["notes"].append(
                "no matching record in any queried registry (not found — not proof of fabrication)"
            )
        return result

    # An exact DOI match is authoritative: the identifier is the record's identity.
    doi_match = bool(
        query.get("doi")
        and record.get("doi")
        and clean_doi(str(query["doi"])).lower() == clean_doi(str(record["doi"])).lower()
    )
    score = 1.0 if doi_match else title_similarity(query.get("title"), record.get("title"))
    result["score"] = score
    author_ok = surname_match(query.get("surnames") or [], record.get("authors") or []) or doi_match
    # Even with an exact DOI, a wrong year is metadata drift worth reporting.
    year_ok = years_apart(query.get("year"), record.get("year")) if query.get("year") else True
    result["author_match"] = author_ok
    result["year_match"] = year_ok

    if record.get("retracted"):
        result["verdict"] = RETRACTED
        result["notes"].append(
            "registry flags this work as retracted/withdrawn"
            + (f" (notice: {record.get('retraction_doi')})" if record.get("retraction_doi") else "")
        )
        return result

    if score >= min_score and (author_ok or not query.get("surnames")):
        if year_ok:
            result["verdict"] = VERIFIED
        else:
            result["verdict"] = CORRECTED
            result["notes"].append(
                f"year differs: cited {query.get('year')}, registry {record.get('year')}"
            )
        return result

    if score >= correction_score:
        if record.get("type") in _GREY_TYPES and score < min_score:
            result["verdict"] = PARTIAL
            result["notes"].append("possible grey-literature match — confirm by hand")
            return result
        result["verdict"] = CORRECTED
        if query.get("year") and not year_ok:
            result["notes"].append(f"year differs: cited {query.get('year')}, registry {record.get('year')}")
        if query.get("surnames") and not author_ok:
            result["notes"].append("author list does not match the registry record")
        if score < min_score:
            result["notes"].append(f"title similarity {score:.2f} — metadata drift, verify the target")
        if not result["notes"]:
            result["notes"].append("metadata differs slightly from the registry record")
        return result

    result["notes"].append(f"closest candidate scored {score:.2f} — likely a different work")
    result["record"] = None if score < 0.40 else record
    return result


# --------------------------------------------------------------------------- #
# Misc CLI helpers                                                            #
# --------------------------------------------------------------------------- #


def human_counts(items: Iterable[str]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for item in items:
        counts[item] = counts.get(item, 0) + 1
    return counts


def cli(argv: Optional[List[str]] = None) -> int:
    """Small entry point so the module documents itself like the other scripts."""
    import argparse

    parser = argparse.ArgumentParser(
        prog="rx_common.py",
        description=(
            "Shared helpers for the ResearchX scripts: disk-cached HTTP (Net), title/author "
            "matching, registry record normalisation and verdict logic (judge)."
        ),
    )
    parser.add_argument("--version", action="version", version=f"ResearchX {VERSION}")
    parser.add_argument(
        "--selftest",
        action="store_true",
        help="run the offline sanity checks (no network) and exit 0 when healthy",
    )
    args = parser.parse_args(argv)
    if args.selftest:
        checks = {
            "title_similarity": round(title_similarity("Attention is all you need", "Attention Is All You Need"), 3),
            "surnames": extract_surnames("Chen, W., Kumar, A."),
            "doi_clean": clean_doi("10.1000/abc.123."),
            "judge": judge(
                {"title": "Attention is all you need", "surnames": ["Vaswani"], "year": "2017"},
                blank_record(title="Attention is all you need", authors=["Vaswani"], year=2017),
            )["verdict"],
        }
        print(json.dumps(checks, ensure_ascii=False, indent=2))
        return 0
    parser.print_help()
    return 0


def env_mailto() -> Optional[str]:
    return os.environ.get("RESEARCHX_MAILTO") or os.environ.get("CROSSREF_MAILTO")


def slugify(text: str, fallback: str = "topic", maxlen: int = 48) -> str:
    ascii_text = unicodedata.normalize("NFKD", text or "")
    ascii_text = "".join(ch for ch in ascii_text if not unicodedata.combining(ch)).lower()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_text).strip("-")
    return (slug[:maxlen].rstrip("-") or fallback)


DOI_RE = re.compile(r"10\.\d{4,9}/[-._;()/:A-Za-z0-9]+")
ARXIV_RE = re.compile(r"arXiv[:\s]*([a-z\-]+(?:\.[A-Z]{2})?/\d{7}|\d{4}\.\d{4,5})(v\d+)?", re.I)
YEAR_RE = re.compile(r"\b(19|20)\d{2}[a-z]?\b")


def clean_doi(doi: str) -> str:
    doi = doi.strip().rstrip(".,;)]}\u3002\uff0c")
    return doi[4:] if doi.lower().startswith("doi:") else doi


def find_dois(text: str) -> List[str]:
    found: List[str] = []
    for match in DOI_RE.findall(text or ""):
        cleaned = clean_doi(match)
        if cleaned and cleaned not in found:
            found.append(cleaned)
    return found


if __name__ == "__main__":
    raise SystemExit(cli())
