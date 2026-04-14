"""POST /chat: validation and streaming responses."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.chatbot.knowledge.models import KnowledgeDocument


def _stream_content(response_text: str) -> str:
    out: list[str] = []
    for event in response_text.split("\n\n"):
        if not event.startswith("data: "):
            continue
        payload = event.removeprefix("data: ").strip()
        if not payload:
            continue
        parsed = json.loads(payload)
        if parsed.get("type") == "chunk" and isinstance(parsed.get("content"), str):
            out.append(parsed["content"])
    return "".join(out)


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


@patch("app.api.chat.chatbot.generate_chat_stream", side_effect=RuntimeError("no provider"))
def test_chat_stream_failure_returns_streamed_fallback(_mock_stream: object, client: TestClient) -> None:
    r = client.post("/chat", json={"message": "hello world"})
    assert r.status_code == 200
    assert '"type": "chunk"' in r.text
    assert "The AI service is temporarily unavailable" in r.text
    assert '"type": "done"' in r.text

