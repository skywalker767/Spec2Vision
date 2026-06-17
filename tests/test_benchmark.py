"""Tests for benchmark runner."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.config import PROJECT_ROOT, get_settings
from app.tools.benchmark import run_benchmark


@pytest.fixture(autouse=True)
def clear_cache():
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_run_benchmark_generates_report():
    report = run_benchmark(save=True)

    assert report["total_cases"] == 3
    assert len(report["results"]) == 3
    assert "summary" in report
    assert report["report_path"]

    report_path = Path(report["report_path"])
    assert report_path.exists()

    saved = json.loads(report_path.read_text(encoding="utf-8"))
    assert saved["total_cases"] == 3

    for row in report["results"]:
        assert "routing_correct" in row
        assert "visual_spec_completeness" in row
        assert "prompt_length" in row
        assert "overall_score" in row
        assert "output_exists" in row
        assert "trace_steps" in row
        assert "total_duration_ms" in row
        assert row["trace_steps"] >= 5
        assert row["output_exists"] is True
        assert row["routing_correct"] is True


def test_benchmark_report_default_path():
    report = run_benchmark(save=True)
    expected = PROJECT_ROOT / "storage" / "reports" / "benchmark_report.json"
    assert Path(report["report_path"]) == expected
