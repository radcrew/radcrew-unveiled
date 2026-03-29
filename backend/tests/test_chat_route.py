"""POST /chat: validation, fallback, and error handling (parity with backend/src/server.ts)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models import KnowledgeChunkScored


@pytest.fixture
def client() -> TestClient:
    with TestClient(app) as c:
        yield c


def test_chat_invalid_message_length_returns_400(client: TestClient) -> None:
    r = client.post("/chat", json={"message": "x"})
    assert r.status_code == 400
    assert r.json() == {"error": "Invalid request payload."}


def test_chat_invalid_history_returns_400(client: TestClient) -> None:
    r = client.post(
        "/chat",
        json={
            "message": "hello there",
            "history": [{"role": "user", "content": "x"}] * 13,
        },
    )
    assert r.status_code == 400
    assert r.json() == {"error": "Invalid request payload."}


@patch("app.chat.service.retrieve_relevant_chunks", return_value=[])
def test_chat_retrieval_fallback_returns_200_with_fallback_copy(_mock: object, client: TestClient) -> None:
    r = client.post("/chat", json={"message": "hello there"})
    assert r.status_code == 200
    body = r.json()
    assert body["confidence"] == 0.2
    assert body["sources"] == []
    assert "hello@radcrew.dev" in body["answer"]


@patch("app.chat.service.generate_answer", side_effect=RuntimeError("no provider"))
@patch("app.chat.service.get_settings")
@patch("app.chat.service.retrieve_relevant_chunks")
def test_chat_hf_failure_returns_502(
    mock_retrieve: MagicMock,
    mock_settings: MagicMock,
    _mock_gen: object,
    client: TestClient,
) -> None:
    mock_retrieve.return_value = [
        KnowledgeChunkScored(
            id="c1",
            title="Title",
            text="snippet text",
            tokens=["hello", "world"],
            score=2.0,
            url=None,
        )
    ]
    cfg = MagicMock()
    cfg.HUGGINGFACE_API_KEY = "token"
    cfg.HUGGINGFACE_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"
    cfg.HUGGINGFACE_PROVIDER = "hf-inference"
    mock_settings.return_value = cfg

    r = client.post("/chat", json={"message": "hello world"})
    assert r.status_code == 502
    assert r.json()["error"].startswith("The AI service is temporarily unavailable")


@patch("app.chat.service.get_settings")
@patch("app.chat.service.retrieve_relevant_chunks")
def test_chat_missing_hf_key_returns_200_with_config_message(
    mock_retrieve: MagicMock,
    mock_settings: MagicMock,
    client: TestClient,
) -> None:
    mock_retrieve.return_value = [
        KnowledgeChunkScored(
            id="c1",
            title="Title",
            text="snippet text",
            tokens=["hello", "world"],
            score=2.0,
            url=None,
        )
    ]
    cfg = MagicMock()
    cfg.HUGGINGFACE_API_KEY = None
    mock_settings.return_value = cfg

    r = client.post("/chat", json={"message": "hello world"})
    assert r.status_code == 200
    body = r.json()
    assert body["confidence"] == 0
    assert body["sources"] == []
    assert "HUGGINGFACE_API_KEY" in body["answer"]
    assert "backend/.env" in body["answer"]
