"""VisionFlow / Spec2Vision FastAPI application."""

from __future__ import annotations

import mimetypes
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import get_settings
from app.core.errors import AppError, SecurityError, ValidationError
from app.core.logging import setup_logging
from app.core.responses import error_response, success_response
from app.core.security import validate_trace_id, validate_upload_filename, validate_user_input
from app.models.database import get_db, init_db
from app.models.schemas import (
    ClarificationRequest,
    ClarificationResponse,
    DeleteResponse,
    DocumentExtractResponse,
    GenerationRequest,
    GenerationResult,
    HealthResponse,
    StatsResponse,
    TaskListResponse,
    TraceResponse,
)
from app.services.generation_service import get_generation_service
from app.tools.document_extractor import DocumentExtractionError

MAX_UPLOAD_BYTES = 15 * 1024 * 1024  # 15 MB
APP_VERSION = "1.0.0"


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    setup_logging(settings.log_level, settings.log_json)
    settings.ensure_dirs()
    init_db()
    yield


app = FastAPI(
    title="Spec2Vision API",
    description="Visual Spec driven multi-agent visual asset generation",
    version=APP_VERSION,
    lifespan=lifespan,
)


@app.middleware("http")
async def attach_request_id(request: Request, call_next):
    request.state.trace_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())[:12]
    response = await call_next(request)
    response.headers["X-Request-ID"] = request.state.trace_id
    return response


@app.exception_handler(AppError)
async def handle_app_error(request: Request, exc: AppError):
    trace_id = getattr(request.state, "trace_id", None)
    return JSONResponse(
        status_code=exc.http_status,
        content=error_response(
            exc.code,
            exc.message,
            recoverable=exc.recoverable,
            details=exc.details,
            trace_id=trace_id,
        ),
    )


@app.get("/health", response_model=HealthResponse)
def health_check(db: Session = Depends(get_db)):
    settings = get_settings()
    db_ok = True
    storage_ok = True
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_ok = False
    try:
        settings.storage_root.mkdir(parents=True, exist_ok=True)
        probe = settings.storage_root / ".health_probe"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink(missing_ok=True)
    except Exception:
        storage_ok = False
    status = "ok" if db_ok and storage_ok else "degraded"
    return HealthResponse(
        status=status,
        llm_provider=settings.llm_provider,
        image_provider=settings.image_provider,
        rag_enabled=settings.rag_enabled,
        database_ok=db_ok,
        storage_ok=storage_ok,
        version=APP_VERSION,
    )


@app.get("/traces/{trace_id}")
def get_trace(trace_id: str, db: Session = Depends(get_db)):
    """Structured trace lookup for observability demos."""
    tid = validate_trace_id(trace_id)
    service = get_generation_service()
    payload = service.get_trace_bundle(db, tid)
    if not payload:
        raise HTTPException(status_code=404, detail=f"Trace {tid} not found")
    return success_response(payload, trace_id=tid)


@app.get("/stats", response_model=StatsResponse)
def get_stats(db: Session = Depends(get_db)):
    service = get_generation_service()
    return service.get_stats(db)


@app.post("/extract", response_model=DocumentExtractResponse)
async def extract_document(file: UploadFile = File(...)):
    data = await file.read()
    if not data:
        raise ValidationError("上传文件为空", http_status=400)
    if len(data) > MAX_UPLOAD_BYTES:
        raise ValidationError(
            "文件过大（上限 15MB）",
            http_status=413,
            details={"max_bytes": MAX_UPLOAD_BYTES},
        )
    filename = validate_upload_filename(file.filename or "document.txt")
    service = get_generation_service()
    try:
        return service.extract_document(filename, data)
    except DocumentExtractionError as exc:
        raise ValidationError(str(exc)) from exc


@app.post("/clarify", response_model=ClarificationResponse)
def clarify_requirements(request: ClarificationRequest):
    request.user_input = validate_user_input(request.user_input)
    service = get_generation_service()
    return service.run_clarify(request)


@app.post("/generate", response_model=GenerationResult)
def generate_visual(
    request: GenerationRequest,
    db: Session = Depends(get_db),
):
    request.user_input = validate_user_input(request.user_input)
    service = get_generation_service()
    try:
        return service.run_generation(db, request)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/tasks", response_model=TaskListResponse)
def list_tasks(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    service = get_generation_service()
    page = service.list_tasks(db, limit=limit, offset=offset)
    return TaskListResponse(
        tasks=page.items,
        items=page.items,
        total=page.total,
        limit=page.limit,
        offset=page.offset,
        returned_count=len(page.items),
        has_next=page.has_next,
    )


@app.get("/tasks/{task_id}", response_model=GenerationResult)
def get_task(task_id: str, db: Session = Depends(get_db)):
    tid = validate_trace_id(task_id)
    service = get_generation_service()
    record = service.get_task(db, tid)
    if not record:
        raise HTTPException(status_code=404, detail=f"Task {tid} not found")
    return record


@app.get("/tasks/{task_id}/asset")
def get_task_asset(task_id: str, db: Session = Depends(get_db)):
    from app.core.security import resolve_storage_path

    tid = validate_trace_id(task_id)
    service = get_generation_service()
    record = service.get_task(db, tid)
    if not record:
        raise HTTPException(status_code=404, detail=f"Task {tid} not found")
    try:
        path = resolve_storage_path(record.output_path)
    except SecurityError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Asset file missing: {path.name}")
    media_type = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
    if path.suffix.lower() == ".svg":
        media_type = "image/svg+xml"
    return FileResponse(str(path), media_type=media_type, filename=path.name)


@app.delete("/tasks/{task_id}", response_model=DeleteResponse)
def delete_task(task_id: str, db: Session = Depends(get_db)):
    tid = validate_trace_id(task_id)
    service = get_generation_service()
    deleted = service.delete_task(db, tid)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Task {tid} not found")
    return DeleteResponse(task_id=tid, deleted=True)
