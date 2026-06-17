"""MCP tool handlers – reuse GenerationService and core agents."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.agents.requirement_agent import RequirementAgent
from app.agents.router_agent import TaskRouterAgent
from app.agents.visual_spec_agent import VisualSpecAgent
from app.config import get_settings
from app.core.errors import AppError, NotFoundError, ValidationError
from app.core.security import resolve_storage_path, validate_trace_id, validate_user_input
from app.mcp.schemas import (
    CreateVisualSpecInput,
    EvaluateVisualAssetInput,
    GenerateVisualAssetInput,
    McpToolResult,
    QueryGenerationTraceInput,
)
from app.models.database import Base
from app.models.schemas import GenerationRequest, VisualSpec, WorkflowState
from app.rag.retriever import get_retriever
from app.services.generation_service import GenerationService
from app.tools.evaluator import Evaluator
from app.tools.trace_logger import append_trace


def _ephemeral_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)()


def _ok(data: dict, *, trace_id: str | None = None) -> McpToolResult:
    return McpToolResult(success=True, data=data, trace_id=trace_id)


def _err(exc: Exception, *, trace_id: str | None = None) -> McpToolResult:
    if isinstance(exc, AppError):
        return McpToolResult(
            success=False,
            error=exc.to_dict(),
            trace_id=trace_id,
        )
    return McpToolResult(
        success=False,
        error={"code": "internal_error", "message": str(exc), "recoverable": False},
        trace_id=trace_id,
    )


def create_visual_spec(payload: dict[str, Any]) -> McpToolResult:
    try:
        req = CreateVisualSpecInput.model_validate(payload)
        user_input = validate_user_input(req.user_input)
        service = GenerationService()
        task_id = service.create_task_id()
        gen_req = GenerationRequest(
            user_input=user_input,
            task_type=req.task_type,
            style_preference=req.style_preference,
            target_audience=req.target_audience,
            aspect_ratio=req.aspect_ratio,
            skip_clarification=True,
        )
        state = WorkflowState(request=gen_req, task_id=task_id)
        router = TaskRouterAgent()
        requirement = RequirementAgent()
        visual = VisualSpecAgent()
        state = router.route(state)
        state = requirement.parse(state)
        rag = get_retriever().build_context(user_input, task_type=state.task_type)
        if rag.hits:
            state.requirement.setdefault("rag_constraints", rag.applied_constraints)
            append_trace(
                state.traces,
                agent_name="RagAgent",
                step="retrieve_guidelines",
                input_summary=user_input[:120],
                output_summary=f"hits={len(rag.hits)}",
                metadata={
                    "hits": [h.model_dump() for h in rag.hits],
                    "applied_constraints": rag.applied_constraints,
                    "pipeline_step": "rag_retrieval",
                },
                pipeline_step="rag_retrieval",
            )
        for c in req.constraints:
            state.requirement.setdefault("constraints", []).append(c)
        for c in rag.applied_constraints:
            state.requirement.setdefault("constraints", []).append(c)
        state = visual.build(state)
        if not state.visual_spec:
            raise ValidationError("Visual Spec 构建失败")
        return _ok(
            {
                "visual_spec": state.visual_spec.model_dump(),
                "task_type": state.task_type,
                "route_reason": state.route_reason,
                "rag_hits": [h.model_dump() for h in rag.hits],
            },
            trace_id=task_id,
        )
    except Exception as exc:  # noqa: BLE001
        return _err(exc)


def generate_visual_asset(payload: dict[str, Any]) -> McpToolResult:
    session = _ephemeral_session()
    try:
        req = GenerateVisualAssetInput.model_validate(payload)
        user_input = validate_user_input(req.user_input)
        gen_req = GenerationRequest(
            user_input=user_input,
            task_type=req.task_type,
            skip_clarification=req.skip_clarification,
            enable_revision=req.enable_revision,
        )
        service = GenerationService()
        result = service.run_generation(session, gen_req)
        return _ok(
            {
                "task_id": result.task_id,
                "output_path": result.output_path,
                "prompt": result.prompt,
                "task_type": result.task_type,
                "metadata": {
                    "duration_ms": result.duration_ms,
                    "overall_score": result.evaluation.overall_score,
                },
            },
            trace_id=result.task_id,
        )
    except Exception as exc:  # noqa: BLE001
        return _err(exc)
    finally:
        session.close()


def evaluate_visual_asset(payload: dict[str, Any]) -> McpToolResult:
    try:
        req = EvaluateVisualAssetInput.model_validate(payload)
        spec = VisualSpec.model_validate(req.visual_spec)
        settings = get_settings()
        path: Path | None = None
        trace_id = req.task_id
        if req.asset_path:
            path = resolve_storage_path(req.asset_path)
        elif req.task_id:
            trace_id = validate_trace_id(req.task_id)
            for root in (
                settings.generated_dir,
                settings.diagrams_dir,
            ):
                matches = list(root.glob(f"{trace_id}_*"))
                if matches:
                    path = matches[0]
                    break
            if path is None:
                raise NotFoundError(f"未找到 task_id={trace_id} 的资产文件")
        else:
            raise ValidationError("需提供 asset_path 或 task_id")

        evaluator = Evaluator()
        report = evaluator.evaluate(
            spec,
            prompt=spec.title or "",
            output_path=path,
            trace_count=0,
            traces=[],
        )
        passed = report.overall_score >= int(settings.min_quality_score * 100)
        return _ok(
            {
                "overall_score": report.overall_score,
                "offline_score": report.offline_score,
                "passed": passed,
                "issues": report.warnings + report.comments,
                "suggestions": report.suggestions,
                "evaluation": report.model_dump(),
            },
            trace_id=trace_id,
        )
    except Exception as exc:  # noqa: BLE001
        return _err(exc, trace_id=payload.get("task_id") if isinstance(payload, dict) else None)


def query_generation_trace(payload: dict[str, Any]) -> McpToolResult:
    try:
        req = QueryGenerationTraceInput.model_validate(payload)
        trace_id = validate_trace_id(req.trace_id)
        settings = get_settings()
        trace_path = settings.traces_dir / f"{trace_id}.json"
        if not trace_path.exists():
            raise NotFoundError(f"Trace {trace_id} 不存在")
        traces = json.loads(trace_path.read_text(encoding="utf-8"))
        return _ok({"trace_id": trace_id, "traces": traces}, trace_id=trace_id)
    except Exception as exc:  # noqa: BLE001
        return _err(exc, trace_id=payload.get("trace_id") if isinstance(payload, dict) else None)


TOOL_HANDLERS = {
    "create_visual_spec": create_visual_spec,
    "generate_visual_asset": generate_visual_asset,
    "evaluate_visual_asset": evaluate_visual_asset,
    "query_generation_trace": query_generation_trace,
}


def list_tool_definitions() -> list[dict[str, Any]]:
    from app.mcp.schemas import (
        CreateVisualSpecInput,
        EvaluateVisualAssetInput,
        GenerateVisualAssetInput,
        QueryGenerationTraceInput,
    )

    return [
        {
            "name": "create_visual_spec",
            "description": "Convert a fuzzy visual brief into structured Visual Spec JSON.",
            "inputSchema": CreateVisualSpecInput.model_json_schema(),
        },
        {
            "name": "generate_visual_asset",
            "description": "Run the full Spec2Vision generation pipeline and return asset metadata.",
            "inputSchema": GenerateVisualAssetInput.model_json_schema(),
        },
        {
            "name": "evaluate_visual_asset",
            "description": "Evaluate an asset against Visual Spec using the heuristic rubric.",
            "inputSchema": EvaluateVisualAssetInput.model_json_schema(),
        },
        {
            "name": "query_generation_trace",
            "description": "Fetch agent trace timeline for a generation task.",
            "inputSchema": QueryGenerationTraceInput.model_json_schema(),
        },
    ]
