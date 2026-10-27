"""
mcp_server.py - MCP (Model Context Protocol) JSON-RPC 2.0 Tool Server for CodeShift

Fulfills Requirement 2 (Tool Integration using MCP):
Exposes external and custom tools over standardized MCP JSON-RPC 2.0 protocol:
1. verify_python_code: Syntax verification & compilation tool.
2. ast_file_parser: Custom AST parser for Java and Python files.
3. dependency_database_lookup: Database lookup mapping Maven dependencies to PyPI packages.
4. code_metric_calculator: Calculator tool computing LOC, complexity, and token counts.
"""

import sys
import json
import os
from typing import Dict, Any

# Add src to sys.path
web_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(web_dir)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from tools.mcp_tools import (
    verify_python_code,
    ast_file_parser,
    dependency_database_lookup,
    code_metric_calculator
)
from tools.mcp_client import mcp_client


def handle_mcp_request(request_json: Dict[str, Any]) -> Dict[str, Any]:
    """
    Processes an incoming MCP JSON-RPC 2.0 tool call request.

    Args:
        request_json (Dict[str, Any]): JSON-RPC request dictionary.

    Returns:
        Dict[str, Any]: Standardized JSON-RPC 2.0 response dictionary.
    """
    req_id = request_json.get("id", 1)
    method = request_json.get("method", "")

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": mcp_client.list_tools()
            }
        }
    elif method == "tools/call":
        params = request_json.get("params", {})
        tool_name = params.get("name", "")
        args = params.get("arguments", {})

        try:
            res = mcp_client.call_tool(tool_name, args)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(res, indent=2)
                        }
                    ]
                }
            }
        except KeyError as ke:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": str(ke)}
            }
        except Exception as exc:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32603, "message": f"Internal tool execution error: {str(exc)}"}
            }

    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": -32601, "message": f"Method '{method}' not found."}
    }


def main_mcp_stdio_server():
    """Runs MCP stdio tool server listening on stdin and responding on stdout."""
    print("CodeShift MCP Tool Server running on stdio (4 tools registered)...", file=sys.stderr)
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            resp = handle_mcp_request(req)
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
        except Exception as exc:
            err_resp = {"jsonrpc": "2.0", "id": None, "error": {"code": -32603, "message": str(exc)}}
            sys.stdout.write(json.dumps(err_resp) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main_mcp_stdio_server()
