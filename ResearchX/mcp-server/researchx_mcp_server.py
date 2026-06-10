"""
ResearchX MCP Server — AI Research Operating System

A Model Context Protocol (MCP) server that exposes ResearchX's research capabilities
as MCP tools. Compatible with Claude Desktop, Cline, Continue.dev, and other MCP clients.

Usage:
  # Install dependencies
  pip install mcp httpx

  # Run the server (stdio mode, for Claude Desktop)
  python mcp_server.py

  # Run with custom transport
  python mcp_server.py --transport sse --port 8080
"""

import json
import sys
import argparse
from typing import Any


# --------------- MCP Tool Definitions ---------------

TOOLS = [
    {
        "name": "analyze_paper",
        "description": "Analyze a research paper: extract logic chain, find innovation, identify gaps, compare with SOTA",
        "inputSchema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Paper title or DOI"},
                "topic": {"type": "string", "description": "Research domain (e.g., remote sensing, medicine)"}
            },
            "required": ["title"]
        }
    },
    {
        "name": "find_research_gaps",
        "description": "Search latest literature (2023-2026) to find research gaps and generate SCI topic proposals",
        "inputSchema": {
            "type": "object",
            "properties": {
                "topic": {"type": "string", "description": "Research domain or field"},
                "count": {"type": "integer", "description": "Number of topic proposals", "default": 5}
            },
            "required": ["topic"]
        }
    },
    {
        "name": "mine_methods",
        "description": "Search latest literature to discover methods and build method landscape table for a research topic",
        "inputSchema": {
            "type": "object",
            "properties": {
                "topic": {"type": "string", "description": "Research topic"},
                "years": {"type": "string", "description": "Year range (e.g., '2023-2026')", "default": "2023-2026"}
            },
            "required": ["topic"]
        }
    },
    {
        "name": "design_experiments",
        "description": "Design comprehensive experimental protocol: baselines, ablation, generalization, robustness tests",
        "inputSchema": {
            "type": "object",
            "properties": {
                "method": {"type": "string", "description": "Proposed method name"},
                "domain": {"type": "string", "description": "Research domain"}
            },
            "required": ["method", "domain"]
        }
    },
    {
        "name": "write_manuscript_section",
        "description": "Write a journal-adapted manuscript section with literature citations",
        "inputSchema": {
            "type": "object",
            "properties": {
                "section": {
                    "type": "string",
                    "enum": ["abstract", "introduction", "methods", "results", "discussion", "conclusion"],
                    "description": "Section to write"
                },
                "topic": {"type": "string", "description": "Research topic"},
                "journal_style": {
                    "type": "string",
                    "enum": ["nature", "science", "rse", "isprs", "ieee", "general"],
                    "description": "Target journal style",
                    "default": "general"
                }
            },
            "required": ["section", "topic"]
        }
    },
    {
        "name": "upgrade_to_q1",
        "description": "Assess paper quality and generate upgrade plan from current level to Q1 publication",
        "inputSchema": {
            "type": "object",
            "properties": {
                "paper_summary": {"type": "string", "description": "Paper abstract or summary"},
                "target_journal": {"type": "string", "description": "Target journal name (optional)"}
            },
            "required": ["paper_summary"]
        }
    },
    {
        "name": "simulate_peer_review",
        "description": "Simulate peer review from multiple reviewer perspectives with revision strategy",
        "inputSchema": {
            "type": "object",
            "properties": {
                "paper_summary": {"type": "string", "description": "Paper summary or abstract"},
                "reviewer_type": {
                    "type": "string",
                    "enum": ["top_journal", "domain_expert", "methodologist"],
                    "description": "Reviewer persona",
                    "default": "domain_expert"
                }
            },
            "required": ["paper_summary"]
        }
    },
    {
        "name": "generate_graphical_abstract",
        "description": "Generate AI image prompts for graphical abstract (GPT-4o, Midjourney, Flux)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "topic": {"type": "string", "description": "Research topic"},
                "style": {
                    "type": "string",
                    "enum": ["nature", "science", "cell", "general"],
                    "description": "Visual style",
                    "default": "general"
                }
            },
            "required": ["topic"]
        }
    },
    {
        "name": "write_grant_proposal",
        "description": "Generate a grant proposal with literature-backed claims",
        "inputSchema": {
            "type": "object",
            "properties": {
                "topic": {"type": "string", "description": "Research topic"},
                "agency": {"type": "string", "description": "Funding agency (e.g., NSFC, NSF, ERC)", "default": "NSFC"}
            },
            "required": ["topic"]
        }
    },
    {
        "name": "build_literature_review",
        "description": "Build a structured literature matrix and generate Related Work section",
        "inputSchema": {
            "type": "object",
            "properties": {
                "topic": {"type": "string", "description": "Research topic"},
                "paper_count": {"type": "integer", "description": "Number of papers to include", "default": 15}
            },
            "required": ["topic"]
        }
    }
]


