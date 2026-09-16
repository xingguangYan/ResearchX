.PHONY: help test validate check mcp clean demo version release-check package notes dist

PY ?= python3

help:
	@echo "ResearchX — make targets"
	@echo "  make test           run the offline pytest suite"
	@echo "  make validate       validate the skill against the Agent Skills spec"
	@echo "  make check          validate + test + JSON manifests + version consistency"
	@echo "  make demo           run the citation verifier on a sample bibliography (needs network, cached)"
	@echo "  make mcp            start the MCP server (stdio)"
	@echo "  make version        print the current version"
	@echo "  make release-check  version consistency + notes + tag readiness"
	@echo "  make package        build the release artifacts into dist/"
	@echo "  make notes          print this version's release notes (release body)"
	@echo "  make dist           package + notes + the exact gh command to publish"

test:
	$(PY) -m pytest tests -q

validate:
	$(PY) tests/validate_skill.py --strict

manifests:
	$(PY) -c "import json,glob; [json.load(open(f)) for f in glob.glob('.claude-plugin/*.json')+glob.glob('.codex-plugin/*.json')+glob.glob('.cursor-plugin/*.json')+['gemini-extension.json','mcp-server/package.json']]; print('manifests valid')"

check: validate test manifests release-check

version:
	$(PY) scripts/bump_version.py --current

release-check:
	$(PY) scripts/bump_version.py --check
	$(PY) scripts/extract_release_notes.py --current > /dev/null && echo "release notes: OK"

package:
	$(PY) scripts/package_skill.py --out dist

notes:
	$(PY) scripts/extract_release_notes.py --current

dist: package notes
	@echo "publish with: gh release create v$$($(PY) scripts/bump_version.py --current) --notes-file RELEASES_BODY.md dist/*"

demo:
	$(PY) skills/researchx/scripts/search_literature.py --query "foundation model remote sensing" --from-year 2024 --limit 5 --format md
	$(PY) skills/researchx/scripts/verify_citations.py skills/researchx/references/citation-verification.md --format text --max-refs 5

mcp:
	$(PY) mcp-server/researchx_mcp_server.py

clean:
	rm -rf .researchx-cache .pytest_cache dist **/__pycache__
