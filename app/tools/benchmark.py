"""Benchmark runner for VisionFlow example cases."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import PROJECT_ROOT, get_settings
from app.models.database import Base
from app.models.schemas import GenerationRequest, GenerationResult, VisualSpec
from app.services.generation_service import GenerationService

EXAMPLES_DIR = PROJECT_ROOT / "examples"
EXAMPLE_FILES = [
    "ecommerce_case.json",
    "academic_case.json",
    "ppt_case.json",
]

REQUIRED_VISUAL_SPEC_FIELDS = [
    "task_type", "title", "scenario", "target_audience", "purpose",
    "style", "aspect_ratio", "main_subject", "key_elements",
    "text_requirements", "constraints", "avoid", "output_format",
    "evaluation_dimensions",
]


def _visual_spec_completeness(spec: VisualSpec) -> float:
    """Return ratio of non-empty required VisualSpec fields (0.0–1.0)."""
    data = spec.model_dump()
    filled = 0
    for field in REQUIRED_VISUAL_SPEC_FIELDS:
        val = data.get(field)
        if val is None:
            continue
        if isinstance(val, list) and len(val) > 0:
            filled += 1
        elif isinstance(val, str) and val.strip():
            filled += 1
        elif not isinstance(val, (list, str)):
            filled += 1
    return round(filled / len(REQUIRED_VISUAL_SPEC_FIELDS), 3)


def _evaluate_case(case: dict, result: GenerationResult) -> dict:
    expected_type = case.get("expected_task_type", "")
    output_path = Path(result.output_path) if result.output_path else None
    return {
        "case_file": case.get("_file", ""),
        "task_id": result.task_id,
        "expected_task_type": expected_type,
        "actual_task_type": result.task_type,
        "routing_correct": result.task_type == expected_type,
        "visual_spec_completeness": _visual_spec_completeness(result.visual_spec),
        "prompt_length": len(result.prompt or ""),
        "overall_score": result.evaluation.overall_score,
        "output_exists": bool(output_path and output_path.exists()),
        "output_path": result.output_path,
        "trace_steps": len(result.traces),
        "total_duration_ms": sum(t.duration_ms for t in result.traces),
    }


def run_benchmark(save: bool = True) -> dict:
    """Run all example cases and produce a benchmark report.

    Returns the report dict and optionally saves to
    storage/reports/benchmark_report.json.
    """
    settings = get_settings()
    settings.ensure_dirs()

    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    db = sessionmaker(bind=engine)()

    service = GenerationService()
    results = []
    started_at = datetime.now(timezone.utc).isoformat()

    try:
        for filename in EXAMPLE_FILES:
            path = EXAMPLES_DIR / filename
            case = json.loads(path.read_text(encoding="utf-8"))
            case["_file"] = filename

            request = GenerationRequest(
                user_input=case["user_input"],
                task_type=case.get("task_type", "auto"),
                style_preference=case.get("style_preference"),
                target_audience=case.get("target_audience"),
                aspect_ratio=case.get("aspect_ratio"),
                enable_revision=case.get("enable_revision", True),
            )
            gen_result = service.run_generation(db, request)
            results.append(_evaluate_case(case, gen_result))
    finally:
        db.close()

    passed = sum(1 for r in results if r["routing_correct"] and r["output_exists"])
    report = {
        "generated_at": started_at,
        "total_cases": len(results),
        "passed_cases": passed,
        "pass_rate": round(passed / max(len(results), 1), 3),
        "results": results,
        "summary": {
            "avg_overall_score": round(
                sum(r["overall_score"] for r in results) / max(len(results), 1), 1,
            ),
            "avg_visual_spec_completeness": round(
                sum(r["visual_spec_completeness"] for r in results) / max(len(results), 1), 3,
            ),
            "avg_trace_steps": round(
                sum(r["trace_steps"] for r in results) / max(len(results), 1), 1,
            ),
            "avg_total_duration_ms": int(
                sum(r["total_duration_ms"] for r in results) / max(len(results), 1),
            ),
        },
    }

    if save:
        out_path = settings.reports_dir / "benchmark_report.json"
        out_path.write_text(
            json.dumps(report, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        report["report_path"] = str(out_path)

    return report


if __name__ == "__main__":
    r = run_benchmark()
    print(json.dumps(r, indent=2, ensure_ascii=False))
