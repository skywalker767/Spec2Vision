"""Multi-metric quality evaluator used by CriticAgent (deterministic/offline)."""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path

from app.models.schemas import EvaluationReport, VisualSpec

RISK_WORDS = [
    "最好", "第一", "绝对", "100%", "best ever", "guaranteed", "永远",
    "国家级", "顶级", "唯一", "#1",
]

_PROMPT_SECTION_MARKERS = [
    ("subject", r"subject|主体|main subject"),
    ("scene", r"scene|场景|scenario"),
    ("style", r"style|风格|style:"),
    ("composition", r"composition|构图|layout"),
    ("aspect", r"aspect ratio|宽高比|aspect_ratio"),
]

_DOMAIN_KEYWORDS = {
    "ecommerce_banner": ["product", "sale", "banner", "商品", "促销", "cta", "购买"],
    "academic_figure": ["flowchart", "diagram", "pipeline", "模块", "箭头", "流程"],
    "ppt_visual": ["presentation", "slide", "cover", "汇报", "标题", "infographic", "教学"],
}


class Evaluator:
    """Deterministic multi-metric evaluator producing integer scores 0-100."""

    def evaluate(
        self,
        visual_spec: VisualSpec,
        prompt: str,
        output_path: Path | None,
        trace_count: int,
        traces: list | None = None,
    ) -> EvaluationReport:
        """Score generation quality across core and extended metrics."""
        comments: list[str] = []
        suggestions: list[str] = []
        warnings: list[str] = []
        metric_scores: dict[str, int] = {}

        # --- Spec completeness ---
        spec_score = self._spec_completeness_score(visual_spec)
        metric_scores["spec_completeness"] = spec_score
        if spec_score < 70:
            suggestions.append("补充 VisualSpec 必填字段（title、key_elements、purpose 等）。")

        # --- Prompt-spec alignment ---
        align_score = self._prompt_alignment_score(visual_spec, prompt)
        metric_scores["prompt_spec_alignment"] = align_score
        if align_score < 70:
            suggestions.append("使 prompt 与 main_subject、key_elements 更一致。")

        # --- Domain compliance ---
        domain_score = self._domain_compliance_score(visual_spec, prompt)
        metric_scores["task_domain_compliance"] = domain_score

        # --- Output validity ---
        output_score, output_warnings = self._output_validity_score(visual_spec, output_path)
        metric_scores["output_validity"] = output_score
        warnings.extend(output_warnings)
        if output_score < 60:
            suggestions.append("重新生成视觉资产，确保文件存在且格式有效。")

        # --- Trace completeness ---
        trace_score = self._trace_completeness_score(trace_count, traces)
        metric_scores["trace_completeness"] = trace_score
        if trace_score < 60:
            suggestions.append("工作流 trace 步骤不足，检查 Agent 是否全部执行。")

        # --- Accessibility (text-heavy visuals) ---
        a11y_score, a11y_warnings = self._accessibility_score(visual_spec, output_path)
        metric_scores["accessibility"] = a11y_score
        warnings.extend(a11y_warnings)

        # Map to legacy five dimensions for API compatibility
        req_score = align_score
        prompt_score = self._prompt_structure_score(prompt)
        visual_score = output_score

        # Risk detection
        combined = prompt + " " + " ".join(visual_spec.text_requirements)
        risk_count = sum(1 for w in RISK_WORDS if w.lower() in combined.lower())
        metric_scores["risk_penalty"] = max(0, 100 - risk_count * 15)
        if risk_count > 0:
            warnings.append(f"检测到 {risk_count} 个风险宣传词。")
            suggestions.append("移除绝对化宣传用语，降低合规风险。")

        core_scores = [req_score, domain_score, visual_score, prompt_score, trace_score]
        overall = int(sum(core_scores) / len(core_scores)) - risk_count * 2
        overall = max(0, min(100, overall))
        metric_scores["overall_weighted"] = overall

        comments.extend([
            f"Spec 完整度: {spec_score}/100",
            f"Prompt 对齐: {align_score}/100",
            f"领域合规: {domain_score}/100",
            f"输出有效性: {output_score}/100",
            f"Trace 完整性: {trace_score}/100",
            f"可访问性: {a11y_score}/100",
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
            metric_scores=metric_scores,
            warnings=warnings,
        )

    def _spec_completeness_score(self, spec: VisualSpec) -> int:
        required = [
            spec.title, spec.scenario, spec.purpose, spec.style,
            spec.main_subject, spec.aspect_ratio, spec.output_format,
        ]
        filled = sum(1 for v in required if v and str(v).strip())
        list_fields = [spec.key_elements, spec.text_requirements, spec.constraints]
        filled += sum(1 for lst in list_fields if lst)
        base = int((filled / (len(required) + len(list_fields))) * 100)

        # Domain-specific bonus
        if spec.task_type == "ecommerce_banner" and spec.product_poster:
            pp = spec.product_poster
            domain_filled = sum(1 for v in [pp.product_name, pp.cta, pp.brand_tone] if v)
            base = min(100, base + domain_filled * 5)
        elif spec.task_type == "ppt_visual" and spec.educational:
            ed = spec.educational
            domain_filled = sum(1 for v in [ed.topic, ed.learning_goal] if v)
            base = min(100, base + domain_filled * 5)
        elif spec.task_type == "academic_figure" and spec.academic:
            ac = spec.academic
            domain_filled = sum(1 for v in [ac.entities, ac.relationships, ac.caption] if v)
            base = min(100, base + domain_filled * 5)
        return min(100, base)

    def _prompt_alignment_score(self, spec: VisualSpec, prompt: str) -> int:
        score = 50
        pl = prompt.lower()
        if spec.main_subject and spec.main_subject.lower() in pl:
            score += 25
        matched_elements = sum(
            1 for el in spec.key_elements[:6]
            if el and el.lower() in pl
        )
        score += min(25, matched_elements * 8)
        if spec.purpose and len(spec.purpose) > 5:
            score += 5
        return min(100, score)

    def _domain_compliance_score(self, spec: VisualSpec, prompt: str) -> int:
        score = 60
        pl = prompt.lower()
        keywords = _DOMAIN_KEYWORDS.get(spec.task_type, [])
        hits = sum(1 for k in keywords if k.lower() in pl)
        score += min(25, hits * 8)
        if spec.constraints:
            score += 10
        if spec.task_type == "academic_figure" and spec.key_elements:
            score += 5
        return min(100, score)

    def _output_validity_score(
        self, spec: VisualSpec, output_path: Path | None,
    ) -> tuple[int, list[str]]:
        warnings: list[str] = []
        if not output_path or not output_path.exists():
            warnings.append("输出文件不存在。")
            return 20, warnings

        size = output_path.stat().st_size
        if size < 50:
            warnings.append("输出文件过小，可能无效。")
            return 35, warnings

        suffix = output_path.suffix.lower()
        if suffix == ".svg":
            return self._evaluate_svg(output_path, spec)
        if suffix == ".png":
            return self._evaluate_png(output_path, warnings)

        warnings.append(f"未知输出格式: {suffix}")
        return 50, warnings

    def _evaluate_svg(self, path: Path, spec: VisualSpec) -> tuple[int, list[str]]:
        warnings: list[str] = []
        score = 70
        try:
            tree = ET.parse(path)
            root = tree.getroot()
            score += 10
            text_nodes = [el.text for el in root.iter() if el.text and el.text.strip()]
            if text_nodes:
                score += 10
            else:
                warnings.append("SVG 中未发现文本标签。")
            if spec.academic and spec.academic.caption:
                caption_found = any(spec.academic.caption[:20] in (t or "") for t in text_nodes)
                if not caption_found and spec.academic.caption:
                    warnings.append("未在 SVG 中找到预期 caption 文本（学术图）。")
            # Check for basic structure elements
            tag_names = {el.tag.split("}")[-1] for el in root.iter()}
            if "rect" in tag_names or "path" in tag_names or "line" in tag_names:
                score += 5
        except ET.ParseError:
            warnings.append("SVG XML 解析失败。")
            return 30, warnings
        return min(100, score), warnings

    def _evaluate_png(self, path: Path, warnings: list[str]) -> tuple[int, list[str]]:
        score = 75
        try:
            from PIL import Image
            with Image.open(path) as img:
                w, h = img.size
                if w < 8 or h < 8:
                    warnings.append("PNG 尺寸异常偏小。")
                    score -= 20
                else:
                    score += 10
                if img.format and img.format.upper() != "PNG":
                    warnings.append(f"文件扩展名为 .png 但格式为 {img.format}。")
        except Exception:
            warnings.append("无法解析 PNG 图像。")
            score = 55
        return min(100, score), warnings

    def _trace_completeness_score(self, trace_count: int, traces: list | None) -> int:
        score = min(100, 30 + trace_count * 7)
        if traces:
            agents = {t.agent_name for t in traces}
            expected = {"TaskRouterAgent", "VisualSpecAgent", "AssetManagerAgent", "CriticAgent"}
            coverage = len(agents & expected) / len(expected)
            score = min(100, int(score * 0.6 + coverage * 40))
        return score

    def _accessibility_score(self, spec: VisualSpec, output_path: Path | None) -> tuple[int, list[str]]:
        warnings: list[str] = []
        text_heavy = len(spec.text_requirements) >= 2 or any(
            kw in " ".join(spec.text_requirements).lower()
            for kw in ("标题", "标签", "文案", "label", "caption")
        )
        if not text_heavy:
            return 85, warnings

        score = 70
        if spec.constraints:
            contrast_hints = any(
                kw in " ".join(spec.constraints).lower()
                for kw in ("对比", "contrast", "可读", "readable")
            )
            if contrast_hints:
                score += 15
            else:
                warnings.append("文字密集型视觉未明确要求对比度/可读性约束。")
        if output_path and output_path.suffix.lower() == ".svg":
            try:
                tree = ET.parse(output_path)
                texts = [el.text for el in tree.getroot().iter() if el.text and el.text.strip()]
                if texts:
                    score += 10
                else:
                    warnings.append("文字密集型任务但 SVG 无可见文本。")
            except ET.ParseError:
                pass
        return min(100, score), warnings

    def _prompt_structure_score(self, prompt: str) -> int:
        pl = prompt.lower()
        found = 0
        for _name, pattern in _PROMPT_SECTION_MARKERS:
            if re.search(pattern, pl, flags=re.IGNORECASE):
                found += 1
        return min(100, 45 + found * 11)
