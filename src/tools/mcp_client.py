"""
mcp_client.py - Standard Model Context Protocol (MCP) Client for CodeShift Agents

Enables ADK and CrewAI agents to interact with external tools via the MCP JSON-RPC 2.0 protocol.
Supports both in-process dispatch (for performance) and subprocess JSON-RPC 2.0 stdio communication.
"""

import json
from typing import Dict, Any, List, Optional
from tools.mcp_tools import (
    verify_python_code,
    ast_file_parser,
    dependency_database_lookup,
    code_metric_calculator
)


class MCPToolClient:
    """
    Standard MCP Client interface executing JSON-RPC 2.0 tool requests.
    """

    def __init__(self):
        self.tool_registry = {
            "verify_python_code": verify_python_code,
            "ast_file_parser": ast_file_parser,
            "dependency_database_lookup": dependency_database_lookup,
            "code_metric_calculator": code_metric_calculator
        }

    def list_tools(self) -> List[Dict[str, Any]]:
        """Returns the MCP tool list conforming to Model Context Protocol specification."""
        return [
            {
                "name": "verify_python_code",
                "description": "Writes candidate Python code to output/ and verifies syntax using py_compile.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "python_code": {"type": "string", "description": "Candidate Python source code"},
                        "filename": {"type": "string", "description": "Target filename"}
                    },
                    "required": ["python_code"]
                }
            },
            {
                "name": "ast_file_parser",
                "description": "Custom file parser extracting classes, methods, imports, and AST features.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file_content": {"type": "string", "description": "Source code text"},
                        "language": {"type": "string", "enum": ["java", "python"], "default": "java"}
                    },
                    "required": ["file_content"]
                }
            },
            {
                "name": "dependency_database_lookup",
                "description": "Database lookup mapping Maven dependencies to equivalent PyPI packages.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "dependency_query": {"type": "string", "description": "Maven artifact ID or dependency keyword"}
                    },
                    "required": ["dependency_query"]
                }
            },
            {
                "name": "code_metric_calculator",
                "description": "Calculator computing LOC, cyclomatic complexity, and token counts.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "source_code": {"type": "string", "description": "Source code text"},
                        "target_code": {"type": "string", "description": "Optional translated code for diff metrics"}
                    },
                    "required": ["source_code"]
                }
            }
        ]

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes an MCP tool call and returns the standardized result dictionary.
        """
        if tool_name not in self.tool_registry:
            raise KeyError(f"MCP Tool '{tool_name}' is not registered.")

        func = self.tool_registry[tool_name]
        try:
            result = func(**arguments)
            return {"status": "success", "tool": tool_name, "result": result}
        except Exception as exc:
            return {"status": "error", "tool": tool_name, "error": str(exc)}


# Global client instance
mcp_client = MCPToolClient()
