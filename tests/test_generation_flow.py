"""Integration tests for generation flow."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.models.database import Base, get_db
from app.models.schemas import GenerationRequest, GenerationResult
from app.services.generation_service import GenerationService

EXAMPLES_DIR = Path(__file__).resolve().parent.parent / "examples"
EXAMPLE_FILES = [
    "ecommerce_case.json",
    "academic_case.json",
    "ppt_case.json",
]


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(bind=engine)

    def override_get_db():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    yield session
    session.close()


def _load_example(name: str) -> dict:
    return json.loads((EXAMPLES_DIR / name).read_text(encoding="utf-8"))


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert "llm_provider" in body
    assert "image_provider" in body


@pytest.mark.parametrize("example_file", EXAMPLE_FILES)
def test_generation_service_with_examples(client, example_file):
    """Full flow via API using three example cases."""
    case = _load_example(example_file)
    payload = {
        "user_input": case["user_input"],
        "task_type": case.get("task_type", "auto"),
        "style_preference": case.get("style_preference"),
        "target_audience": case.get("target_audience"),
        "aspect_ratio": case.get("aspect_ratio"),
        "enable_revision": case.get("enable_revision", True),
    }
    resp = client.post("/generate", json=payload)
    assert resp.status_code == 200, resp.text

    data = resp.json()
    assert data["task_type"] == case["expected_task_type"]
    assert data["prompt"]
    assert len(data["traces"]) >= 5
    assert data["visual_spec"] is not None
    assert data["evaluation"]["overall_score"] >= 0

    output = Path(data["output_path"])
    assert output.exists(), f"output not found: {output}"

    expected_type = case["expected_output_type"]
    if expected_type == "svg":
        assert output.suffix.lower() == ".svg"
    else:
        assert output.suffix.lower() in (".png", ".jpg", ".jpeg")


def test_generation_service_direct(db_session):
    """Call GenerationService directly and validate GenerationResult."""
    case = _load_example("ecommerce_case.json")
    request = GenerationRequest(
        user_input=case["user_input"],
        task_type=case.get("task_type", "auto"),
        enable_revision=True,
    )
    service = GenerationService()
    result = service.run_generation(db_session, request)

    assert isinstance(result, GenerationResult)
    assert result.task_type == "ecommerce_banner"
    assert result.prompt
    assert len(result.traces) >= 5
    assert Path(result.output_path).exists()


def test_list_tasks(client):
    case = _load_example("ppt_case.json")
    client.post(
        "/generate",
        json={"user_input": case["user_input"], "task_type": "auto"},
    )
    resp = client.get("/tasks")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] >= 1
    assert "task_id" in body["tasks"][0]


def test_stats_endpoint(client):
    case = _load_example("ppt_case.json")
    client.post("/generate", json={"user_input": case["user_input"], "task_type": "auto"})

    resp = client.get("/stats")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total_tasks"] >= 1
    assert body["by_task_type"]
    assert "llm_provider" in body
    assert "score_buckets" in body


def test_asset_and_delete_endpoints(client):
    case = _load_example("ppt_case.json")
    gen = client.post(
        "/generate", json={"user_input": case["user_input"], "task_type": "auto"}
    )
    task_id = gen.json()["task_id"]

    asset = client.get(f"/tasks/{task_id}/asset")
    assert asset.status_code == 200
    assert asset.content

    deleted = client.delete(f"/tasks/{task_id}")
    assert deleted.status_code == 200
    assert deleted.json()["deleted"] is True

    assert client.get(f"/tasks/{task_id}").status_code == 404
    assert client.delete(f"/tasks/{task_id}").status_code == 404
