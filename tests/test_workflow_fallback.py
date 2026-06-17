"""Tests for workflow fallback behavior."""

from __future__ import annotations

import pytest

from app.config import get_settings
from app.graph import visionflow_graph as vg_module
from app.graph.visionflow_graph import VisionFlowGraph, run_pipeline
from app.models.schemas import GenerationRequest, WorkflowState


@pytest.fixture
def state():
    return WorkflowState(
        task_id="wf01",
        request=GenerationRequest(
            user_input="制作PPT汇报封面 presentation slide",
            skip_clarification=True,
            enable_revision=False,
        ),
    )


def test_pipeline_fallback_completes(state, monkeypatch):
    """run_pipeline should complete without LangGraph."""
    monkeypatch.setenv("IMAGE_PROVIDER", "mock")
    monkeypatch.setenv("LLM_PROVIDER", "mock")
    get_settings.cache_clear()
    vg_module._graph_instance = None

    result = run_pipeline(state)
    assert result.visual_spec is not None
    assert result.evaluation is not None
    assert result.output_path


def test_workflow_debug_raises(monkeypatch, state):
    monkeypatch.setenv("WORKFLOW_DEBUG", "true")
    monkeypatch.setenv("LLM_PROVIDER", "mock")
    monkeypatch.setenv("IMAGE_PROVIDER", "mock")
    get_settings.cache_clear()
    vg_module._graph_instance = None

    graph = VisionFlowGraph()

    def _boom(s):
        raise RuntimeError("simulated graph failure")

    graph._graph.invoke = _boom  # type: ignore[method-assign]
    with pytest.raises(Exception):
        graph.run(state)


def test_fallback_records_error_metadata(monkeypatch, state):
    monkeypatch.setenv("WORKFLOW_DEBUG", "false")
    monkeypatch.setenv("LLM_PROVIDER", "mock")
    monkeypatch.setenv("IMAGE_PROVIDER", "mock")
    get_settings.cache_clear()
    vg_module._graph_instance = None

    graph = VisionFlowGraph()

    def _boom(s):
        raise ValueError("simulated recoverable failure")

    graph._graph.invoke = _boom  # type: ignore[method-assign]
    result = graph.run(state)
    assert result.workflow_fallback == "pipeline"
    assert result.workflow_error_type == "ValueError"
    assert result.visual_spec is not None
