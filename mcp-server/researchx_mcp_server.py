#!/usr/bin/env python3
"""ResearchX MCP server — zero dependencies, stdio transport.

Exposes the ResearchX tools to any Model Context Protocol client (Claude Desktop, Claude Code,
Cline, Continue, Zed, …) by wrapping the bundled scripts. It speaks JSON-RPC 2.0 over stdio
directly, so nothing needs to be installed (`pip install mcp` is *not* required).

Tools
-----
  verify_citations   check references against Crossref / OpenAlex / arXiv / doi.org
  search_literature  structured search with year filters and citation chaining
  prisma_screen      dedupe + rule screening + PRISMA 2020 counts, flow, ledger
  analyze_methods    method families, trends and gaps over a paper set
  generate_visuals   Mermaid diagrams, figure specs, graphical-abstract prompts
  researchx_status   environment check: skill files present, versions, offline cache

Prompts (slash-commands in supported clients)
---------------------------------------------
  research_gap_mining, manuscript_review, systematic_review, citation_audit, grant_draft

Usage
-----
  python mcp-server/researchx_mcp_server.py            # stdio server
  python mcp-server/researchx_mcp_server.py --list     # print tools and exit
  python mcp-server/researchx_mcp_server.py --selftest # offline protocol self-check

Client configuration (e.g. claude_desktop_config.json):

  {
    "mcpServers": {
      "researchx": {
        "command": "python",
        "args": ["/absolute/path/to/ResearchX/mcp-server/researchx_mcp_server.py"]
      }
    }
  }
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

SERVER_NAME = "researchx"
SERVER_VERSION = "4.0.0"
PROTOCOL_VERSION = "2025-06-18"

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = REPO_ROOT / "skills" / "researchx"
SCRIPTS = SKILL_DIR / "scripts"


def _script(name: str) -> str:
    return str(SCRIPTS / name)


def _run(script: str, args: List[str], timeout: int = 300) -> Dict[str, Any]:
    """Run a bundled script and return {ok, exit_code, stdout, stderr}."""
    if not Path(script).exists():
        return {"ok": False, "exit_code": -1, "stdout": "", "stderr": f"script not found: {script}"}
    try:
        proc = subprocess.run(
            [sys.executable, script, *args],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(REPO_ROOT),
        )
    except subprocess.TimeoutExpired:
        return {"ok": False, "exit_code": -1, "stdout": "", "stderr": f"timed out after {timeout}s"}
    return {
        "ok": proc.returncode == 0,
        "exit_code": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
    }


# --------------------------------------------------------------------------- #
# Tool registry                                                               #
# --------------------------------------------------------------------------- #

TOOLS: List[Dict[str, Any]] = [
    {
        "name": "verify_citations",
        "description": (
            "Verify that references are real. Cross-checks a document (markdown/txt/bib/json), a single DOI "
            "or a title against Crossref, OpenAlex, arXiv and the DOI handle service. Returns VERIFIED / "
            "CORRECTED / PARTIAL / NOT_FOUND / RETRACTED / ERROR per reference. NOT_FOUND means 'not found "
            "in the registries', never 'fabricated' — label those [UNVERIFIED]."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "file to audit (.md .txt .bib .json), or omit and pass doi/title"},
                "doi": {"type": "string", "description": "verify a single DOI"},
                "title": {"type": "string", "description": "verify a single title"},
                "author": {"type": "string", "description": "author hint for title search"},
                "year": {"type": "string", "description": "year hint for title search"},
                "format": {"type": "string", "enum": ["json", "md", "text"], "default": "json"},
                "offline": {"type": "boolean", "default": False, "description": "use only the local cache"},
                "mailto": {"type": "string", "description": "contact email for the polite pool"},
            },
            "required": [],
        },
    },
    {
        "name": "search_literature",
        "description": (
            "Search OpenAlex/Crossref/arXiv for real records (title, DOI, year, venue, citations, abstract). "
            "Supports keyword queries, year windows and forward/backward citation chaining. Returns JSON or "
            "a markdown matrix suitable for a literature table."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "keyword query"},
                "cited_by": {"type": "string", "description": "DOI whose citing works you want (forward chaining)"},
                "references_of": {"type": "string", "description": "DOI whose references you want (backward chaining)"},
                "from_year": {"type": "integer"},
                "to_year": {"type": "integer"},
                "limit": {"type": "integer", "default": 25},
                "sort": {"type": "string", "enum": ["relevance", "citations", "year"]},
                "format": {"type": "string", "enum": ["json", "md", "csv"], "default": "json"},
                "abstracts": {"type": "boolean", "default": False},
            },
            "required": [],
        },
    },
    {
        "name": "prisma_screen",
        "description": (
            "Reproducible screening for a literature/systematic review: dedupe by DOI and title, apply "
            "include/exclude regex rules and a year window, then emit PRISMA 2020 counts, a Mermaid flow "
            "diagram and a screening ledger with the reason for every record."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "input": {"type": "string", "description": "hits JSON/CSV from search_literature"},
                "include": {"type": "array", "items": {"type": "string"}, "description": "regexes that keep a record"},
                "exclude": {"type": "array", "items": {"type": "string"}, "description": "regexes that drop a record"},
                "from_year": {"type": "integer"},
                "to_year": {"type": "integer"},
                "type": {"type": "string", "description": "comma-separated record types to keep"},
                "out_prefix": {"type": "string", "description": "prefix for _flow.md/_ledger.csv/_counts.json/_included.json"},
                "decisions": {"type": "string", "description": "JSON {id: {decision, reason}} for human eligibility decisions"},
            },
            "required": ["input"],
        },
    },
    {
        "name": "analyze_methods",
        "description": (
            "Method mining over a paper set: method families, emergence/decline trends, recurring limitations "
            "(gaps), datasets used, and innovation dimensions. Feed it records produced by search_literature "
            "so every claim stays traceable to a DOI."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "input": {"type": "string", "description": "JSON array of {title, year, method, limitation, dataset, innovation}"},
                "format": {"type": "string", "enum": ["md", "json"], "default": "md"},
            },
            "required": ["input"],
        },
    },
    {
        "name": "generate_visuals",
        "description": (
            "Produce Mermaid workflow/PRISMA diagrams, figure specifications (size, DPI, fonts, colour-blind "
            "palettes) and graphical-abstract prompts for image models. Never invents data; tells the caller "
            "that figure values must come from real results."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "kind": {"type": "string", "enum": ["workflow", "prisma", "abstract", "poster", "figure"], "default": "workflow"},
                "topic": {"type": "string"},
                "style": {"type": "string", "description": "for abstract: nature|science|cell|rse|isprs|default"},
                "palette": {"type": "string", "description": "for figure: colorblind|default"},
                "chart": {"type": "string", "description": "for figure: map|line|bar|scatter|confusion"},
            },
            "required": ["kind"],
        },
    },
    {
        "name": "researchx_status",
        "description": "Check the ResearchX installation: script presence, versions, cache state and whether network registries are reachable.",
        "inputSchema": {"type": "object", "properties": {}},
    },
]

PROMPTS: List[Dict[str, Any]] = [
    {
        "name": "research_gap_mining",
        "description": "Find defensible research gaps and five literature-backed topics in a domain.",
        "arguments": [{"name": "topic", "description": "research domain or problem", "required": True}],
    },
    {
        "name": "manuscript_review",
        "description": "Adversarial peer review of a draft: three personas, severity, cheapest sufficient fix, response letter.",
        "arguments": [{"name": "manuscript", "description": "draft summary or path", "required": True}],
    },
    {
        "name": "systematic_review",
        "description": "Run a PRISMA 2020 review pipeline: search, dedupe, screen, counts, flow, disclosure.",
        "arguments": [{"name": "question", "description": "review question (PICO if possible)", "required": True}],
    },
    {
        "name": "citation_audit",
        "description": "Verify every reference in a document and return an audit with per-reference verdicts.",
        "arguments": [{"name": "document", "description": "path to the draft or bibliography", "required": True}],
    },
    {
        "name": "grant_draft",
        "description": "Draft a grant proposal (NSFC/international) with a cited rationale and a technical route.",
        "arguments": [{"name": "topic", "description": "proposal topic", "required": True}],
    },
]


def tool_result(text: str, is_error: bool = False) -> Dict[str, Any]:
    return {"content": [{"type": "text", "text": text}], "isError": is_error}


def call_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    arguments = arguments or {}
    if name == "verify_citations":
        args: List[str] = ["--format", arguments.get("format", "json"), "--quiet"]
        if arguments.get("path"):
            args.append(arguments["path"])
        if arguments.get("doi"):
            args += ["--doi", arguments["doi"]]
        if arguments.get("title"):
            args += ["--title", arguments["title"]]
        if arguments.get("author"):
            args += ["--author", arguments["author"]]
        if arguments.get("year"):
            args += ["--year", str(arguments["year"])]
        if arguments.get("offline"):
            args.append("--offline")
        if arguments.get("mailto"):
            args += ["--mailto", arguments["mailto"]]
        if not any(a in args for a in ("--doi", "--title")) and not arguments.get("path"):
            return tool_result("Provide `path`, `doi` or `title`.", is_error=True)
        result = _run(_script("verify_citations.py"), args)
        payload = result["stdout"] or result["stderr"]
        if result["exit_code"] == 3:
            payload += "\n\n(exit 3: every lookup failed — offline or rate-limited; report that verification did not run)"
        return tool_result(payload, is_error=result["exit_code"] not in (0, 1, 3))

    if name == "search_literature":
        args = ["--format", arguments.get("format", "json"), "--quiet"]
        if arguments.get("query"):
            args += ["--query", arguments["query"]]
        if arguments.get("cited_by"):
            args += ["--cited-by", arguments["cited_by"]]
        if arguments.get("references_of"):
            args += ["--references-of", arguments["references_of"]]
        if arguments.get("from_year"):
            args += ["--from-year", str(arguments["from_year"])]
        if arguments.get("to_year"):
            args += ["--to-year", str(arguments["to_year"])]
        if arguments.get("limit"):
            args += ["--limit", str(arguments["limit"])]
        if arguments.get("sort"):
            args += ["--sort", arguments["sort"]]
        if arguments.get("abstracts"):
            args.append("--abstracts")
        if not any(k in arguments for k in ("query", "cited_by", "references_of")):
            return tool_result("Provide `query`, `cited_by` or `references_of`.", is_error=True)
        result = _run(_script("search_literature.py"), args)
        payload = result["stdout"] or result["stderr"]
        if result["exit_code"] == 3:
            payload += "\n\n(exit 3: nothing retrievable — report 'no records found', do not invent results)"
        return tool_result(payload, is_error=False)

    if name == "prisma_screen":
        if not arguments.get("input"):
            return tool_result("`input` is required.", is_error=True)
        args = ["--input", arguments["input"], "--format", "json", "--quiet"]
        for pattern in arguments.get("include", []) or []:
            args += ["--include", pattern]
        for pattern in arguments.get("exclude", []) or []:
            args += ["--exclude", pattern]
        if arguments.get("from_year"):
            args += ["--from-year", str(arguments["from_year"])]
        if arguments.get("to_year"):
            args += ["--to-year", str(arguments["to_year"])]
        if arguments.get("type"):
            args += ["--type", arguments["type"]]
        if arguments.get("decisions"):
            args += ["--decisions", arguments["decisions"]]
        if arguments.get("out_prefix"):
            args += ["--out-prefix", arguments["out_prefix"]]
        result = _run(_script("prisma_screen.py"), args)
        return tool_result(result["stdout"] or result["stderr"], is_error=not result["ok"] and result["exit_code"] != 3)

    if name == "analyze_methods":
        if not arguments.get("input"):
            return tool_result("`input` is required.", is_error=True)
        args = ["--input", arguments["input"], "--format", arguments.get("format", "md"), "--quiet"]
        result = _run(_script("analyze_methods.py"), args)
        return tool_result(result["stdout"] or result["stderr"], is_error=not result["ok"])

    if name == "generate_visuals":
        kind = arguments.get("kind", "workflow")
        args = [kind]
        if kind in {"workflow", "prisma", "abstract", "poster"}:
            if not arguments.get("topic"):
                return tool_result("`topic` is required for this kind.", is_error=True)
            args += ["--topic", arguments["topic"]]
        if kind == "abstract" and arguments.get("style"):
            args += ["--style", arguments["style"]]
        if kind == "figure":
            args += ["--kind", arguments.get("chart", "line")]
            args += ["--palette", arguments.get("palette", "colorblind")]
        result = _run(_script("generate_visuals.py"), args)
        return tool_result(result["stdout"] or result["stderr"], is_error=not result["ok"])

    if name == "researchx_status":
        status = {
            "skill_dir": str(SKILL_DIR),
            "skill_md": (SKILL_DIR / "SKILL.md").exists(),
            "scripts": {p.name: p.exists() for p in sorted(SCRIPTS.glob("*.py"))},
            "version": SERVER_VERSION,
            "cache_dir": str(REPO_ROOT / ".researchx-cache"),
            "cache_entries": len(list((REPO_ROOT / ".researchx-cache").glob("*.json")))
            if (REPO_ROOT / ".researchx-cache").exists()
            else 0,
            "python": sys.version.split()[0],
        }
        return tool_result(json.dumps(status, indent=2))

    return tool_result(f"Unknown tool: {name}", is_error=True)


def get_prompt(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    arguments = arguments or {}
    if name == "research_gap_mining":
        topic = arguments.get("topic", "[topic]")
        text = (
            f"Run ResearchX module M2 (gap mining) for: {topic}.\n"
            "1. Search OpenAlex/Crossref/arXiv (search_literature) with ≥5 distinct queries, in English and the "
            "user's language, plus one counter-evidence query.\n"
            "2. Classify the literature into solved / unsolved / controversial / unexplored.\n"
            "3. Propose 5 topics with testable question, novelty versus specific papers, data, methods, venue, "
            "feasibility and scoop risk.\n"
            "4. Verify every reference with verify_citations before writing it.\n"
            "5. Save as topics_<topic>_YYYYMMDD.md and report the audit counts."
        )
    elif name == "manuscript_review":
        text = (
            f"Run ResearchX module M7 (adversarial peer review) for: {arguments.get('manuscript', '[draft]')}.\n"
            "Use three personas: domain expert, methodologist/statistician, and a hostile reviewer looking for a "
            "fatal flaw. For each comment give severity, evidence, and the cheapest sufficient fix. Include at "
            "least one potentially fatal comment, then write the point-by-point response letter. Also run "
            "verify_citations on the reference list and report unresolved entries."
        )
    elif name == "systematic_review":
        text = (
            f"Run ResearchX module M9 (PRISMA 2020) for the question: {arguments.get('question', '[question]')}.\n"
            "Write the protocol (PICO, inclusion/exclusion, registries, date), run search_literature to produce "
            "hits.json, run prisma_screen to get counts/flow/ledger, then record human eligibility decisions, "
            "write the synthesis with risk of bias, and include the AI-use disclosure (PRISMA-trAIce)."
        )
    elif name == "citation_audit":
        text = (
            f"Run ResearchX module M11 for: {arguments.get('document', '[document]')}.\n"
            "Call verify_citations on the document, summarise the verdict counts, list CORRECTED references with "
            "the corrected metadata, list NOT_FOUND/PARTIAL ones for manual checking (never call them fake), "
            "flag RETRACTED ones, and save citation_audit_YYYYMMDD.md."
        )
    elif name == "grant_draft":
        text = (
            f"Run ResearchX module M10 for: {arguments.get('topic', '[topic]')}.\n"
            "Build the rationale from retrieved literature (not memory), state 2-3 falsifiable scientific "
            "questions, measurable objectives, work packages, a Mermaid technical route, innovation points "
            "contrasted with the closest work, feasibility, risk mitigation, outcomes, timeline and budget. "
            "Every claim cited and verified; never write 'international leading' without a citation."
        )
    else:
        raise ValueError(f"Unknown prompt: {name}")
    return {
        "description": next(p["description"] for p in PROMPTS if p["name"] == name),
        "messages": [{"role": "user", "content": {"type": "text", "text": text}}],
    }


# --------------------------------------------------------------------------- #
# JSON-RPC plumbing                                                           #
# --------------------------------------------------------------------------- #


def handle(request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Handle one JSON-RPC message; returns a response or None for notifications."""
    method = request.get("method")
    request_id = request.get("id")
    params = request.get("params") or {}

    def ok(result: Any) -> Dict[str, Any]:
        return {"jsonrpc": "2.0", "id": request_id, "result": result}

    def err(code: int, message: str) -> Dict[str, Any]:
        return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}

    if method in {"notifications/initialized", "notifications/cancelled"}:
        return None
    if method == "initialize":
        return ok(
            {
                "protocolVersion": params.get("protocolVersion", PROTOCOL_VERSION),
                "capabilities": {"tools": {"listChanged": False}, "prompts": {"listChanged": False}},
                "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
                "instructions": (
                    "ResearchX is a literature-grounded research assistant. Rules: (1) never emit a reference "
                    "that verify_citations has not confirmed or that is not labelled [UNVERIFIED]; (2) never "
                    "invent numbers; (3) when a lookup fails, say so. Read skills/researchx/SKILL.md for the full "
                    "protocol and references/*.md for module detail."
                ),
            }
        )
    if method == "ping":
        return ok({})
    if method == "tools/list":
        return ok({"tools": TOOLS})
    if method == "tools/call":
        name = params.get("name")
        if not name:
            return err(-32602, "missing tool name")
        try:
            return ok(call_tool(name, params.get("arguments") or {}))
        except Exception as exc:  # keep the server alive
            return ok(tool_result(f"tool error: {exc}", is_error=True))
    if method == "prompts/list":
        return ok({"prompts": PROMPTS})
    if method == "prompts/get":
        try:
            return ok(get_prompt(params.get("name", ""), params.get("arguments") or {}))
        except ValueError as exc:
            return err(-32602, str(exc))
    if method == "resources/list":
        return ok({"resources": []})
    return err(-32601, f"method not found: {method}")


