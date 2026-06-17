"""Tests for evaluator."""

from pathlib import Path

import pytest

from app.models.schemas import VisualSpec
from app.tools.evaluator import Evaluator


@pytest.fixture
def evaluator():
    return Evaluator()


@pytest.fixture
def sample_spec():
    return VisualSpec(
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


def _good_prompt() -> str:
    return (
        "Subject: 促销商品. Scene: 电商. Style: 促销感. "
        "Composition: product headline CTA. Aspect ratio: 1:1. "
        "Constraints: 合规. Avoid: blur."
    )


def test_scores_in_range(evaluator, sample_spec, tmp_path):
    asset = tmp_path / "test.png"
    asset.write_bytes(b"x" * 1000)
    result = evaluator.evaluate(sample_spec, _good_prompt(), asset, trace_count=8)
    for field in (
        "requirement_match_score",
        "domain_compliance_score",
        "visual_quality_score",
        "prompt_completeness_score",
        "traceability_score",
        "overall_score",
    ):
        val = getattr(result, field)
        assert 0 <= val <= 100, f"{field}={val} out of range"


def test_overall_score_calculation(evaluator, sample_spec, tmp_path):
    asset = tmp_path / "test.png"
    asset.write_bytes(b"x" * 1000)
    result = evaluator.evaluate(sample_spec, _good_prompt(), asset, trace_count=8)
    scores = [
        result.requirement_match_score,
        result.domain_compliance_score,
        result.visual_quality_score,
        result.prompt_completeness_score,
        result.traceability_score,
    ]
    expected = int(sum(scores) / len(scores)) - result.risk_count * 2
    expected = max(0, min(100, expected))
    assert result.overall_score == expected


def test_risk_count_lowers_overall_score(evaluator, sample_spec, tmp_path):
    asset = tmp_path / "test.png"
    asset.write_bytes(b"x" * 1000)
    clean = evaluator.evaluate(sample_spec, _good_prompt(), asset, trace_count=8)
    risky_prompt = _good_prompt() + " 最好第一 绝对 guaranteed best ever #1"
    risky = evaluator.evaluate(sample_spec, risky_prompt, asset, trace_count=8)
    assert risky.risk_count > clean.risk_count
    assert risky.overall_score <= clean.overall_score
