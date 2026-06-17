"""Tests for visual spec agent."""

import pytest

from app.agents.requirement_agent import RequirementAgent
from app.agents.router_agent import TaskRouterAgent
from app.agents.visual_spec_agent import VisualSpecAgent
from app.models.schemas import GenerationRequest, WorkflowState


def _prepare_state(text: str, task_type: str = "auto") -> WorkflowState:
    state = WorkflowState(
        task_id="vs01",
        request=GenerationRequest(user_input=text, task_type=task_type),
    )
    state = TaskRouterAgent().route(state)
    state = RequirementAgent().parse(state)
    return state


def test_ecommerce_visual_spec_promotion_rules():
    state = _prepare_state("电商促销商品主图 banner 设计，突出卖点")
    vs = VisualSpecAgent().build(state).visual_spec
    assert vs is not None
    assert vs.task_type == "ecommerce_banner"
    combined = " ".join(vs.key_elements + vs.constraints + vs.avoid).lower()
    assert any(k in combined for k in ("促销", "商品", "cta", "卖点"))
    assert any("夸大" in a or "绝对" in a for a in vs.avoid)


def test_academic_visual_spec_svg_output():
    state = _prepare_state("论文方法流程图 pipeline architecture 实验")
    vs = VisualSpecAgent().build(state).visual_spec
    assert vs.output_format in ("svg", "mermaid")
    assert "学术" in vs.style or "简洁" in vs.style


def test_ppt_visual_spec_professional():
    state = _prepare_state("PPT汇报封面 presentation slide 专业")
    vs = VisualSpecAgent().build(state).visual_spec
    assert vs.task_type == "ppt_visual"
    combined = (vs.style + vs.scenario + vs.purpose).lower()
    assert "专业" in combined or "汇报" in combined or "presentation" in combined.lower()
