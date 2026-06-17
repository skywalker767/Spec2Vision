"""Lightweight MCP-compatible stdio server (JSON-RPC 2.0)."""

from __future__ import annotations

import json
import sys
from typing import Any

from app.core.logging import setup_logging
from app.mcp.tools import TOOL_HANDLERS, list_tool_definitions

SERVER_INFO = {"name": "spec2vision-mcp", "version": "1.0.0"}
PROTOCOL_VERSION = "2024-11-05"


class McpServer:
    """Minimal MCP server without external SDK dependency."""

    def __init__(self) -> None:
        self._initialized = False

    def handle(self, message: dict[str, Any]) -> dict[str, Any] | None:
        if message.get("method") == "notifications/initialized":
            return None
        msg_id = message.get("id")
        method = message.get("method", "")
        params = message.get("params") or {}

        try:
            if method == "initialize":
                self._initialized = True
                return self._result(
                    msg_id,
                    {
                        "protocolVersion": PROTOCOL_VERSION,
                        "capabilities": {"tools": {}},
                        "serverInfo": SERVER_INFO,
                    },
                )
            if method == "tools/list":
                return self._result(msg_id, {"tools": list_tool_definitions()})
            if method == "tools/call":
                name = params.get("name")
                arguments = params.get("arguments") or {}
                handler = TOOL_HANDLERS.get(name)
                if not handler:
                    return self._error(msg_id, -32601, f"Unknown tool: {name}")
                result = handler(arguments)
                return self._result(
                    msg_id,
                    {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result.model_dump(), ensure_ascii=False, indent=2),
                            }
                        ],
                        "isError": not result.success,
                    },
                )
            if method == "ping":
                return self._result(msg_id, {})
            return self._error(msg_id, -32601, f"Method not found: {method}")
        except Exception as exc:  # noqa: BLE001
            return self._error(msg_id, -32603, str(exc))

    @staticmethod
    def _result(msg_id: Any, result: dict) -> dict:
        return {"jsonrpc": "2.0", "id": msg_id, "result": result}

    @staticmethod
    def _error(msg_id: Any, code: int, message: str) -> dict:
        return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": code, "message": message}}


def run_stdio_server() -> None:
    setup_logging()
    server = McpServer()
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            continue
        response = server.handle(message)
        if response is not None:
            sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    run_stdio_server()
