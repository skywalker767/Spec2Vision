"""Tests for mock image provider and demo mode."""

from __future__ import annotations

import json

import pytest

from app.config import get_settings
from app.graph import visionflow_graph as vg_module
from app.models.schemas import GenerationRequest
from app.services import generation_service as svc_module
from app.services.generation_service import GenerationService
from app.tools.image_factory import get_image_generator
from app.tools.mock_image_generator import MockImageGenerator


@pytest.fixture
def mock_env(monkeypatch):
    monkeypatch.setenv("DEMO_MODE", "true")
    monkeypatch.setenv("LLM_PROVIDER", "mock")
    monkeypatch.setenv("IMAGE_PROVIDER", "mock")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    get_settings.cache_clear()
    vg_module._graph_instance = None
    svc_module._service = None
    yield
    get_settings.cache_clear()
    vg_module._graph_instance = None
    svc_module._service = None


def test_mock_image_generator_creates_valid_png(mock_env, tmp_path, monkeypatch):
    monkeypatch.setenv("STORAGE_ROOT", str(tmp_path))
    get_settings.cache_clear()
    gen = get_image_generator()
    assert isinstance(gen, MockImageGenerator)
    path = gen.generate("abc12345", "ecommerce_banner", "Test Title", "prompt text", "16:9")
    assert path.exists()
    assert path.suffix == ".png"
    assert path.stat().st_size > 50
    meta_path = path.with_suffix(".mock.json")
    assert meta_path.exists()
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    assert meta["provider"] == "mock"
    assert meta["task_type"] == "ecommerce_banner"
    assert meta["normalized_size"] == "1792x1024"


def test_mock_end_to_end_generation(mock_env, tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'test.db'}")
    get_settings.cache_clear()
    vg_module._graph_instance = None
    svc_module._service = None

    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    from app.models.database import Base

    engine = create_engine(f"sqlite:///{tmp_path / 'test.db'}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    db = sessionmaker(bind=engine)()

    service = GenerationService()
    req = GenerationRequest(
        user_input="为夏季冰咖啡制作电商促销主图 banner",
        task_type="auto",
        skip_clarification=True,
        enable_revision=False,
    )
    result = service.run_generation(db, req)
    assert result.output_path
    assert result.evaluation.overall_score >= 0
    asset_meta = [t for t in result.traces if t.step == "generate_asset"]
    assert asset_meta
    assert asset_meta[0].metadata.get("generation_mode") == "mock"
    db.close()
