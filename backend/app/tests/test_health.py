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


def test_health_reports_provider_and_embedding_availability() -> None:
    """These two fields are what distinguish "up" from "up but cannot answer"."""
    with TestClient(app) as client:
        data = client.get("/health").json()

    assert data.get("provider") in {"openrouter", "huggingface", "none"}
    assert isinstance(data.get("embeddings"), bool)
    assert isinstance(data.get("vector_store"), bool)


def test_health_reports_no_vector_store_without_a_database() -> None:
    """Configured-but-not-indexed reads the same as absent: retrieval is degraded."""
    with TestClient(app) as client:
        assert client.get("/health").json().get("vector_store") is False


def test_health_never_leaks_credentials() -> None:
    """The endpoint is public, so no secret may appear in the payload."""
    from app.core.settings import get_settings

    settings = get_settings()
    secrets = [
        settings.HF_TOKEN,
        settings.OPENROUTER_API_KEY,
        settings.GITHUB_TOKEN,
        settings.WEB_SEARCH_API_KEY,
        settings.WEB3FORMS_ACCESS_KEY,
    ]

    with TestClient(app) as client:
        body = client.get("/health").text

    for secret in secrets:
        if secret:
            assert secret not in body