def serve(stdin=None, stdout=None) -> int:
    stdin = stdin or sys.stdin
    stdout = stdout or sys.stdout
    for line in stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
        except json.JSONDecodeError:
            stdout.write(json.dumps({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "parse error"}}) + "\n")
            stdout.flush()
            continue
        response = handle(request)
        if response is not None:
            stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
            stdout.flush()
    return 0


def selftest() -> int:
    """Offline protocol self-check used by CI and by `--selftest`."""
    checks = []
    init = handle({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    checks.append(("initialize", init["result"]["serverInfo"]["name"] == SERVER_NAME))
    tools = handle({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})["result"]["tools"]
    names = {tool["name"] for tool in tools}
    checks.append(("tools/list", {"verify_citations", "search_literature", "prisma_screen"} <= names))
    prompts = handle({"jsonrpc": "2.0", "id": 3, "method": "prompts/list"})["result"]["prompts"]
    checks.append(("prompts/list", len(prompts) >= 4))
    status = handle({"jsonrpc": "2.0", "id": 4, "method": "tools/call",
                     "params": {"name": "researchx_status", "arguments": {}}})["result"]
    checks.append(("tools/call status", not status["isError"]))
    unknown = handle({"jsonrpc": "2.0", "id": 5, "method": "nope"})
    checks.append(("unknown method", "error" in unknown))
    for label, passed in checks:
        print(f"{'PASS' if passed else 'FAIL'}  {label}")
    return 0 if all(passed for _, passed in checks) else 1


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="researchx_mcp_server.py",
        description="ResearchX MCP server (stdio, zero dependencies)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Point your MCP client at this file; see the module docstring for a config snippet.",
    )
    parser.add_argument("--list", action="store_true", help="print the exposed tools/prompts and exit")
    parser.add_argument("--selftest", action="store_true", help="run the offline protocol self-check and exit")
    parser.add_argument("--version", action="version", version=f"ResearchX MCP {SERVER_VERSION}")
    args = parser.parse_args(argv)

    if args.list:
        print(f"# {SERVER_NAME} {SERVER_VERSION}")
        for tool in TOOLS:
            print(f"{tool['name']}: {tool['description'].splitlines()[0]}")
        print("\n# prompts")
        for prompt in PROMPTS:
            print(f"{prompt['name']}: {prompt['description']}")
        return 0
    if args.selftest:
        return selftest()
    os.environ.setdefault("PYTHONUNBUFFERED", "1")
    return serve()


if __name__ == "__main__":
    raise SystemExit(main())
