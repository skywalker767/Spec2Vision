#!/usr/bin/env python3
"""Start Spec2Vision MCP server (stdio JSON-RPC)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Default mock for MCP demos without API keys (override via env)
os.environ.setdefault("LLM_PROVIDER", "mock")
os.environ.setdefault("IMAGE_PROVIDER", "mock")
os.environ.setdefault("RAG_ENABLED", "true")

from app.mcp.server import run_stdio_server  # noqa: E402

if __name__ == "__main__":
    run_stdio_server()
