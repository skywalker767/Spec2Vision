"""Security helper tests."""

from __future__ import annotations

import pytest

from app.core.errors import SecurityError, ValidationError
from app.core.security import (
    resolve_storage_path,
    validate_trace_id,
    validate_upload_filename,
    validate_user_input,
)
from app.config import get_settings


def test_validate_user_input_rejects_empty():
    with pytest.raises(ValidationError):
        validate_user_input("   ")


def test_validate_upload_rejects_traversal():
    with pytest.raises(SecurityError):
        validate_upload_filename("../secret.env")


def test_validate_upload_rejects_unknown_suffix():
    with pytest.raises(ValidationError):
        validate_upload_filename("slides.pptx")


def test_validate_trace_id_rejects_injection():
    with pytest.raises(SecurityError):
        validate_trace_id("../../etc/passwd")


def test_resolve_storage_path_blocks_escape(tmp_path, monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "generated_dir", tmp_path / "generated")
    settings.generated_dir.mkdir(parents=True)
    with pytest.raises(SecurityError):
        resolve_storage_path("../../outside.png", allowed_roots=[settings.generated_dir])
