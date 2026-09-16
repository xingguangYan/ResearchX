.PHONY: help test validate check mcp clean demo

PY ?= python3

help:
	@echo "ResearchX — make targets"
	@echo "  make test       run the offline pytest suite"
	@echo "  make validate   validate the skill against the Agent Skills spec"
	@echo "  make check      validate + test + JSON manifests"
	@echo "  make demo       run the citation verifier on a sample bibliography (needs network, cached)"
	@echo "  make mcp        start the MCP server (stdio)"

test:
	$(PY) -m pytest tests -q

validate:
	$(PY) tests/validate_skill.py --strict

manifests:
	$(PY) -c "import json,glob; [json.load(open(f)) for f in glob.glob('.claude-plugin/*.json')+glob.glob('.codex-plugin/*.json')+glob.glob('.cursor-plugin/*.json')+['gemini-extension.json','mcp-server/package.json']]; print('manifests valid')"

check: validate test manifests

demo:
	$(PY) skills/researchx/scripts/search_literature.py --query "foundation model remote sensing" --from-year 2024 --limit 5 --format md
	$(PY) skills/researchx/scripts/verify_citations.py skills/researchx/references/citation-verification.md --format text --max-refs 5

mcp:
	$(PY) mcp-server/researchx_mcp_server.py

clean:
	rm -rf .researchx-cache .pytest_cache **/__pycache__
