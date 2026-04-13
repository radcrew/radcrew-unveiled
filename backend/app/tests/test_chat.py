"""POST /chat: validation and streaming responses."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.chatbot.huggingface.tool_routing import ParsedToolCall
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


@patch("app.chatbot.rag.stream.generate_answer", return_value=iter(["Your name is Macho."]))
@patch("app.chatbot.rag.stream.get_settings")
@patch(
    "app.chatbot.rag.stream.retrieve_relevant_chunks",
    return_value=(
        [KnowledgeDocument(id="c1", title="T", text="ctx")],
        0.9,
    ),
)

@patch("app.api.chat.chatbot.generate_chat_stream", side_effect=RuntimeError("no provider"))
def test_chat_stream_failure_returns_streamed_fallback(_mock_stream: object, client: TestClient) -> None:
    r = client.post("/chat", json={"message": "hello world"})
    assert r.status_code == 200
    assert '"type": "chunk"' in r.text
    assert "The AI service is temporarily unavailable" in r.text
    assert '"type": "done"' in r.text


@patch("app.chatbot.rag.stream.get_settings")
@patch("app.chatbot.rag.stream.retrieve_relevant_chunks")
def test_chat_missing_hf_key_returns_200_with_config_message(
    mock_retrieve: MagicMock,
    mock_settings: MagicMock,
    client: TestClient,
) -> None:
    mock_retrieve.return_value = (
        [KnowledgeDocument(id="c1", title="Title", text="snippet text", url=None)],
        0.9,
    )
    cfg = MagicMock()
    cfg.HUGGINGFACE_API_KEY = None
    mock_settings.return_value = cfg

    r = client.post("/chat", json={"message": "hello world"})
    assert r.status_code == 200
    assert '"type": "chunk"' in r.text
    streamed_answer = _stream_content(r.text)
    assert "HUGGINGFACE_API_KEY" in streamed_answer
    assert "backend/.env" in streamed_answer
    assert '"type": "done"' in r.text
