# Contributing to ResearchX

The goal: make ResearchX the most *trustworthy* research assistant — one that never hands a researcher a
citation, number or claim they cannot check. Contributions that increase trust or reach are the most
valuable.

## Highest-value contributions

| Area | Examples |
|---|---|
| **Verification robustness** | new registry adapters (PubMed/Europe PMC, DBLP, Semantic Scholar, DataCite), better non-Latin title matching, author-disambiguation, retraction sources |
| **Screening & reviews** | RIS/BibTeX import, full-text PDF screening, risk-of-bias templates, meta-analysis statistics |
| **Discipline modules** | clinical (CONSORT/STROBE/PRISMA-P), chemistry, materials, humanities, law, economics |
| **Language coverage** | Chinese (CNKI/万方 query patterns, GB/T 7714 output), Spanish, Portuguese, Arabic, Japanese workflows |
| **Platforms** | new agent plugin manifests, MCP tool coverage, editor integrations |
| **Evaluations** | trigger cases, rubric-based output tests, regression fixtures from real reviewer comments |

## Ground rules

1. **No fabrication anywhere** — not in examples, not in templates, not in documentation. If you need a
   sample reference, use a real one and verify it.
2. Scripts: standard library only, non-interactive, `--help` documented, `--format json`, graceful network
   failure, deterministic given the same inputs.
3. Tests must pass offline (`make test`). Add fixtures instead of hitting the network.
4. Keep `SKILL.md` under 500 lines and spec-valid (`make validate`); deep material goes in `references/`.
5. Don't add dependencies the user has to install; if unavoidable, make it optional and documented.

## Workflow

```bash
git clone https://github.com/xingguangYan/ResearchX && cd ResearchX
make check                 # tests + spec validation, offline
make test                  # pytest only
python tests/validate_skill.py --strict
```

1. Fork, branch (`feat/…`, `fix/…`, `docs/…`).
2. Make the change; add or update tests and fixtures.
3. Update the docs that describe the behaviour: `SKILL.md`, `references/*`, `README.md`, `CHANGELOG.md`.
4. Open a PR explaining the research workflow it improves, and how you tested it.

## Release checklist (maintainers)

```bash
python scripts/bump_version.py --set X.Y.Z     # bumps SKILL.md, manifests, constants, CITATION.cff
$EDITOR CHANGELOG.md RELEASE-NOTES.md          # developer history + user-facing notes (Install/Verify/Limitations)
make check                                     # spec validator, tests, manifests, version consistency
python scripts/package_skill.py --out dist     # optional local check of the artifacts
git commit -am "chore(release): vX.Y.Z"
git tag -a vX.Y.Z -m "ResearchX vX.Y.Z" && git push origin main --follow-tags
```

The tag triggers `.github/workflows/release.yml` (validate → test → tag/version gate → build → publish).
Notes must state what changed, how to install/upgrade, and the known limitations — a release without
limitations is a release nobody trusts.

## Reporting problems

Open an issue with: the command or prompt you ran, the input, the observed output, and what you expected.
For wrong verdicts from `verify_citations.py`, include the DOI/title so the case can become a fixture.

## Review criteria

- Does it make the agent more correct (verification, honesty, specificity) or more useful (new workflow,
  less friction)?
- Would a reviewer trust the output more?
- Is it testable offline?
- Does it respect the integrity rules in `references/integrity-and-ethics.md`?
