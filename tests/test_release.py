"""Release system: version consistency, notes, deterministic artifacts, workflow wiring."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "scripts"


def run(script: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / script), *args],
        cwd=REPO, capture_output=True, text=True, timeout=300,
    )


def current_version() -> str:
    return run("bump_version.py", "--current").stdout.strip()


# --------------------------------------------------------------------------- #
# Version consistency                                                         #
# --------------------------------------------------------------------------- #


def test_all_versions_agree():
    result = run("bump_version.py", "--check")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "version consistency: OK" in result.stdout


def test_version_locations_are_comprehensive():
    """Every manifest/constant that carries a version must be covered by the checker."""
    output = run("bump_version.py", "--check").stdout
    for expected in (
        "skills/researchx/SKILL.md",
        ".claude-plugin/plugin.json",
        ".claude-plugin/marketplace.json",
        ".codex-plugin/plugin.json",
        ".cursor-plugin/plugin.json",
        "gemini-extension.json",
        "mcp-server/package.json",
        "mcp-server/pyproject.toml",
        "SERVER_VERSION",
        "CITATION.cff",
    ):
        assert expected in output, f"version checker does not cover {expected}"


def test_tag_check_accepts_matching_tag_and_rejects_others():
    version = current_version()
    assert run("bump_version.py", "--check", "--tag", f"v{version}").returncode == 0
    mismatch = run("bump_version.py", "--check", "--tag", "v99.0.0")
    assert mismatch.returncode == 1
    assert "does not match the repository version" in mismatch.stderr


def test_bump_refuses_to_go_backwards(tmp_path):
    result = run("bump_version.py", "--set", "0.0.1")
    assert result.returncode == 2
    assert "not newer" in result.stderr


def test_set_is_reversible_and_dry_run_is_safe():
    version = current_version()
    dry = run("bump_version.py", "--set", "9.9.9", "--dry-run")
    assert dry.returncode == 0
    assert current_version() == version, "a dry run must not modify files"
    # the dry run must not have left a pending changelog/notes requirement either
    assert run("bump_version.py", "--check").returncode == 0


# --------------------------------------------------------------------------- #
# Release notes                                                               #
# --------------------------------------------------------------------------- #


def test_release_notes_cover_the_current_version():
    version = current_version()
    notes = (REPO / "RELEASE-NOTES.md").read_text(encoding="utf-8")
    assert re.search(rf"^## v{re.escape(version)}\b", notes, re.M), "no section for the current version"
    assert "RELEASE-NOTES.md" in notes  # self-reference in the process section
    for required in ("### Install", "### Verify", "### Known limitations"):
        assert required in notes, f"release notes are missing {required!r}"


def test_release_notes_document_install_and_upgrade_paths():
    notes = (REPO / "RELEASE-NOTES.md").read_text(encoding="utf-8")
    assert "plugin marketplace add xingguangYan/ResearchX" in notes
    assert "skills/researchx" in notes
    assert "verify_citations.py" in notes


def test_extract_release_notes_returns_the_current_section():
    version = current_version()
    notes = run("extract_release_notes.py", f"v{version}")
    assert notes.returncode == 0, notes.stderr
    assert notes.stdout.startswith(f"## v{version}")
    assert "Install" in notes.stdout

    changelog = run("extract_release_notes.py", "--source", "changelog", "--current")
    assert changelog.returncode == 0, changelog.stderr
    assert f"[{version}]" in changelog.stdout


def test_extract_release_notes_fails_cleanly_for_unknown_version():
    result = run("extract_release_notes.py", "v0.0.0-nope")
    assert result.returncode == 1
    assert "no section for" in result.stderr


def test_changelog_has_an_entry_per_release_note_section():
    changelog = (REPO / "CHANGELOG.md").read_text(encoding="utf-8")
    versions = re.findall(r"^##\s*\[([0-9][0-9A-Za-z.\-]*)\]", changelog, re.M)
    notes = re.findall(r"^##\s*v([0-9][0-9A-Za-z.\-]*)", (REPO / "RELEASE-NOTES.md").read_text(encoding="utf-8"), re.M)
    assert versions, "CHANGELOG.md has no version entries"
    assert current_version() in versions and current_version() in notes
    latest_changelog = versions[0]
    latest_notes = notes[0]
    assert latest_changelog == latest_notes == current_version(), (
        f"newest entries disagree: changelog {latest_changelog}, notes {latest_notes}, version {current_version()}"
    )


# --------------------------------------------------------------------------- #
# Packaging                                                                   #
# --------------------------------------------------------------------------- #


def test_package_builds_expected_artifacts(tmp_path):
    version = current_version()
    result = run("package_skill.py", "--out", str(tmp_path), "--quiet")
    assert result.returncode == 0, result.stderr
    names = {path.name for path in tmp_path.iterdir()}
    assert names == {
        f"researchx-skill-v{version}.zip",
        f"researchx-skill-v{version}.tar.gz",
        f"researchx-mcp-v{version}.tar.gz",
        "SHA256SUMS",
    }
    sums = (tmp_path / "SHA256SUMS").read_text(encoding="utf-8").splitlines()
    assert len(sums) == 3
    for line in sums:
        digest, name = line.split("  ")
        assert hashlib.sha256((tmp_path / name).read_bytes()).hexdigest() == digest


def test_package_contents_are_a_drop_in_skill(tmp_path):
    version = current_version()
    run("package_skill.py", "--out", str(tmp_path), "--quiet")

    with zipfile.ZipFile(tmp_path / f"researchx-skill-v{version}.zip") as archive:
        members = archive.namelist()
        assert "researchx/SKILL.md" in members
        assert "researchx/scripts/verify_citations.py" in members
        assert "researchx/references/citation-verification.md" in members
        assert not any("__pycache__" in name for name in members)
        skill_md = archive.read("researchx/SKILL.md").decode("utf-8")
        assert "name: researchx" in skill_md

    with tarfile.open(tmp_path / f"researchx-skill-v{version}.tar.gz") as archive:
        names = archive.getnames()
        assert f"researchx-{version}/researchx/SKILL.md" in names

    with tarfile.open(tmp_path / f"researchx-mcp-v{version}.tar.gz") as archive:
        names = archive.getnames()
        assert any(name.endswith("mcp-server/researchx_mcp_server.py") for name in names)


def test_package_is_deterministic(tmp_path):
    first, second = tmp_path / "a", tmp_path / "b"
    run("package_skill.py", "--out", str(first), "--quiet")
    run("package_skill.py", "--out", str(second), "--quiet")
    for path in sorted(first.iterdir()):
        twin = second / path.name
        assert path.read_bytes() == twin.read_bytes(), f"{path.name} differs between builds"


def test_package_check_mode_lists_without_writing(tmp_path):
    result = run("package_skill.py", "--out", str(tmp_path), "--check")
    assert result.returncode == 0
    assert "would build" in result.stdout
    assert not tmp_path.exists() or not list(tmp_path.iterdir())


# --------------------------------------------------------------------------- #
# Workflow wiring                                                             #
# --------------------------------------------------------------------------- #


def test_release_workflow_is_wired_for_tag_pushes():
    workflow = (REPO / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")
    assert 'tags: ["v*"]' in workflow, "release workflow must trigger on version tags"
    assert "contents: write" in workflow, "creating a release needs contents: write"
    for step in ("bump_version.py --check --tag", "validate_skill.py --strict", "pytest", "package_skill.py",
                 "extract_release_notes.py", "gh release create"):
        assert step in workflow, f"release workflow is missing {step!r}"


def test_validate_workflow_runs_version_check():
    workflow = (REPO / ".github" / "workflows" / "validate.yml").read_text(encoding="utf-8")
    assert "bump_version.py --check" in workflow


def test_makefile_exposes_release_targets():
    makefile = (REPO / "Makefile").read_text(encoding="utf-8")
    for target in ("version:", "package:", "notes:", "release-check:"):
        assert target in makefile, f"Makefile is missing the {target} target"


def test_citation_and_license_present_for_releases():
    assert (REPO / "LICENSE").exists()
    cff = (REPO / "CITATION.cff").read_text(encoding="utf-8")
    assert f"version: {current_version()}" in cff
    assert "date-released" in cff
