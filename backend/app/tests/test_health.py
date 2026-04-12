"""Tests for ``GET /health``."""

from fastapi.testclient import TestClient

from app.main import app


def test_health_returns_ok_and_chunk_count() -> None:
    with TestClient(app) as client:
        r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data.get("ok") is True
    assert isinstance(data.get("chunks"), int)
