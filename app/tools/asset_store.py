"""Local asset storage helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.config import get_settings


def save_text(task_id: str, category: str, filename: str, content: str) -> Path:
    """Save text content to the appropriate storage subdirectory."""
    settings = get_settings()
    dir_map = {
        "prompt": settings.prompts_dir,
        "report": settings.reports_dir,
        "trace": settings.traces_dir,
        "generated": settings.generated_dir,
        "diagram": settings.diagrams_dir,
    }
    base = dir_map.get(category, settings.storage_root)
    base.mkdir(parents=True, exist_ok=True)
    path = base / f"{task_id}_{filename}"
    path.write_text(content, encoding="utf-8")
    return path


def save_json(task_id: str, category: str, filename: str, data: dict[str, Any]) -> Path:
    """Save JSON data to storage."""
    content = json.dumps(data, indent=2, ensure_ascii=False, default=str)
    return save_text(task_id, category, filename, content)


def ensure_dir(category: str) -> Path:
    """Ensure a storage subdirectory exists and return its path."""
    settings = get_settings()
    dir_map = {
        "prompt": settings.prompts_dir,
        "report": settings.reports_dir,
        "trace": settings.traces_dir,
        "generated": settings.generated_dir,
        "diagram": settings.diagrams_dir,
    }
    path = dir_map.get(category, settings.storage_root)
    path.mkdir(parents=True, exist_ok=True)
    return path
