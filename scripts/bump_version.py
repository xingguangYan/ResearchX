#!/usr/bin/env python3
"""ResearchX — keep every version number in the repository in sync.

The skill version lives in eleven places (frontmatter metadata, four plugin manifests, the MCP
package metadata, two Python constants, CITATION.cff, CHANGELOG headings and RELEASE-NOTES). This
script is the single source of truth for them: it reads, checks and writes them.

Usage
-----
  python scripts/bump_version.py --check                 # verify everything agrees (CI gate)
  python scripts/bump_version.py --current               # print the current version
  python scripts/bump_version.py --tag                   # print the expected release tag (vX.Y.Z)
  python scripts/bump_version.py --set 4.1.0             # bump every file
  python scripts/bump_version.py --set 4.1.0 --dry-run   # show what would change
  python scripts/bump_version.py --check --tag v4.0.0    # also fail when the git tag disagrees

Exit codes: 0 = consistent, 1 = mismatch, 2 = usage error.

Rules
-----
* `skills/researchx/SKILL.md` metadata.version is authoritative; every other file must match it.
* `--set` refuses to go backwards (use --force to override) and refuses to touch a version that is
  already correct.
* CHANGELOG.md and RELEASE-NOTES.md are not rewritten: a human writes the entry, the check only
  verifies that a heading for the current version exists.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

REPO = Path(__file__).resolve().parents[1]
SEMVER = re.compile(r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?$")


def read_json(path: Path) -> Dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Dict, dry_run: bool) -> None:
    if dry_run:
        return
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


# --------------------------------------------------------------------------- #
# Version locations                                                           #
# --------------------------------------------------------------------------- #


def skill_version(path: Path) -> Optional[str]:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"^\s+version:\s*[\"']?([0-9][0-9A-Za-z.\-]*)[\"']?\s*$", text, re.M)
    return match.group(1) if match else None


def set_skill_version(path: Path, version: str, dry_run: bool) -> None:
    text = path.read_text(encoding="utf-8")

    def replace(match: re.Match) -> str:
        return f'{match.group(1)}version: "{version}"'

    updated = re.sub(r"(?m)^(\s+)version:\s*[\"']?[0-9][0-9A-Za-z.\-]*[\"']?\s*$",
                     lambda m: f'{m.group(1)}version: "{version}"', text, count=1)
    if updated == text:
        raise SystemExit(f"error: could not find a metadata version line in {path}")
    if not dry_run:
        path.write_text(updated, encoding="utf-8")


def py_constant(path: Path, name: str) -> Optional[str]:
    match = re.search(rf'^{name}\s*=\s*"([^"]+)"', path.read_text(encoding="utf-8"), re.M)
    return match.group(1) if match else None


def set_py_constant(path: Path, name: str, version: str, dry_run: bool) -> None:
    text = path.read_text(encoding="utf-8")
    updated = re.sub(rf'^({name}\s*=\s*)"[^"]+"', rf'\g<1>"{version}"', text, count=1, flags=re.M)
    if updated == text:
        raise SystemExit(f"error: could not find {name} in {path}")
    if not dry_run:
        path.write_text(updated, encoding="utf-8")


def toml_version(path: Path) -> Optional[str]:
    match = re.search(r'^version\s*=\s*"([^"]+)"', path.read_text(encoding="utf-8"), re.M)
    return match.group(1) if match else None


def set_toml_version(path: Path, version: str, dry_run: bool) -> None:
    text = path.read_text(encoding="utf-8")
    updated = re.sub(r'^(version\s*=\s*)"[^"]+"', rf'\g<1>"{version}"', text, count=1, flags=re.M)
    if updated == text:
        raise SystemExit(f"error: could not find a version field in {path}")
    if not dry_run:
        path.write_text(updated, encoding="utf-8")


def cff_version(path: Path) -> Optional[str]:
    match = re.search(r"^version:\s*[\"']?([0-9][0-9A-Za-z.\-]*)", path.read_text(encoding="utf-8"), re.M)
    return match.group(1) if match else None


def set_cff_version(path: Path, version: str, dry_run: bool) -> None:
    text = path.read_text(encoding="utf-8")
    updated = re.sub(r"^version:\s*[\"']?[0-9][0-9A-Za-z.\-]*", f"version: {version}",
                     text, count=1, flags=re.M)
    if updated == text:
        raise SystemExit(f"error: could not find a version field in {path}")
    if not dry_run:
        path.write_text(updated, encoding="utf-8")


def collect() -> List[Tuple[str, Optional[str]]]:
    """Return [(label, version)] for every location that carries a version."""
    found: List[Tuple[str, Optional[str]]] = []
    found.append(("skills/researchx/SKILL.md (metadata.version)", skill_version(REPO / "skills/researchx/SKILL.md")))

    for relative in (".claude-plugin/plugin.json", ".codex-plugin/plugin.json", ".cursor-plugin/plugin.json"):
        path = REPO / relative
        payload = read_json(path) if path.exists() else {}
        found.append((relative, payload.get("version")))

    marketplace = REPO / ".claude-plugin/marketplace.json"
    if marketplace.exists():
        payload = read_json(marketplace)
        for entry in payload.get("plugins", []):
            found.append((f".claude-plugin/marketplace.json → {entry.get('name')}", entry.get("version")))

    gemini = REPO / "gemini-extension.json"
    if gemini.exists():
        found.append(("gemini-extension.json", read_json(gemini).get("version")))

    package = REPO / "mcp-server/package.json"
    if package.exists():
        found.append(("mcp-server/package.json", read_json(package).get("version")))

    pyproject = REPO / "mcp-server/pyproject.toml"
    if pyproject.exists():
        found.append(("mcp-server/pyproject.toml", toml_version(pyproject)))

    found.append((
        "mcp-server/researchx_mcp_server.py (SERVER_VERSION)",
        py_constant(REPO / "mcp-server/researchx_mcp_server.py", "SERVER_VERSION"),
    ))
    found.append((
        "skills/researchx/scripts/rx_common.py (VERSION)",
        py_constant(REPO / "skills/researchx/scripts/rx_common.py", "VERSION"),
    ))
    found.append(("CITATION.cff", cff_version(REPO / "CITATION.cff")))
    return found


def changelog_versions() -> List[str]:
    text = (REPO / "CHANGELOG.md").read_text(encoding="utf-8") if (REPO / "CHANGELOG.md").exists() else ""
    return re.findall(r"^##\s*\[([0-9][0-9A-Za-z.\-]*)\]", text, re.M)


def release_notes_versions() -> List[str]:
    path = REPO / "RELEASE-NOTES.md"
    if not path.exists():
        return []
    return re.findall(r"^##\s*v?([0-9][0-9A-Za-z.\-]*)", path.read_text(encoding="utf-8"), re.M)


def bump(version: str, dry_run: bool) -> None:
    set_skill_version(REPO / "skills/researchx/SKILL.md", version, dry_run)

    for relative in (".claude-plugin/plugin.json", ".codex-plugin/plugin.json", ".cursor-plugin/plugin.json"):
        path = REPO / relative
        if path.exists():
            payload = read_json(path)
            payload["version"] = version
            write_json(path, payload, dry_run)

    marketplace = REPO / ".claude-plugin/marketplace.json"
    if marketplace.exists():
        payload = read_json(marketplace)
        for entry in payload.get("plugins", []):
            entry["version"] = version
        write_json(marketplace, payload, dry_run)

    for relative in ("gemini-extension.json", "mcp-server/package.json"):
        path = REPO / relative
        if path.exists():
            payload = read_json(path)
            payload["version"] = version
            write_json(path, payload, dry_run)

    set_toml_version(REPO / "mcp-server/pyproject.toml", version, dry_run)
    set_py_constant(REPO / "mcp-server/researchx_mcp_server.py", "SERVER_VERSION", version, dry_run)
    set_py_constant(REPO / "skills/researchx/scripts/rx_common.py", "VERSION", version, dry_run)
    set_cff_version(REPO / "CITATION.cff", version, dry_run)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="bump_version.py",
        description="Read, check and update the ResearchX version everywhere it appears.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--check", action="store_true", help="verify every location agrees (exit 1 on drift)")
    parser.add_argument("--current", action="store_true", help="print the current version and exit")
    parser.add_argument("--tag", dest="tag", nargs="?", const="__auto__", default=None,
                        help="expected release tag: 'v4.1.0' or '-v4.1.0' (e.g. in CI, pass $GITHUB_REF_NAME)")
    parser.add_argument("--set", dest="new_version", default=None, help="set this version everywhere")
    parser.add_argument("--dry-run", action="store_true", help="with --set: show what would change")
    parser.add_argument("--force", action="store_true", help="allow a version that goes backwards")
    args = parser.parse_args(argv)

    locations = collect()
    versions = {version for _, version in locations if version}
    authoritative = locations[0][1]

    if args.current:
        print(authoritative or "")
        return 0

    if args.tag and args.tag != "__auto__":
        expected = args.tag[1:] if args.tag.startswith("v") else args.tag
        problems = False
        if not SEMVER.match(args.tag[1:] if args.tag.startswith("v") else args.tag):
            print(f"error: tag {args.tag!r} is not of the form vX.Y.Z", file=sys.stderr)
            return 2
        if expected != authoritative:
            print(
                f"error: tag {args.tag} does not match the repository version {authoritative}\n"
                f"       bump the version first: python scripts/bump_version.py --set {expected}",
                file=sys.stderr,
            )
            problems = True
        if problems:
            return 1

    if args.new_version:
        if not SEMVER.match(args.new_version):
            print(f"error: {args.new_version!r} is not a semantic version", file=sys.stderr)
            return 2
        if authoritative and not args.force:
            current_parts = [int(p) for p in authoritative.split("-")[0].split(".")]
            new_parts = [int(p) for p in args.new_version.split("-")[0].split(".")]
            if new_parts <= current_parts:
                print(
                    f"error: {args.new_version} is not newer than {authoritative} (use --force to override)",
                    file=sys.stderr,
                )
                return 2
        bump(args.new_version, args.dry_run)
        verb = "would set" if args.dry_run else "set"
        print(f"{verb} version {args.new_version} in {len(locations)} location(s)")
        print("next: add a CHANGELOG.md entry and a RELEASE-NOTES.md section, then commit and tag:")
        print(f"  git commit -am 'chore(release): v{args.new_version}'")
        print(f"  git tag -a v{args.new_version} -m 'ResearchX v{args.new_version}' && git push origin v{args.new_version}")
        return 0

    # --check (also the default when nothing else is requested)
    ok = True
    print(f"authoritative version (SKILL.md metadata): {authoritative or 'MISSING'}\n")
    for label, version in locations:
        status = "ok" if version == authoritative else "MISMATCH"
        if version != authoritative:
            ok = False
        print(f"  [{status:>8}] {label}: {version or 'MISSING'}")

    if authoritative:
        if authoritative not in changelog_versions():
            print(f"\n  [MISMATCH] CHANGELOG.md has no `## [{authoritative}]` entry")
            ok = False
        else:
            print(f"\n  [      ok] CHANGELOG.md entry for {authoritative}")
        if release_notes_versions():
            if authoritative not in release_notes_versions():
                print(f"  [MISMATCH] RELEASE-NOTES.md has no `## v{authoritative}` section")
                ok = False
            else:
                print(f"  [      ok] RELEASE-NOTES.md section for {authoritative}")
        else:
            print("  [   warn] RELEASE-NOTES.md missing or empty")

    print("\n" + ("version consistency: OK" if ok else f"version drift detected ({len(versions)} distinct versions)"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
