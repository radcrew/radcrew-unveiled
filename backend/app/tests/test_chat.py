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


@patch("app.chatbot.feedback.tool_branch.route_send_feedback_call", return_value=None)
@patch("app.chatbot.rag.stream.retrieve_relevant_chunks", return_value=([], 0.0))
def test_chat_retrieval_fallback_returns_200_with_fallback_copy(
    _mock_retrieve: object, _mock_route: object, client: TestClient
) -> None:
    r = client.post("/chat", json={"message": "hello there"})
    assert r.status_code == 200
    assert r.text.count('"type": "chunk"') > 1
    assert "code@radcrew.org" in _stream_content(r.text)
    assert '"type": "done"' in r.text


@patch("app.chatbot.rag.stream.generate_answer", return_value=iter(["Your name is Macho."]))
@patch("app.chatbot.rag.stream.get_settings")
@patch(
    "app.chatbot.rag.stream.retrieve_relevant_chunks",
    return_value=(
        [KnowledgeDocument(id="c1", title="T", text="ctx")],
        0.9,
    ),
)
@patch("app.chatbot.feedback.tool_branch.route_send_feedback_call", return_value=None)
def test_chat_with_history_does_not_force_retrieval_fallback(
    _mock_route: object,
    _mock_retrieve: object,
    mock_settings: MagicMock,
    _mock_generate: object,
    client: TestClient,
) -> None:
    cfg = MagicMock()
    cfg.HUGGINGFACE_API_KEY = "hf_test_token"
    cfg.HUGGINGFACE_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"
    cfg.HUGGINGFACE_PROVIDER = "hf-inference"
    cfg.HUGGINGFACE_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    cfg.HUGGINGFACE_EMBEDDING_PROVIDER = "hf-inference"
    mock_settings.return_value = cfg

    r = client.post(
        "/chat",
        json={
            "message": "What is my name?",
            "history": [{"role": "user", "content": "My name is Macho."}],
        },
    )
    assert r.status_code == 200
    streamed_answer = _stream_content(r.text)
    assert "Your name is Macho." in streamed_answer
    assert "code@radcrew.org" not in streamed_answer
    assert '"type": "done"' in r.text


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


@patch("app.chatbot.rag.stream.generate_answer")
@patch("app.chatbot.rag.stream.retrieve_relevant_chunks")
@patch("app.chatbot.feedback.tool_branch.submit_feedback_via_web3forms")
@patch("app.chatbot.feedback.tool_branch.route_send_feedback_call")
@patch("app.chatbot.feedback.web3forms.get_settings")
@patch("app.chatbot.feedback.tool_branch.get_settings")
def test_chat_feedback_tool_skips_retrieval_and_streams_thanks(
    mock_settings_branch: MagicMock,
    mock_settings_web3: MagicMock,
    mock_route: MagicMock,
    mock_submit: MagicMock,
    mock_retrieve: MagicMock,
    mock_generate: MagicMock,
    client: TestClient,
) -> None:
    mock_route.return_value = ParsedToolCall(
        id="c1",
        name="send_feedback",
        arguments='{"message": "Great product idea", "subject": "Idea"}',
    )
    cfg = MagicMock()
    cfg.HUGGINGFACE_API_KEY = "hf_test_token"
    cfg.HUGGINGFACE_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"
    cfg.HUGGINGFACE_PROVIDER = "hf-inference"
    cfg.HUGGINGFACE_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    cfg.HUGGINGFACE_EMBEDDING_PROVIDER = "hf-inference"
    cfg.WEB3FORMS_ACCESS_KEY = "wf_key"
    cfg.COMPANY_FEEDBACK_EMAIL = "code@radcrew.org"
    mock_settings_branch.return_value = cfg
    mock_settings_web3.return_value = cfg

    r = client.post(
        "/chat",
        json={"message": "Please send this feedback to the company."},
    )
    assert r.status_code == 200
    mock_retrieve.assert_not_called()
    mock_generate.assert_not_called()
    mock_submit.assert_called_once()
    streamed = _stream_content(r.text)
    assert "Thanks" in streamed and "code@radcrew.org" in streamed
    assert '"type": "done"' in r.text


@patch("app.chatbot.rag.stream.retrieve_relevant_chunks")
@patch("app.chatbot.feedback.tool_branch.route_send_feedback_call")
@patch("app.chatbot.feedback.web3forms.get_settings")
@patch("app.chatbot.feedback.tool_branch.get_settings")
def test_chat_feedback_tool_without_web3_key_streams_unavailable_copy(
    mock_settings_branch: MagicMock,
    mock_settings_web3: MagicMock,
    mock_route: MagicMock,
    mock_retrieve: MagicMock,
    client: TestClient,
) -> None:
    mock_route.return_value = ParsedToolCall(
        id="c1",
        name="send_feedback",
        arguments='{"message": "Feedback body"}',
    )
    cfg = MagicMock()
    cfg.HUGGINGFACE_API_KEY = "hf_test_token"
    cfg.HUGGINGFACE_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"
    cfg.HUGGINGFACE_PROVIDER = "hf-inference"
    cfg.HUGGINGFACE_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    cfg.HUGGINGFACE_EMBEDDING_PROVIDER = "hf-inference"
    cfg.WEB3FORMS_ACCESS_KEY = None
    cfg.COMPANY_FEEDBACK_EMAIL = "code@radcrew.org"
    mock_settings_branch.return_value = cfg
    mock_settings_web3.return_value = cfg

    r = client.post("/chat", json={"message": "Send my feedback to the team."})
    assert r.status_code == 200
    mock_retrieve.assert_not_called()
    streamed = _stream_content(r.text)
    assert "couldn't send" in streamed.lower() or "try again" in streamed.lower()
    assert "code@radcrew.org" in streamed
    assert '"type": "done"' in r.text
