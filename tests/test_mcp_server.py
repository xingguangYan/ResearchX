"""The MCP server must speak valid JSON-RPC over stdio and stay dependency-free."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

SERVER = Path(__file__).resolve().parents[1] / "mcp-server" / "researchx_mcp_server.py"

sys.path.insert(0, str(SERVER.parent))
import researchx_mcp_server as mcp  # noqa: E402


def test_initialize_announces_server():
    response = mcp.handle({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    assert response["result"]["serverInfo"]["name"] == "researchx"
    assert "tools" in response["result"]["capabilities"]
    assert "verify_citations" in response["result"]["instructions"]


def test_tools_list_contains_integrity_tools():
    tools = mcp.handle({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})["result"]["tools"]
    names = {tool["name"] for tool in tools}
    assert {"verify_citations", "search_literature", "prisma_screen", "researchx_status"} <= names
    for tool in tools:
        assert tool["description"] and tool["inputSchema"]["type"] == "object"


def test_verify_citations_tool_reports_offline_instead_of_inventing():
    result = mcp.call_tool(
        "verify_citations",
        {"title": "A paper that certainly does not exist", "offline": True, "format": "json"},
    )
    text = result["content"][0]["text"]
    payload = json.loads(text.split("\n\n")[0])
    assert payload["summary"]["error"] == 1
    assert payload["results"][0]["verdict"] == "ERROR"
    assert "verification did not run" in text


def test_unknown_method_returns_jsonrpc_error():
    response = mcp.handle({"jsonrpc": "2.0", "id": 3, "method": "does/not/exist"})
    assert response["error"]["code"] == -32601


def test_prompts_include_research_workflows():
    prompts = mcp.handle({"jsonrpc": "2.0", "id": 4, "method": "prompts/list"})["result"]["prompts"]
    names = {prompt["name"] for prompt in prompts}
    assert {"research_gap_mining", "citation_audit", "systematic_review"} <= names
    filled = mcp.get_prompt("citation_audit", {"document": "draft.md"})
    assert "draft.md" in filled["messages"][0]["content"]["text"]


def test_stdio_round_trip():
    messages = (
        json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}) + "\n"
        + json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list"}) + "\n"
    )
    proc = subprocess.run(
        [sys.executable, str(SERVER)], input=messages, capture_output=True, text=True, timeout=120
    )
    lines = [json.loads(line) for line in proc.stdout.splitlines() if line.strip()]
    assert [line["id"] for line in lines] == [1, 2]
    assert any(tool["name"] == "prisma_screen" for tool in lines[1]["result"]["tools"])


def test_selftest_passes():
    proc = subprocess.run([sys.executable, str(SERVER), "--selftest"], capture_output=True, text=True, timeout=120)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "FAIL" not in proc.stdout
