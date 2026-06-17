"""Quality evaluation helpers used by CriticAgent."""

from __future__ import annotations

import re
from pathlib import Path

from app.models.schemas import EvaluationReport, VisualSpec

RISK_WORDS = [
    "最好", "第一", "绝对", "100%", "best ever", "guaranteed", "永远",
    "国家级", "顶级", "唯一", "#1",
]


class Evaluator:
    """Rule-based evaluator producing integer scores 0-100."""

    def evaluate(
        self,
        visual_spec: VisualSpec,
        prompt: str,
        output_path: Path | None,
        trace_count: int,
    ) -> EvaluationReport:
        """Score generation quality across five dimensions."""
        comments: list[str] = []
        suggestions: list[str] = []

        # Requirement match
        req_score = 60
        if visual_spec.main_subject and visual_spec.main_subject.lower() in prompt.lower():
            req_score += 20
        if visual_spec.purpose and len(visual_spec.purpose) > 5:
            req_score += 10
        req_score = min(100, req_score)
        if req_score < 80:
            suggestions.append("补充主体描述，使 prompt 与 main_subject 更一致。")

        # Domain compliance
        domain_score = 70
        if visual_spec.task_type == "ecommerce_banner":
            if any(k in prompt.lower() for k in ("product", "sale", "banner", "商品")):
                domain_score += 15
            if visual_spec.constraints:
                domain_score += 10
        elif visual_spec.task_type == "academic_figure":
            if "flowchart" in prompt.lower() or "mermaid" in prompt.lower() or "diagram" in prompt.lower():
                domain_score += 20
            if visual_spec.key_elements:
                domain_score += 10
        elif visual_spec.task_type == "ppt_visual":
            if any(k in prompt.lower() for k in ("presentation", "slide", "cover", "professional")):
                domain_score += 20
        domain_score = min(100, domain_score)

        # Visual quality (asset existence heuristic)
        if output_path and output_path.exists() and output_path.stat().st_size > 200:
            visual_score = 85
            comments.append(f"资产已生成: {output_path.name}")
        else:
            visual_score = 40
            suggestions.append("重新生成视觉资产，确保文件有效。")

        # Prompt completeness
        required_sections = ["subject", "scene", "style", "composition", "aspect ratio"]
        found = sum(1 for s in required_sections if s in prompt.lower())
        prompt_score = min(100, 50 + found * 10)
        if prompt_score < 80:
            suggestions.append("Prompt 应包含 subject, scene, style, composition, aspect ratio 等字段。")

        # Traceability
        trace_score = min(100, 40 + trace_count * 8)
        if trace_count < 5:
            suggestions.append("工作流 trace 步骤较少，检查 Agent 是否全部执行。")

        # Risk detection
        combined = prompt + " " + " ".join(visual_spec.text_requirements)
        risk_count = sum(1 for w in RISK_WORDS if w.lower() in combined.lower())
        if risk_count > 0:
            comments.append(f"检测到 {risk_count} 个风险词。")
            suggestions.append("移除绝对化宣传用语，降低合规风险。")

        scores = [req_score, domain_score, visual_score, prompt_score, trace_score]
        overall = int(sum(scores) / len(scores)) - risk_count * 2
        overall = max(0, min(100, overall))

        comments.extend([
            f"需求匹配: {req_score}/100",
            f"领域合规: {domain_score}/100",
            f"视觉质量: {visual_score}/100",
            f"Prompt 完整度: {prompt_score}/100",
            f"可追溯性: {trace_score}/100",
        ])

        return EvaluationReport(
            requirement_match_score=req_score,
            domain_compliance_score=domain_score,
            visual_quality_score=visual_score,
            prompt_completeness_score=prompt_score,
            traceability_score=trace_score,
            risk_count=risk_count,
            overall_score=overall,
            comments=comments,
            suggestions=suggestions,
        )
