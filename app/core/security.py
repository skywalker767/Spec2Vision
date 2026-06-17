"""Input validation and path safety helpers."""

from __future__ import annotations

import re
from pathlib import Path

from app.config import PROJECT_ROOT, get_settings
from app.core.errors import SecurityError, ValidationError

ALLOWED_UPLOAD_SUFFIXES = {".pdf", ".txt", ".md", ".markdown"}
MAX_USER_INPUT_LENGTH = 8000
MAX_PROMPT_LENGTH = 12000

_SAFE_ID = re.compile(r"^[a-zA-Z0-9_-]{1,64}$")


def validate_user_input(text: str, *, field: str = "user_input") -> str:
    cleaned = (text or "").strip()
    if not cleaned:
        raise ValidationError(f"{field} 不能为空")
    if len(cleaned) > MAX_USER_INPUT_LENGTH:
        raise ValidationError(
            f"{field} 超过长度上限 {MAX_USER_INPUT_LENGTH} 字符",
            details={"max_length": MAX_USER_INPUT_LENGTH},
        )
    return cleaned


def validate_upload_filename(filename: str) -> str:
    raw = filename or "upload"
    if ".." in raw or raw.strip().startswith("."):
        raise SecurityError("非法文件名")
    name = Path(raw).name
    suffix = Path(name).suffix.lower()
    if suffix not in ALLOWED_UPLOAD_SUFFIXES:
        raise ValidationError(
            f"不支持的文件类型: {suffix or '(无扩展名)'}",
            details={"allowed": sorted(ALLOWED_UPLOAD_SUFFIXES)},
        )
    return name


def validate_trace_id(trace_id: str) -> str:
    tid = (trace_id or "").strip()
    if not _SAFE_ID.match(tid):
        raise SecurityError("非法 trace_id")
    return tid


def resolve_storage_path(relative_or_absolute: str, *, allowed_roots: list[Path] | None = None) -> Path:
    """Resolve a path and ensure it stays under approved storage roots."""
    settings = get_settings()
    roots = allowed_roots or [
        settings.generated_dir,
        settings.diagrams_dir,
        settings.prompts_dir,
        settings.reports_dir,
        settings.traces_dir,
    ]
    raw = Path(relative_or_absolute)
    candidate = raw if raw.is_absolute() else (PROJECT_ROOT / raw)
    resolved = candidate.resolve()
    for root in roots:
        root_resolved = root.resolve()
        try:
            resolved.relative_to(root_resolved)
            return resolved
        except ValueError:
            continue
    raise SecurityError("路径不在允许的存储目录内")


def sanitize_prompt_injection_block(text: str) -> str:
    """Mark user content boundaries for downstream LLM calls."""
    cleaned = validate_user_input(text)
    return f"[USER_INPUT_START]\n{cleaned}\n[USER_INPUT_END]"
