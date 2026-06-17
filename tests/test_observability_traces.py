"""Observability endpoints and trace export."""

from __future__ import annotations

import json

from app.config import get_settings


def test_health_includes_rag_and_storage(client):
    body = client.get("/health").json()
    assert body["status"] in ("ok", "degraded")
    assert "rag_enabled" in body
    assert "database_ok" in body
    assert body["version"]


def test_trace_endpoint_after_generation(client):
    gen = client.post(
        "/generate",
        json={
            "user_input": "简洁商务 PPT 封面",
            "task_type": "ppt_visual",
            "skip_clarification": True,
            "enable_revision": False,
        },
    )
    assert gen.status_code == 200
    task_id = gen.json()["task_id"]
    settings = get_settings()
    trace_file = settings.traces_dir / f"{task_id}.json"
    assert trace_file.exists()
    resp = client.get(f"/traces/{task_id}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["trace_id"] == task_id
    assert body["data"]["traces"]


def test_trace_endpoint_structured_error(client):
    resp = client.get("/traces/notfound999")
    assert resp.status_code == 404
