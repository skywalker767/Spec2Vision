"""Router agent: classify user task into domain workflow."""

from __future__ import annotations

from app.models.schemas import WorkflowState
from app.tools.trace_logger import append_trace

ECOMMERCE_KEYWORDS = [
    "商品", "促销", "电商", "主图", "详情页", "618", "双11", "banner", "广告",
    "product", "sale", "shop", "ecommerce", "discount",
]
ACADEMIC_KEYWORDS = [
    "论文", "方法", "模型", "流程图", "实验", "framework", "pipeline",
    "architecture", "graphical abstract", "学术", "algorithm", "diagram",
]
PPT_KEYWORDS = [
    "ppt", "汇报", "报告", "封面", "演示", "presentation", "slide", "keynote",
]


class TaskRouterAgent:
    """Rule-based task router with optional LLM extension point."""

    def __init__(self, llm_client=None):
        self.llm_client = llm_client

    def route(self, state: WorkflowState) -> WorkflowState:
        """Determine task_type and route_reason from user input."""
        req = state.request
        text = req.user_input.lower()

        if req.task_type and req.task_type != "auto" and req.task_type in (
            "ecommerce_banner", "academic_figure", "ppt_visual",
        ):
            state.task_type = req.task_type
            state.route_reason = f"用户手动指定任务类型: {req.task_type}"
        else:
            ecom_score = sum(1 for kw in ECOMMERCE_KEYWORDS if kw.lower() in text)
            acad_score = sum(1 for kw in ACADEMIC_KEYWORDS if kw.lower() in text)
            ppt_score = sum(1 for kw in PPT_KEYWORDS if kw.lower() in text)

            scores = {
                "ecommerce_banner": ecom_score,
                "academic_figure": acad_score,
                "ppt_visual": ppt_score,
            }
            best = max(scores, key=scores.get)

            if scores[best] == 0:
                state.task_type = "ppt_visual"
                state.route_reason = "未匹配到明确关键词，默认路由到 ppt_visual"
            else:
                state.task_type = best
                state.route_reason = (
                    f"关键词匹配: ecommerce={ecom_score}, academic={acad_score}, "
                    f"ppt={ppt_score} → {best}"
                )

        append_trace(
            state.traces,
            agent_name="TaskRouterAgent",
            step="route_task",
            input_summary=req.user_input[:120],
            output_summary=f"type={state.task_type}, reason={state.route_reason[:80]}",
            metadata={"task_type": state.task_type, "route_reason": state.route_reason},
        )
        return state

    def route_with_llm(self, state: WorkflowState) -> WorkflowState:
        """Placeholder for LLM-based routing."""
        return self.route(state)


# Backward-compatible alias
RouterAgent = TaskRouterAgent
