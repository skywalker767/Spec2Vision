"""MCP tool schema and mock invocation tests."""

from __future__ import annotations

import json

from app.mcp.tools import (
    TOOL_HANDLERS,
    create_visual_spec,
    evaluate_visual_asset,
    list_tool_definitions,
    query_generation_trace,
)


def test_mcp_lists_four_tools():
    tools = list_tool_definitions()
    names = {t["name"] for t in tools}
    assert names == {
        "create_visual_spec",
        "generate_visual_asset",
        "evaluate_visual_asset",
        "query_generation_trace",
    }
    for tool in tools:
        assert "inputSchema" in tool
        assert tool["inputSchema"].get("properties")


def test_mcp_create_visual_spec_mock():
    result = create_visual_spec(
        {"user_input": "淘宝护肤品促销主图，突出卖点", "task_type": "ecommerce_banner"}
    )
    assert result.success is True
    assert result.trace_id
    spec = result.data["visual_spec"]
    assert spec["task_type"] == "ecommerce_banner"
    assert spec["title"]


def test_mcp_generate_visual_asset_mock():
    handler = TOOL_HANDLERS["generate_visual_asset"]
    result = handler(
        {
            "user_input": "简洁 PPT 封面，AI 课程",
            "task_type": "ppt_visual",
            "skip_clarification": True,
        }
    )
    assert result.success is True
    assert result.data["output_path"]
    assert result.trace_id == result.data["task_id"]


def test_mcp_query_missing_trace():
    result = query_generation_trace({"trace_id": "missing123"})
    assert result.success is False
    assert result.error["code"] == "not_found"


def test_mcp_evaluate_requires_path_or_task():
    result = evaluate_visual_asset({"visual_spec": {"task_type": "ppt_visual"}})
    assert result.success is False
