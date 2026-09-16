#!/usr/bin/env python3
"""Validate the ResearchX skill against the Agent Skills spec + repo hygiene rules.

Usage:
    python tests/validate_skill.py [--skill-dir skills/researchx] [--repo .] [--strict]

Exit code 0 = valid, 1 = errors found (warnings alone do not fail unless --strict).

Checks
------
spec:      name/description present, name matches directory, length limits, kebab-case
structure: SKILL.md, references/, scripts/, assets/ exist; referenced files exist
budget:    SKILL.md body < 500 lines and < 6000 tokens (approx), description <= 1024 chars
scripts:   every script has a module docstring, --help works, no interactive input(),
           no third-party imports outside the allowed list
manifests: JSON manifests parse; marketplace/plugin names agree
docs:      README documents one-command install per platform, LICENSE exists
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple

def _imports_and_calls(source: str):
    """Return (module names, whether the code calls input())."""
    import ast

    tree = ast.parse(source)
    modules = []
    calls_input = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules += [alias.name.split(".")[0] for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.level == 0:
                modules.append(node.module.split(".")[0])
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "input":
            calls_input = True
    return modules, calls_input

ALLOWED_THIRD_PARTY = set()  # scripts must be standard-library only

FALLBACK_STDLIB = {
    "__future__", "argparse", "ast", "collections", "csv", "datetime", "difflib", "hashlib", "io",
    "json", "math", "os", "pathlib", "random", "re", "shutil", "subprocess", "sys", "tempfile",
    "textwrap", "time", "typing", "unicodedata", "urllib", "xml",
}
ALLOWED_IMPORTS = FALLBACK_STDLIB | {"rx_common", "skills_ref", "researchx"}

FRONTMATTER_KEYS_OK = {
    "name", "description", "license", "compatibility", "metadata", "allowed-tools",
    "version", "author", "homepage", "keywords",
}

REQUIRED_REFERENCE_FILES = [
    "references/modules.md",
    "references/citation-verification.md",
    "references/search-queries.md",
    "references/journal-playbook.md",
    "references/research-design.md",
    "references/systematic-review-prisma.md",
    "references/integrity-and-ethics.md",
    "references/gotchas.md",
]

REQUIRED_SCRIPTS = [
    "scripts/verify_citations.py",
    "scripts/search_literature.py",
    "scripts/prisma_screen.py",
    "scripts/analyze_methods.py",
    "scripts/generate_visuals.py",
]


def parse_frontmatter(text: str) -> Tuple[Dict[str, str], str]:
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    raw, body = parts[1], parts[2]
    data: Dict[str, str] = {}
    key = None
    buffer: List[str] = []
    for line in raw.splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        if re.match(r"^[a-zA-Z_-]+:", line):
            if key:
                data[key] = " ".join(buffer).strip()
            key, _, value = line.partition(":")
            key = key.strip()
            buffer = [value.strip().strip('"').strip("'")]
        elif key:
            buffer.append(line.strip().strip('"').strip("'"))
    if key:
        data[key] = " ".join(buffer).strip()
    return data, body


def validate(skill_dir: Path, repo: Path, strict: bool) -> int:
    errors: List[str] = []
    warnings: List[str] = []

    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        print(f"ERROR: {skill_md} not found")
        return 1
    text = skill_md.read_text(encoding="utf-8")
    front, body = parse_frontmatter(text)

    # --- frontmatter ------------------------------------------------------- #
    name = front.get("name", "")
    description = front.get("description", "")
    if not name:
        errors.append("frontmatter: missing `name`")
    if not description:
        errors.append("frontmatter: missing `description`")
    if name and not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name):
        errors.append(f"frontmatter: `name` must be lowercase kebab-case, got {name!r}")
    if name and name != skill_dir.name:
        errors.append(f"frontmatter: `name` ({name}) must match directory ({skill_dir.name})")
    if len(name) > 64:
        errors.append("frontmatter: `name` longer than 64 characters")
    if len(description) > 1024:
        errors.append(f"frontmatter: `description` is {len(description)} chars (max 1024)")
    if len(description) < 80:
        warnings.append("frontmatter: `description` is short — trigger keywords may be missing")
    for key in front:
        if key not in FRONTMATTER_KEYS_OK:
            warnings.append(f"frontmatter: non-standard key {key!r} (move agent-specific data into metadata)")
    if "metadata" not in front:
        warnings.append("frontmatter: no `metadata` block (version/author/homepage are useful)")

    # --- size budget ------------------------------------------------------- #
    body_lines = body.count("\n")
    approx_tokens = len(body) // 4
    if body_lines > 500:
        errors.append(f"budget: SKILL.md body is {body_lines} lines (max 500)")
    if approx_tokens > 6000:
        warnings.append(f"budget: SKILL.md body ~{approx_tokens} tokens (recommended < 5000)")

    # --- structure --------------------------------------------------------- #
    for required in REQUIRED_REFERENCE_FILES + REQUIRED_SCRIPTS:
        if not (skill_dir / required).exists():
            errors.append(f"structure: missing {required}")
    if not (skill_dir / "assets").is_dir():
        warnings.append("structure: no assets/ directory (output templates help consistency)")

    referenced = set(re.findall(r"`((?:references|scripts|assets)/[\w./-]+)`", text))
    for ref in sorted(referenced):
        if not (skill_dir / ref).exists():
            errors.append(f"structure: SKILL.md references missing file {ref}")

    glob_refs = set(re.findall(r"`(assets/\*\.md)`", text))
    if glob_refs and not list((skill_dir / "assets").glob("*.md")):
        errors.append("structure: SKILL.md points at assets/*.md but assets/ has no markdown templates")

    # --- scripts ----------------------------------------------------------- #
    import ast

    for script in sorted((skill_dir / "scripts").glob("*.py")):
        source = script.read_text(encoding="utf-8")
        try:
            tree = ast.parse(source)
            if not ast.get_docstring(tree):
                warnings.append(f"scripts: {script.name} has no module docstring")
        except SyntaxError as exc:
            errors.append(f"scripts: {script.name} does not parse ({exc})")
            continue
        modules, calls_input = _imports_and_calls(source)
        if calls_input:
            errors.append(f"scripts: {script.name} calls input() — scripts must be non-interactive")
        stdlib_names = set(getattr(sys, "stdlib_module_names", None) or ()) | FALLBACK_STDLIB
        for module in modules:
            if module not in stdlib_names and module not in ALLOWED_THIRD_PARTY and module not in ALLOWED_IMPORTS:
                errors.append(f"scripts: {script.name} imports third-party module {module!r}")
        try:
            result = subprocess.run(
                [sys.executable, str(script), "--help"],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode != 0:
                errors.append(f"scripts: {script.name} --help exited {result.returncode}")
            elif "--" not in result.stdout:
                warnings.append(f"scripts: {script.name} --help has no documented options")
        except subprocess.TimeoutExpired:
            errors.append(f"scripts: {script.name} --help timed out")

    # --- manifests --------------------------------------------------------- #
    marketplace_path = repo / ".claude-plugin" / "marketplace.json"
    plugin_path = repo / ".claude-plugin" / "plugin.json"
    if not marketplace_path.exists():
        errors.append("manifests: .claude-plugin/marketplace.json missing (blocks one-command install)")
    if not plugin_path.exists():
        errors.append("manifests: .claude-plugin/plugin.json missing")
    for path in (marketplace_path, plugin_path, repo / ".codex-plugin" / "plugin.json",
                 repo / ".cursor-plugin" / "plugin.json", repo / "gemini-extension.json"):
        if not path.exists():
            warnings.append(f"manifests: {path.relative_to(repo)} not present (platform coverage)")
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"manifests: {path.relative_to(repo)} is invalid JSON ({exc})")
            continue
        if path.name == "marketplace.json":
            if not payload.get("plugins"):
                errors.append("manifests: marketplace.json lists no plugins")
            for entry in payload.get("plugins", []):
                for field in ("name", "source", "description"):
                    if not entry.get(field):
                        errors.append(f"manifests: marketplace plugin entry missing {field!r}")

    # --- docs -------------------------------------------------------------- #
    readme = repo / "README.md"
    if not readme.exists():
        errors.append("docs: README.md missing")
    else:
        readme_text = readme.read_text(encoding="utf-8")
        for needle in ("marketplace add", "install", "ResearchX"):
            if needle.lower() not in readme_text.lower():
                warnings.append(f"docs: README does not mention {needle!r}")
    if not (repo / "LICENSE").exists():
        errors.append("docs: LICENSE file missing")

    # --- report ------------------------------------------------------------ #
    for warning in warnings:
        print(f"WARN  {warning}")
    for error in errors:
        print(f"ERROR {error}")
    print(f"\n{len(errors)} error(s), {len(warnings)} warning(s) — {'FAIL' if errors else 'PASS'}")

    if errors or (strict and warnings):
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the ResearchX skill package.")
    parser.add_argument("--skill-dir", default="skills/researchx")
    parser.add_argument("--repo", default=".")
    parser.add_argument("--strict", action="store_true", help="treat warnings as errors")
    args = parser.parse_args()
    repo = Path(args.repo).resolve()
    skill_dir = (repo / args.skill_dir).resolve()
    if not skill_dir.is_dir():
        print(f"ERROR skill directory not found: {skill_dir}")
        return 1
    return validate(skill_dir, repo, args.strict)


if __name__ == "__main__":
    raise SystemExit(main())
