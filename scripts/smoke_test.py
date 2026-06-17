#!/usr/bin/env python3
"""End-to-end smoke test for clone-and-run verification."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ.setdefault("LLM_PROVIDER", "mock")
os.environ.setdefault("IMAGE_PROVIDER", "mock")
os.environ.setdefault("RAG_ENABLED", "true")

from app.config import get_settings
from app.mcp.tools import create_visual_spec, list_tool_definitions
from app.rag.retriever import get_retriever


def main() -> int:
    get_settings.cache_clear()
    tools = list_tool_definitions()
    assert len(tools) >= 4, "MCP tools missing"

    hits = get_retriever().search("电商主图 促销", task_type="ecommerce_banner", top_k=1)
    assert hits, "RAG index empty – run scripts/ingest_knowledge_base.py"

    result = create_visual_spec(
        {"user_input": "小红书冰咖啡促销主图", "task_type": "ecommerce_banner"}
    )
    assert result.success, result.error

    print("Smoke OK:", len(tools), "MCP tools,", len(hits), "RAG hits,", "visual_spec keys=", list(result.data.get("visual_spec", {}).keys())[:4])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
