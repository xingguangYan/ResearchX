#!/usr/bin/env python3
"""ResearchX — extract the notes for one release from RELEASE-NOTES.md or CHANGELOG.md.

Used by `.github/workflows/release.yml` to fill the GitHub Release body, and useful locally:

    python scripts/extract_release_notes.py v4.0.0                 # newest section, notes only
    python scripts/extract_release_notes.py --version 4.0.0        # from RELEASE-NOTES.md
    python scripts/extract_release_notes.py --source changelog     # from CHANGELOG.md
    python scripts/extract_release_notes.py --current --out release_body.md

Exit codes: 0 = section found, 1 = version not found, 2 = usage error.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import List, Optional, Tuple

REPO = Path(__file__).resolve().parents[1]
FILES = {"notes": REPO / "RELEASE-NOTES.md", "changelog": REPO / "CHANGELOG.md"}


def sections(text: str) -> List[Tuple[str, str]]:
    """Split a markdown file into (version, body) sections on `## vX.Y.Z` / `## [X.Y.Z]`."""
    out: List[Tuple[str, str]] = []
    current_version: Optional[str] = None
    buffer: List[str] = []
    for line in text.splitlines():
        if line.startswith("## "):
            if current_version is not None:
                out.append((current_version, "\n".join(buffer).strip()))
            heading = line[3:].strip()
            match = re.search(r"\[?v?(\d+\.\d+\.\d+(?:-[0-9A-Za-z.\-]+)?)\]?", heading)
            current_version = match.group(1) if match else None
            buffer = [line]
        elif current_version is not None:
            buffer.append(line)
    if current_version is not None:
        out.append((current_version, "\n".join(buffer).strip()))
    return out


def extract(source: str, version: Optional[str]) -> Tuple[Optional[str], List[str]]:
    path = FILES[source]
    if not path.exists():
        return None, []
    found = sections(path.read_text(encoding="utf-8"))
    if not found:
        return None, []
    if version is None:
        return found[0][1], [v for v, _ in found]
    wanted = version[1:] if version.startswith("v") else version
    for candidate, body in found:
        if candidate == wanted:
            return body, [v for v, _ in found]
    return None, [v for v, _ in found]


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="extract_release_notes.py",
        description="Extract one version's notes for a GitHub Release body.",
    )
    parser.add_argument("version", nargs="?", default=None, help="version or tag (e.g. v4.0.0); default: newest")
    parser.add_argument("--version", dest="version_opt", default=None, help="same as the positional argument")
    parser.add_argument("--source", choices=sorted(FILES), default="notes")
    parser.add_argument("--out", "-o", default=None, help="write to a file instead of stdout")
    parser.add_argument("--current", action="store_true", help="use the version from SKILL.md")
    args = parser.parse_args(argv)

    version = args.version_opt or args.version
    if args.current or version is None:
        skill = (REPO / "skills/researchx/SKILL.md").read_text(encoding="utf-8")
        match = re.search(r'^\s+version:\s*"?([0-9][0-9A-Za-z.\-]+)', skill, re.M)
        version = match.group(1) if match else None

    body, available = extract(args.source, version)
    if body is None:
        print(
            f"error: no section for {version or 'current version'} in {FILES[args.source].name}"
            + (f" (available: {', '.join(available)})" if available else ""),
            file=sys.stderr,
        )
        return 1

    if args.out:
        Path(args.out).write_text(body + "\n", encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        print(body)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
