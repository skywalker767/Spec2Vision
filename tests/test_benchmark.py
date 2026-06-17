"""Tests for benchmark runner."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.config import PROJECT_ROOT, get_settings
from app.tools.benchmark import BENCHMARK_FILES, run_benchmark


@pytest.fixture(autouse=True)
def clear_cache():
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_benchmark_manifest_has_fifteen_cases():
    assert len(BENCHMARK_FILES) == 15


def test_run_benchmark_subset_generates_report():
    report = run_benchmark(save=True, case_files=["ecommerce_case.json", "ppt_case.json"])

    assert report["total_cases"] == 2
    assert len(report["results"]) == 2
    assert "summary" in report
    assert report["report_path"]
    assert report.get("markdown_report_path")

    report_path = Path(report["report_path"])
    assert report_path.exists()

    md_path = Path(report["markdown_report_path"])
    assert md_path.exists()
    assert "# VisionFlow Benchmark Report" in md_path.read_text(encoding="utf-8")

    for row in report["results"]:
        assert "routing_correct" in row
        assert "required_fields_ok" in row
        assert "score_meets_threshold" in row
        assert "passed" in row
        assert row["output_exists"] is True


def test_benchmark_offline_mock_mode(monkeypatch, tmp_path):
    monkeypatch.setenv("DEMO_MODE", "true")
    monkeypatch.setenv("LLM_PROVIDER", "mock")
    monkeypatch.setenv("IMAGE_PROVIDER", "mock")
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'bench.db'}")
    get_settings.cache_clear()

    report = run_benchmark(
        save=False,
        case_files=["ecommerce_case.json", "academic_case.json", "ppt_case.json"],
    )
    assert report["mode"] == "mock"
    assert report["total_cases"] == 3
    assert all(r["output_exists"] for r in report["results"])


def test_benchmark_report_default_path():
    report = run_benchmark(save=True, case_files=["ecommerce_case.json"])
    expected = PROJECT_ROOT / "storage" / "reports" / "benchmark_report.json"
    assert Path(report["report_path"]) == expected