def handle_list_tools() -> dict:
    """Handle the list_tools MCP request."""
    return {"tools": TOOLS}


def handle_call_tool(name: str, arguments: dict) -> dict:
    """Handle the call_tool MCP request.

    This is a proxy implementation. The actual research work is done by the
    AI model using web_search. This MCP server routes the request and provides
    the framework for the response.
    """
    # Validate the tool name
    tool_names = [t["name"] for t in TOOLS]
    if name not in tool_names:
        return {"content": [{"type": "text", "text": f"Unknown tool: {name}"}], "isError": True}

    # Return instructions for the AI to execute this research task
    instructions = {
        "type": "text",
        "text": (
            f"## ResearchX: {name}\n\n"
            f"Task parameters:\n{json.dumps(arguments, indent=2, ensure_ascii=False)}\n\n"
            f"Instructions:\n"
            f"1. Use web_search to find latest literature (2023-2026) on this topic\n"
            f"2. Analyze and synthesize the findings\n"
            f"3. Apply ResearchX methodology (literature-driven, not hardcoded)\n"
            f"4. Output structured analysis with citations\n\n"
            f"See ResearchX SKILL.md for full methodology."
        )
    }

    return {"content": [instructions]}


# --------------- Transport Implementations ---------------

def run_stdio():
    """Run MCP server in stdio mode (for Claude Desktop)."""
    import sys
    import json

    # Read messages from stdin
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            continue

        msg_id = message.get("id")
        method = message.get("method", "")
        params = message.get("params", {})

        if method == "tools/list":
            response = {"jsonrpc": "2.0", "id": msg_id, "result": TOOLS}
        elif method == "tools/call":
            result = handle_call_tool(params.get("name", ""), params.get("arguments", {}))
            response = {"jsonrpc": "2.0", "id": msg_id, "result": result}
        elif method == "initialize":
            response = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "researchx-mcp", "version": "1.0.0"}
                }
            }
        else:
            response = {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32601, "message": f"Method not found: {method}"}}

        sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
        sys.stdout.flush()


def run_sse(port: int):
    """Run MCP server in SSE mode (for web-based MCP clients)."""
    from http.server import HTTPServer, BaseHTTPRequestHandler

    class MCPHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/tools":
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(TOOLS, ensure_ascii=False).encode())
            elif self.path == "/health":
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'{"status":"ok"}')
            else:
                self.send_response(404)
                self.end_headers()

    server = HTTPServer(("0.0.0.0", port), MCPHandler)
    print(f"ResearchX MCP Server running on http://0.0.0.0:{port}", file=sys.stderr)
    server.serve_forever()


# --------------- CLI Entry Point ---------------

def main():
    parser = argparse.ArgumentParser(description="ResearchX MCP Server")
    parser.add_argument("--transport", choices=["stdio", "sse"], default="stdio",
                       help="Transport protocol")
    parser.add_argument("--port", type=int, default=8080, help="Port for SSE transport")
    args = parser.parse_args()

    if args.transport == "sse":
        run_sse(args.port)
    else:
        run_stdio()


if __name__ == "__main__":
    main()
