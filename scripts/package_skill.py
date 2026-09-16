#!/usr/bin/env python3
"""ResearchX — build the release artifacts attached to a GitHub Release.

Produces deterministic archives of the skill (and optionally the MCP server) with a
SHA256SUMS file, so a user can install without cloning:

    researchx-skill-v4.0.0.zip       skills/researchx/** (drop-in skill directory)
    researchx-skill-v4.0.0.tar.gz    same content, tar flavour
    researchx-mcp-v4.0.0.tar.gz      MCP server + the scripts it calls
    SHA256SUMS                        checksums for the above

Deterministic = sorted entries, fixed timestamps and permissions, so re-running on the same
commit reproduces the same bytes (verifiable by anyone).

Usage
-----
  python scripts/package_skill.py                      # writes dist/ for the current version
  python scripts/package_skill.py --out /tmp/rel --skip-mcp
  python scripts/package_skill.py --check              # report the expected artifacts without writing
  python scripts/package_skill.py --version 4.1.0      # override the version (defaults to SKILL.md)

Exit codes: 0 = built, 1 = build problem, 2 = usage error.
"""

from __future__ import annotations

import argparse
import contextlib
import gzip
import hashlib
import io
import re
import sys
import tarfile
import zipfile
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

REPO = Path(__file__).resolve().parents[1]
FIXED_TIME = (2026, 1, 1, 0, 0, 0)  # deterministic mtime for reproducible archives
EXCLUDE = {"__pycache__", ".pytest_cache", ".researchx-cache", ".DS_Store"}


def current_version() -> Optional[str]:
    text = (REPO / "skills/researchx/SKILL.md").read_text(encoding="utf-8")
    match = re.search(r"^\s+version:\s*[\"']?([0-9][0-9A-Za-z.\-]*)[\"']?\s*$", text, re.M)
    return match.group(1) if match else None


def iter_files(root: Path) -> List[Path]:
    files = [
        path
        for path in sorted(root.rglob("*"))
        if path.is_file() and not any(part in EXCLUDE for part in path.parts)
    ]
    return files


def archive_name(path: Path, root: Path, prefix: str) -> str:
    """Archive member name: the directory the user copies, not the repo path."""
    return f"{prefix}/{path.relative_to(root)}"


def add_to_zip(archive: zipfile.ZipFile, files: Iterable[Path], root: Path, prefix: str) -> None:
    for path in files:
        info = zipfile.ZipInfo(archive_name(path, root, prefix), date_time=FIXED_TIME)
        info.external_attr = (0o755 if path.suffix == ".py" else 0o644) << 16
        info.compress_type = zipfile.ZIP_DEFLATED
        archive.writestr(info, path.read_bytes())


def add_to_tar(archive: tarfile.TarFile, files: Iterable[Path], root: Path, prefix: str) -> None:
    for path in files:
        data = path.read_bytes()
        info = tarfile.TarInfo(archive_name(path, root, prefix))
        info.size = len(data)
        info.mtime = 0
        info.mode = 0o755 if path.suffix == ".py" else 0o644
        info.uid = info.gid = 0
        info.uname = info.gname = "researchx"
        archive.addfile(info, io.BytesIO(data))


@contextlib.contextmanager
def open_deterministic_tar(path: Path):
    """tar.gz with a fixed gzip mtime/name, so rebuilds produce identical bytes.

    tarfile in stream mode does not close a fileobj it was handed, and gzip buffers, so both
    layers are closed explicitly — otherwise the checksum of the archive would be computed
    from a partially flushed file.
    """
    raw = open(path, "wb")
    gz = gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0, compresslevel=9)
    tar = tarfile.open(fileobj=gz, mode="w|")
    try:
        yield tar
    finally:
        tar.close()
        gz.close()
        raw.close()


def build(version: str, out_dir: Path, skip_mcp: bool = False, quiet: bool = False) -> List[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    skill_root = REPO / "skills/researchx"
    if not (skill_root / "SKILL.md").exists():
        raise SystemExit("error: skills/researchx/SKILL.md not found — run from the repository root")

    skill_files = iter_files(skill_root)
    artifacts: List[Path] = []

    zip_path = out_dir / f"researchx-skill-v{version}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        add_to_zip(archive, skill_files, skill_root, "researchx")
    artifacts.append(zip_path)

    tar_path = out_dir / f"researchx-skill-v{version}.tar.gz"
    with open_deterministic_tar(tar_path) as archive:
        add_to_tar(archive, skill_files, skill_root, f"researchx-{version}/researchx")
    artifacts.append(tar_path)

    if not skip_mcp:
        mcp_files = iter_files(REPO / "mcp-server") + iter_files(REPO / "skills/researchx/scripts")
        mcp_tar = out_dir / f"researchx-mcp-v{version}.tar.gz"
        with open_deterministic_tar(mcp_tar) as archive:
            for path in mcp_files:
                data = path.read_bytes()
                info = tarfile.TarInfo(f"researchx-mcp-{version}/{path.relative_to(REPO)}")
                info.size = len(data)
                info.mtime = 0
                info.mode = 0o755 if path.suffix == ".py" else 0o644
                info.uid = info.gid = 0
                info.uname = info.gname = "researchx"
                archive.addfile(info, io.BytesIO(data))
        artifacts.append(mcp_tar)

    sums = out_dir / "SHA256SUMS"
    sums.write_text(
        "".join(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}\n" for path in artifacts),
        encoding="utf-8",
    )
    artifacts.append(sums)

    if not quiet:
        for path in artifacts:
            size = path.stat().st_size
            print(f"{path.relative_to(REPO.parent) if str(path).startswith(str(REPO.parent)) else path}"
                  f"  ({size:,} bytes)")
    return artifacts


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="package_skill.py",
        description="Build the ResearchX release artifacts (deterministic zip/tar.gz + SHA256SUMS).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--version", default=None, help="override the version (default: SKILL.md metadata)")
    parser.add_argument("--out", "-o", default=str(REPO / "dist"), help="output directory (default: dist/)")
    parser.add_argument("--skip-mcp", action="store_true", help="skip the MCP server archive")
    parser.add_argument("--check", action="store_true", help="print the artifact list without writing")
    parser.add_argument("--quiet", "-q", action="store_true")
    args = parser.parse_args(argv)

    version = args.version or current_version()
    if not version:
        print("error: could not determine the version — pass --version", file=sys.stderr)
        return 2

    if args.check:
        names = [
            f"researchx-skill-v{version}.zip",
            f"researchx-skill-v{version}.tar.gz",
        ]
        if not args.skip_mcp:
            names.append(f"researchx-mcp-v{version}.tar.gz")
        names.append("SHA256SUMS")
        for name in names:
            print(f"would build {Path(args.out) / name}")
        return 0

    build(version, Path(args.out), skip_mcp=args.skip_mcp, quiet=args.quiet)
    if not args.quiet:
        print(f"\nRelease artifacts for v{version} are in {args.out}/")
        print("Attach them to the GitHub Release:")
        print(f"  gh release create v{version} --notes-file release_body.md {args.out}/*")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
