"""Guardrails: the skill package must stay spec-compliant and self-consistent."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SKILL_DIR = REPO / "skills" / "researchx"
SKILL_MD = SKILL_DIR / "SKILL.md"


def read_frontmatter(text: str) -> dict:
    raw = text.split("---", 2)[1]
    data = {}
    key = None
    for line in raw.splitlines():
        if not line.strip():
            continue
        if re.match(r"^[a-zA-Z_-]+:", line):
            key, _, value = line.partition(":")
            key = key.strip()
            data[key] = value.strip().strip('"')
        elif key:
            data[key] += " " + line.strip().strip('"')
    return data


@pytest.fixture(scope="module")
def skill_text():
    return SKILL_MD.read_text(encoding="utf-8")


def test_name_matches_directory(skill_text):
    front = read_frontmatter(skill_text)
    assert front["name"] == SKILL_DIR.name == "researchx"
    assert re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", front["name"])


def test_description_budget_and_keywords(skill_text):
    description = read_frontmatter(skill_text)["description"]
    assert len(description) <= 1024
    lowered = description.lower()
    for keyword in ("citation", "literature", "manuscript", "grant", "review"):
        assert keyword in lowered, f"description is missing the trigger keyword {keyword!r}"


def test_body_budget(skill_text):
    body = skill_text.split("---", 2)[2]
    assert body.count("\n") < 500, "SKILL.md body exceeded 500 lines — move detail into references/"


def test_required_files_exist():
    for relative in (
        "references/modules.md",
        "references/citation-verification.md",
        "references/search-queries.md",
        "references/journal-playbook.md",
        "references/research-design.md",
        "references/systematic-review-prisma.md",
        "references/integrity-and-ethics.md",
        "references/gotchas.md",
        "scripts/verify_citations.py",
        "scripts/search_literature.py",
        "scripts/prisma_screen.py",
        "scripts/analyze_methods.py",
        "scripts/generate_visuals.py",
        "scripts/rx_common.py",
    ):
        assert (SKILL_DIR / relative).exists(), f"missing {relative}"


def test_every_referenced_file_exists(skill_text):
    for ref in set(re.findall(r"`((?:references|scripts)/[\w./-]+)`", skill_text)):
        assert (SKILL_DIR / ref).exists(), f"SKILL.md points at missing {ref}"


def test_assets_templates_present():
    templates = sorted((SKILL_DIR / "assets").glob("*.md"))
    assert len(templates) >= 5, "expected output templates in assets/"


def _stdlib_names():
    """sys.stdlib_module_names exists from Python 3.10; fall back to a known-good set."""
    names = getattr(sys, "stdlib_module_names", None)
    if names:
        return set(names)
    return {
        "__future__", "argparse", "ast", "csv", "datetime", "difflib", "hashlib", "io", "json", "math",
        "os", "pathlib", "re", "subprocess", "sys", "textwrap", "time", "unicodedata",
        "urllib", "xml", "collections", "itertools", "typing", "unittest", "random",
        "shutil", "tempfile", "traceback", "warnings", "types", "abc", "copy", "enum",
    }


def test_scripts_are_stdlib_only_and_non_interactive():
    import ast

    for script in (SKILL_DIR / "scripts").glob("*.py"):
        source = script.read_text(encoding="utf-8")
        tree = ast.parse(source)
        assert ast.get_docstring(tree), f"{script.name} lacks a module docstring"
        modules, calls_input = [], False
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                modules += [alias.name.split(".")[0] for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                modules.append(node.module.split(".")[0])
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "input":
                calls_input = True
        assert not calls_input, f"{script.name} prompts interactively"
        for module in modules:
            assert module in _stdlib_names() or module in {"rx_common"}, (
                f"{script.name} imports non-stdlib {module}"
            )


def test_scripts_respond_to_help():
    for script in sorted((SKILL_DIR / "scripts").glob("*.py")):
        result = subprocess.run(
            [sys.executable, str(script), "--help"], capture_output=True, text=True, timeout=60
        )
        assert result.returncode == 0, f"{script.name} --help failed: {result.stderr[:200]}"
        assert "usage:" in result.stdout.lower() or "options:" in result.stdout.lower()


def test_marketplace_manifest_points_at_repo_root():
    payload = json.loads((REPO / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
    assert payload["name"]
    assert payload["plugins"], "marketplace must list the plugin"
    entry = payload["plugins"][0]
    assert entry["source"] == "./"
    assert entry["name"] == "researchx"


def test_plugin_manifests_agree_with_skill(tmp_path):
    versions = set()
    for path in (REPO / ".claude-plugin" / "plugin.json", REPO / ".codex-plugin" / "plugin.json",
                 REPO / ".cursor-plugin" / "plugin.json"):
        assert path.exists(), f"missing {path.relative_to(REPO)}"
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload["name"] == "researchx"
        versions.add(payload.get("version"))
    assert len(versions) == 1, f"plugin versions disagree: {versions}"


def test_readme_has_one_command_installs():
    readme = (REPO / "README.md").read_text(encoding="utf-8")
    assert "/plugin marketplace add xingguangYan/ResearchX" in readme
    assert "skills/researchx" in readme
    assert "ResearchX" in readme


def test_no_stale_paths_in_docs():
    """The v4 layout moved ResearchX/ to skills/researchx/ — old paths must not linger."""
    for path in list(REPO.glob("*.md")) + list((REPO / "docs").glob("*.md")) + [
        REPO / ".github" / "workflows" / "validate.yml"
    ]:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for stale in (
            "ResearchX/scripts/",
            "ResearchX/references/",
            "ResearchX/assets/",
            "ResearchX/SKILL.md",
            "ResearchX\\ResearchX",
        ):
            assert stale not in text, f"{path.name} still references {stale}"


def test_validator_passes_without_stdlib_module_names():
    """Python 3.9 has no sys.stdlib_module_names — the validator's fallback must still pass."""
    program = (
        "import sys\n"
        "if hasattr(sys, 'stdlib_module_names'):\n"
        "    del sys.stdlib_module_names\n"
        "sys.argv = ['validate_skill.py', '--strict']\n"
        "exec(compile(open('tests/validate_skill.py').read(), 'validate_skill.py', 'exec'))\n"
    )
    proc = subprocess.run(
        [sys.executable, "-c", program], cwd=REPO, capture_output=True, text=True, timeout=300
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_validate_skill_passes():
    result = subprocess.run(
        [sys.executable, str(REPO / "tests" / "validate_skill.py")],
        capture_output=True,
        text=True,
        cwd=REPO,
        timeout=180,
    )
    assert result.returncode == 0, result.stdout + result.stderr
