"""MCP tool input/output schemas."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class CreateVisualSpecInput(BaseModel):
    user_input: str = Field(..., description="Raw visual requirement")
    task_type: str = Field("auto", description="auto | ecommerce_banner | academic_figure | ppt_visual")
    style_preference: str | None = None
    target_audience: str | None = None
    aspect_ratio: str | None = None
    constraints: list[str] = Field(default_factory=list)


class GenerateVisualAssetInput(BaseModel):
    user_input: str
    task_type: str = "auto"
    visual_spec: dict[str, Any] | None = None
    skip_clarification: bool = True
    enable_revision: bool = False


class EvaluateVisualAssetInput(BaseModel):
    task_id: str | None = None
    asset_path: str | None = None
    visual_spec: dict[str, Any]


class QueryGenerationTraceInput(BaseModel):
    trace_id: str = Field(..., description="Task / trace identifier")


class McpToolResult(BaseModel):
    success: bool
    data: dict[str, Any] = Field(default_factory=dict)
    error: dict[str, Any] | None = None
    trace_id: str | None = None
