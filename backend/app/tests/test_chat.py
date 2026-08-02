"""POST /chat: validation and streaming responses."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.chatbot.chat import ChatStream
from app.chatbot.knowledge.models import KnowledgeDocument
from app.chatbot.messages import MSG_AI_UNAVAILABLE


def _events(response_text: str) -> list[dict]:
    out: list[dict] = []
    for event in response_text.split("\n\n"):
        if not event.startswith("data: "):
            continue
        payload = event.removeprefix("data: ").strip()
        if not payload:
            continue
        out.append(json.loads(payload))
    return out


def _stream_content(response_text: str) -> str:
    return "".join(
        event["content"]
        for event in _events(response_text)
        if event.get("type") == "chunk" and isinstance(event.get("content"), str)
    )


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



def test_chat_stream_failure_yields_fallback_and_done(client: TestClient) -> None:
    """A raise mid-stream must not surface as an empty 200 body.

    The generators are lazy, so the failure happens after the response headers
    are already sent. Without a guard around the iteration it escapes into the
    ASGI server and the client just sees nothing.
    """

    def exploding_stream():
        raise RuntimeError("no inference provider could stream")
        yield  # pragma: no cover - generator marker

    stream = ChatStream(exploding_stream(), ("How do I start a project?",))
    with patch("app.api.chat.chatbot.generate_chat_stream", return_value=stream):
        r = client.post("/chat", json={"message": "what does radcrew do?"})

    assert r.status_code == 200
    assert _stream_content(r.text) == MSG_AI_UNAVAILABLE
    assert '"type": "done"' in r.text or '"type":"done"' in r.text
    # An apology is not an answer, so it carries no follow-up hints.
    assert [e["type"] for e in _events(r.text)] == ["chunk", "done"]


def test_chat_emits_hints_after_the_answer_and_before_done(client: TestClient) -> None:
    hints = ("How quickly can you start?", "How do I start a project?")
    stream = ChatStream(iter(["We build ", "software."]), hints)

    with patch("app.api.chat.chatbot.generate_chat_stream", return_value=stream):
        r = client.post("/chat", json={"message": "what does radcrew do?"})

    events = _events(r.text)
    assert [e["type"] for e in events] == ["chunk", "chunk", "hints", "done"]
    assert events[2]["hints"] == list(hints)


def test_chat_omits_the_hints_event_when_there_are_none(client: TestClient) -> None:
    """Guardrail blocks and feedback replies reach here with no hints."""
    stream = ChatStream(iter(["I can't help with that."]))

    with patch("app.api.chat.chatbot.generate_chat_stream", return_value=stream):
        r = client.post("/chat", json={"message": "what does radcrew do?"})

    assert [e["type"] for e in _events(r.text)] == ["chunk", "done"]
