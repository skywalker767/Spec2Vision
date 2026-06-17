"""Tests for enhanced evaluator."""

from pathlib import Path

import pytest

from app.models.schemas import AcademicDiagramFields, VisualSpec
from app.tools.evaluator import Evaluator


@pytest.fixture
def evaluator():
    return Evaluator()


def _base_spec(**kwargs) -> VisualSpec:
    defaults = dict(
        task_type="ecommerce_banner",
        title="Test Banner",
        scenario="电商推广",
        target_audience="消费者",
        purpose="促进购买转化",
        style="促销感",
        aspect_ratio="1:1",
        main_subject="促销商品",
        key_elements=["product", "headline", "CTA"],
        text_requirements=["商品名"],
        constraints=["禁用夸大宣传"],
        avoid=["绝对化用语"],
        output_format="png",
        evaluation_dimensions=["卖点突出"],
    )
    defaults.update(kwargs)
    return VisualSpec(**defaults)


def _good_prompt() -> str:
    return (
        "Subject: 促销商品. Scene: 电商. Style: 促销感. "
        "Composition: product headline CTA. Aspect ratio: 1:1."
    )


def test_good_output_scores_high(evaluator, tmp_path):
    asset = tmp_path / "good.png"
    asset.write_bytes(b"\x89PNG\r\n\x1a\n" + b"x" * 500)
    result = evaluator.evaluate(_base_spec(), _good_prompt(), asset, trace_count=10)
    assert result.overall_score >= 60
    assert result.metric_scores.get("spec_completeness", 0) >= 50
    assert result.metric_scores.get("output_validity", 0) >= 50


def test_mediocre_output(evaluator, tmp_path):
    asset = tmp_path / "small.png"
    asset.write_bytes(b"tiny")
    result = evaluator.evaluate(
        _base_spec(main_subject="无关主体"),
        "short prompt",
        asset,
        trace_count=2,
    )
    assert result.overall_score < 80
    assert result.suggestions


def test_bad_missing_output(evaluator):
    result = evaluator.evaluate(_base_spec(), _good_prompt(), None, trace_count=1)
    assert result.metric_scores["output_validity"] <= 40
    assert any("输出文件不存在" in w for w in result.warnings)
    assert result.overall_score <= 70


def test_regression_missing_spec_fields(evaluator, tmp_path):
    """Evaluator should flag incomplete spec."""
    incomplete = _base_spec(title="", key_elements=[], purpose="")
    asset = tmp_path / "ok.png"
    asset.write_bytes(b"x" * 300)
    result = evaluator.evaluate(incomplete, _good_prompt(), asset, trace_count=5)
    assert result.metric_scores["spec_completeness"] < 80


def test_svg_academic_evaluation(evaluator, tmp_path):
    svg = tmp_path / "diagram.svg"
    svg.write_text(
        '<?xml version="1.0"?><svg xmlns="http://www.w3.org/2000/svg">'
        '<rect x="10" y="10" width="50" height="30"/>'
        '<text x="20" y="30">Input</text></svg>',
        encoding="utf-8",
    )
    spec = _base_spec(
        task_type="academic_figure",
        output_format="svg",
        academic=AcademicDiagramFields(
            entities=["Input", "Output"],
            relationships=["Input → Output"],
            labels=["Input", "Output"],
            caption="Pipeline",
        ),
    )
    result = evaluator.evaluate(spec, "diagram flowchart pipeline", svg, trace_count=8)
    assert result.metric_scores["output_validity"] >= 70


def test_risk_words_generate_warnings(evaluator, tmp_path):
    asset = tmp_path / "r.png"
    asset.write_bytes(b"x" * 400)
    risky = _good_prompt() + " 最好 第一 绝对 guaranteed"
    result = evaluator.evaluate(_base_spec(), risky, asset, trace_count=8)
    assert result.risk_count > 0
    assert result.warnings
