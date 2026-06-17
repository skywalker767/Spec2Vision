"""Pydantic schemas for VisionFlow API and internal state."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal, Optional

import re

from pydantic import BaseModel, ConfigDict, Field, model_validator

TaskTypeStr = Literal["ecommerce_banner", "academic_figure", "ppt_visual"]
VALID_TASK_TYPES = ("ecommerce_banner", "academic_figure", "ppt_visual")


def _prompt_from_document_context(document_context: str) -> str:
    """Build a minimal user_input when only document_context was provided."""
    title_m = re.search(r"【文档标题】(.+)", document_context)
    flow_m = re.search(r"【方法流程】(.+)", document_context)
    title = (title_m.group(1).strip() if title_m else "") or "上传文档"
    chain = (flow_m.group(1).strip() if flow_m else "") or "核心方法流程"
    return f"为论文《{title}》生成一张图形摘要，展示：{chain}。"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class GenerationRequest(BaseModel):
    """User request for visual content generation."""

    user_input: str = Field(default="", description="User task description")
    task_type: Optional[str] = Field(
        "auto",
        description="ecommerce_banner | academic_figure | ppt_visual | auto",
    )
    style_preference: Optional[str] = None
    target_audience: Optional[str] = None
    aspect_ratio: Optional[str] = None
    enable_revision: bool = True
    clarification_answers: list["ClarificationAnswer"] = Field(default_factory=list)
    skip_clarification: bool = False
    document_context: Optional[str] = Field(
        None,
        description="Optional distilled context from an uploaded document (e.g. a paper).",
    )

    @model_validator(mode="after")
    def ensure_user_input(self) -> "GenerationRequest":
        if self.user_input and self.user_input.strip():
            return self
        if self.document_context and self.document_context.strip():
            self.user_input = _prompt_from_document_context(self.document_context)
            return self
        raise ValueError("user_input 不能为空（可上传 PDF 自动填充，或手动输入 Prompt）")


class ClarificationOption(BaseModel):
    label: str
    value: str
    description: str | None = None
    incompatible_with: list[str] = Field(
        default_factory=list,
        description="Option values that cannot be selected together with this option",
    )


class ClarificationQuestion(BaseModel):
    question_id: str
    question_text: str
    question_type: str = "single_choice"  # single_choice | multi_choice
    required: bool = True
    options: list[ClarificationOption]
    default_value: str | None = None
    reason: str


class DocumentSummary(BaseModel):
    """Structured overview distilled from an uploaded document."""

    title: str = ""
    problem: str = ""
    method_steps: list[str] = Field(default_factory=list)
    contributions: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    architecture_highlights: list[str] = Field(default_factory=list)
    performance_metrics: list[str] = Field(default_factory=list)
    suggested_input: str = ""
    char_count: int = 0


class DocumentExtractResponse(BaseModel):
    """Response for an uploaded document: summary + a context string for generation."""

    filename: str
    summary: DocumentSummary
    document_context: str
    suggested_task_type: str = "academic_figure"
    suggested_aspect_ratio: str = "16:9"


class ClarificationRequest(BaseModel):
    user_input: str = Field(default="")
    task_type: str | None = "auto"
    document_context: Optional[str] = None

    @model_validator(mode="after")
    def ensure_user_input(self) -> "ClarificationRequest":
        if self.user_input and self.user_input.strip():
            return self
        if self.document_context and self.document_context.strip():
            self.user_input = _prompt_from_document_context(self.document_context)
            return self
        raise ValueError("user_input 不能为空（可上传 PDF 自动填充，或手动输入 Prompt）")


class ClarificationResponse(BaseModel):
    task_type: str
    route_reason: str
    questions: list[ClarificationQuestion]
    sources: dict[str, str] = Field(default_factory=dict)


class ClarificationAnswer(BaseModel):
    question_id: str
    selected_value: str = ""
    selected_values: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def normalize_selection(self) -> "ClarificationAnswer":
        if self.selected_values:
            if not self.selected_value:
                self.selected_value = self.selected_values[0]
        elif self.selected_value:
            if ";" in self.selected_value:
                self.selected_values = [v for v in self.selected_value.split(";") if v]
            else:
                self.selected_values = [self.selected_value]
        return self


class VisualSpec(BaseModel):
    """Structured visual specification produced by VisualSpecAgent."""

    task_type: str
    title: str
    scenario: str
    target_audience: str
    purpose: str
    style: str
    aspect_ratio: str
    main_subject: str
    key_elements: list[str]
    text_requirements: list[str]
    constraints: list[str]
    avoid: list[str]
    output_format: str
    evaluation_dimensions: list[str]


class AgentTrace(BaseModel):
    """Single step trace entry from an agent."""

    step: str
    agent_name: str
    input_summary: str
    output_summary: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    timestamp: str = Field(default_factory=utc_now_iso)
    duration_ms: int = Field(0, ge=0, description="Step execution time in milliseconds")


class EvaluationReport(BaseModel):
    """Quality evaluation report from CriticAgent."""

    requirement_match_score: int = Field(..., ge=0, le=100)
    domain_compliance_score: int = Field(..., ge=0, le=100)
    visual_quality_score: int = Field(..., ge=0, le=100)
    prompt_completeness_score: int = Field(..., ge=0, le=100)
    traceability_score: int = Field(..., ge=0, le=100)
    risk_count: int = Field(0, ge=0)
    overall_score: int = Field(..., ge=0, le=100)
    comments: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)


class GenerationResult(BaseModel):
    """Complete output of a generation workflow."""

    task_id: str
    task_type: str
    route_reason: str
    visual_spec: VisualSpec
    prompt: str
    output_path: str
    report_path: str
    evaluation: EvaluationReport
    traces: list[AgentTrace]
    clarification_answers: list[ClarificationAnswer] = Field(default_factory=list)
    status: str = "completed"
    duration_ms: int = 0
    created_at: str = Field(default_factory=utc_now_iso)


class TaskSummary(BaseModel):
    """Brief summary for task listing."""

    task_id: str
    task_type: str
    title: str
    overall_score: int
    output_path: str
    status: str = "completed"
    duration_ms: int = 0
    created_at: str


class TaskListResponse(BaseModel):
    tasks: list[TaskSummary]
    total: int


class StatsResponse(BaseModel):
    """Aggregate statistics across all generated tasks."""

    total_tasks: int = 0
    avg_overall_score: float = 0.0
    avg_duration_ms: int = 0
    total_risk_count: int = 0
    by_task_type: dict[str, int] = Field(default_factory=dict)
    avg_score_by_type: dict[str, float] = Field(default_factory=dict)
    score_buckets: dict[str, int] = Field(default_factory=dict)
    llm_provider: str = "unknown"
    image_provider: str = "unknown"


class DeleteResponse(BaseModel):
    task_id: str
    deleted: bool


class HealthResponse(BaseModel):
    status: str = "ok"
    llm_provider: str = "unknown"
    image_provider: str = "unknown"


class WorkflowState(BaseModel):
    """Internal LangGraph workflow state."""

    request: GenerationRequest
    task_id: str
    task_type: str = "ppt_visual"
    route_reason: str = ""

    requirement: dict[str, Any] = Field(default_factory=dict)
    domain_enrichment: dict[str, Any] = Field(default_factory=dict)
    clarification_questions: list[ClarificationQuestion] = Field(default_factory=list)
    clarification_resolved: dict[str, str] = Field(default_factory=dict)
    visual_spec: Optional[VisualSpec] = None
    prompt: str = ""
    output_path: str = ""
    evaluation: Optional[EvaluationReport] = None
    traces: list[AgentTrace] = Field(default_factory=list)
    report_path: str = ""

    revision_done: bool = False
    error_message: Optional[str] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)
