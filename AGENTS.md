# Repository guide for coding agents

ResearchX is an **Agent Skill** (SKILL.md + references + templates + stdlib Python tools) that runs the
research lifecycle for the user. The skill is the product; the repo is its packaging, tests and docs.

## Layout

```
skills/researchx/          # THE SKILL — what gets loaded by Claude Code / Codex / Cursor / Gemini CLI
├── SKILL.md               # entry point: contract, routing, gates, module summaries (<500 lines)
├── references/            # deep material, loaded on demand (modules, verification, PRISMA, journals…)
├── assets/                # output templates the agent fills in
├── scripts/               # stdlib-only CLIs (verify_citations, search_literature, prisma_screen, …)
└── evals/                 # trigger/behaviour cases used to check the skill still works
.claude-plugin/            # Claude Code marketplace + plugin manifests (one-command install)
.codex-plugin/ .cursor-plugin/ gemini-extension.json   # other platforms' manifests
mcp-server/                # optional MCP server exposing the tools to MCP clients
tests/                     # offline pytest suite + Agent Skills spec validator
platforms/                 # thin per-platform rule files (Cursor, Cline, Continue, Windsurf…)
docs/                      # install guide, comparison, roadmap, launch kit
```

## Invariants — do not break these

1. `skills/researchx/SKILL.md` frontmatter: `name` must equal the directory name (`researchx`),
   `description` ≤ 1024 chars, body < 500 lines. Platform-specific keys belong in `metadata`.
2. Every file referenced by SKILL.md must exist, and paths must be relative to the skill root.
3. Scripts are **standard-library only**, non-interactive, support `--help`, print machine-readable output
   with `--format json`, and never raise a traceback at the user for a network failure.
4. `scripts/verify_citations.py` may never claim a reference is fabricated — `NOT_FOUND` means
   "not verified", and the report says so.
5. No fabricated references, numbers, datasets, or results anywhere in docs, examples, or templates.
6. Tests must pass offline: registry access goes through the injectable `rx_common.Net` transport.

## Releases

- `scripts/bump_version.py` owns the version (SKILL.md `metadata.version` is authoritative;
  `--check` verifies all eleven locations, `--set X.Y.Z` updates them, `--tag vX.Y.Z` gates a release).
- `scripts/package_skill.py` builds the deterministic release archives; `scripts/extract_release_notes.py`
  produces the GitHub Release body from `RELEASE-NOTES.md`.
- Never hand-edit a version in one file only, and never tag a version that `--check` rejects.
- Any change to the version plumbing must keep `tests/test_release.py` green (it rebuilds the archives
  twice and compares bytes).

## Workflow

```bash
make test        # pytest suite (offline, uses recorded registry fixtures)
make validate    # Agent Skills spec + repo hygiene checks
make check       # both, plus manifests and version consistency
make dist        # build release artifacts + print the publish command
```

When changing a script: update `--help`, the docstring, the SKILL.md table entry, and `references/gotchas.md`
if behaviour is surprising. When changing behaviour described in SKILL.md, keep SKILL.md and
`references/modules.md` in sync — the agent reads both.

## Commits

Conventional-ish prefixes (`feat:`, `fix:`, `docs:`, `test:`, `chore:`) and a one-line summary of the
*research capability* affected, e.g. `fix: prisma dedupe no longer drops records without a DOI`.
