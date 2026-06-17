"""Tests for router agent."""

import pytest

from app.agents.router_agent import TaskRouterAgent
from app.models.schemas import GenerationRequest, WorkflowState

ECOMMERCE_INPUT = "为商品设计一张618促销主图，突出限时优惠和电商banner广告"
ACADEMIC_INPUT = "绘制论文方法流程图，展示模型pipeline和实验framework架构"
PPT_INPUT = "制作课程汇报PPT封面，presentation slide演示"


@pytest.fixture
def router():
    return TaskRouterAgent()


def _state(text: str, task_type: str = "auto") -> WorkflowState:
    return WorkflowState(
        task_id="test01",
        request=GenerationRequest(user_input=text, task_type=task_type),
    )


def test_route_ecommerce(router):
    result = router.route(_state(ECOMMERCE_INPUT))
    assert result.task_type == "ecommerce_banner"
    assert result.route_reason
    assert result.traces[0].agent_name == "TaskRouterAgent"


def test_route_academic(router):
    result = router.route(_state(ACADEMIC_INPUT))
    assert result.task_type == "academic_figure"


def test_route_ppt(router):
    result = router.route(_state(PPT_INPUT))
    assert result.task_type == "ppt_visual"


def test_manual_override(router):
    result = router.route(_state("任意描述", task_type="academic_figure"))
    assert result.task_type == "academic_figure"
    assert "手动指定" in result.route_reason
