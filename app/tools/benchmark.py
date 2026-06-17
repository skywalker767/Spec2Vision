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
BENCHMARK_DIR = EXAMPLES_DIR / "benchmark"

# 15 benchmark cases: 3 legacy + 12 expanded
BENCHMARK_FILES = [
    "ecommerce_case.json",
    "academic_case.json",
    "ppt_case.json",
    "benchmark/ecom_skincare.json",
    "benchmark/ecom_phone.json",
    "benchmark/ecom_food.json",
    "benchmark/ecom_ambiguous.json",
    "benchmark/edu_climate.json",
    "benchmark/edu_math.json",
    "benchmark/edu_history.json",
    "benchmark/edu_ambiguous.json",
    "benchmark/acad_nlp.json",
    "benchmark/acad_cv.json",
    "benchmark/acad_biology.json",
    "benchmark/acad_mixed.json",
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


def _check_required_fields(spec: VisualSpec, required: list[str]) -> dict[str, bool]:
    """Check nested required spec field paths."""
    data = spec.model_dump()
    results: dict[str, bool] = {}
    for path in required:
        parts = path.split(".")
        cur: object = data
        ok = True
        for part in parts:
            if not isinstance(cur, dict) or part not in cur:
                ok = False
                break
            cur = cur[part]
        if ok:
            if isinstance(cur, list):
                ok = len(cur) > 0
            elif isinstance(cur, str):
                ok = bool(cur.strip())
            else:
                ok = cur is not None
        results[path] = ok
    return results


def _evaluate_case(case: dict, result: GenerationResult) -> dict:
    expected_type = case.get("expected_task_type", "")
    output_path = Path(result.output_path) if result.output_path else None
    min_score = int(case.get("min_evaluation_score", 50))
    required_fields = case.get("required_spec_fields", [])
    field_checks = _check_required_fields(result.visual_spec, required_fields)
    score_ok = result.evaluation.overall_score >= min_score
    fields_ok = all(field_checks.values()) if field_checks else True

    return {
        "case_id": case.get("id", case.get("_file", "")),
        "case_file": case.get("_file", ""),
        "task_id": result.task_id,
        "expected_task_type": expected_type,
        "actual_task_type": result.task_type,
        "routing_correct": result.task_type == expected_type,
        "visual_spec_completeness": _visual_spec_completeness(result.visual_spec),
        "required_field_checks": field_checks,
        "required_fields_ok": fields_ok,
        "prompt_length": len(result.prompt or ""),
        "overall_score": result.evaluation.overall_score,
        "min_evaluation_score": min_score,
        "score_meets_threshold": score_ok,
        "output_exists": bool(output_path and output_path.exists()),
        "output_path": result.output_path,
        "trace_steps": len(result.traces),
        "total_duration_ms": sum(t.duration_ms for t in result.traces),
        "passed": (
            result.task_type == expected_type
            and bool(output_path and output_path.exists())
            and score_ok
            and fields_ok
        ),
    }


def _markdown_summary(report: dict) -> str:
    lines = [
        "# VisionFlow Benchmark Report",
        "",
        f"- Generated at: {report.get('generated_at', '')}",
        f"- Total cases: {report.get('total_cases', 0)}",
        f"- Passed: {report.get('passed_cases', 0)}",
        f"- Pass rate: {report.get('pass_rate', 0):.1%}",
        "",
        "## Summary",
        "",
    ]
    summary = report.get("summary", {})
    for key, val in summary.items():
        lines.append(f"- {key}: {val}")
    lines.extend(["", "## Results", ""])
    for r in report.get("results", []):
        status = "PASS" if r.get("passed") else "FAIL"
        lines.append(
            f"- [{status}] {r.get('case_id', r.get('case_file'))}: "
            f"type={r.get('actual_task_type')} score={r.get('overall_score')} "
            f"routing={'ok' if r.get('routing_correct') else 'miss'}"
        )
    return "\n".join(lines) + "\n"


def run_benchmark(save: bool = True, case_files: list[str] | None = None) -> dict:
    """Run benchmark cases and produce JSON + optional markdown report."""
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
    files = case_files or BENCHMARK_FILES

    try:
        for rel_path in files:
            path = EXAMPLES_DIR / rel_path.replace("/", "\\") if "\\" in rel_path else EXAMPLES_DIR / rel_path
            if not path.exists():
                path = EXAMPLES_DIR / Path(rel_path).name
            case = json.loads(path.read_text(encoding="utf-8"))
            case["_file"] = rel_path

            request = GenerationRequest(
                user_input=case["user_input"],
                task_type=case.get("task_type", "auto"),
                style_preference=case.get("style_preference"),
                target_audience=case.get("target_audience"),
                aspect_ratio=case.get("aspect_ratio"),
                enable_revision=case.get("enable_revision", False),
                skip_clarification=True,
            )
            gen_result = service.run_generation(db, request)
            results.append(_evaluate_case(case, gen_result))
    finally:
        db.close()

    passed = sum(1 for r in results if r["passed"])
    report = {
        "generated_at": started_at,
        "mode": "mock" if settings.demo_mode or settings.image_provider == "mock" else settings.image_provider,
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
            "routing_accuracy": round(
                sum(1 for r in results if r["routing_correct"]) / max(len(results), 1), 3,
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
        json_path = settings.reports_dir / "benchmark_report.json"
        json_path.write_text(
            json.dumps(report, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        report["report_path"] = str(json_path)

        md_path = settings.reports_dir / "benchmark_report.md"
        md_path.write_text(_markdown_summary(report), encoding="utf-8")
        report["markdown_report_path"] = str(md_path)

    return report


if __name__ == "__main__":
    r = run_benchmark()
    print(json.dumps(r, indent=2, ensure_ascii=False))
