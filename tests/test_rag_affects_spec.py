"""RAG influence on requirement / visual spec pipeline."""

from __future__ import annotations

from app.agents.requirement_agent import RequirementAgent
from app.models.schemas import GenerationRequest, WorkflowState


def test_rag_constraints_flow_into_requirement(monkeypatch):
    monkeypatch.setenv("RAG_ENABLED", "true")
    from app.config import get_settings
    from app.rag.retriever import reset_retriever_cache

    get_settings.cache_clear()
    reset_retriever_cache()
    state = WorkflowState(
        request=GenerationRequest(
            user_input="小红书冰咖啡促销主图，突出卖点",
            task_type="ecommerce_banner",
            skip_clarification=True,
        ),
        task_id="rag01",
        task_type="ecommerce_banner",
    )
    agent = RequirementAgent()
    state = agent.parse(state)
    constraints = state.requirement.get("constraints", [])
    assert len(constraints) >= 2
    assert state.requirement.get("rag_hits") is not None or rag_traces
    rag_traces = [t for t in state.traces if t.agent_name == "RagAgent"]
    assert rag_traces
