"""End-to-end POST /chat with OpenRouter selected as the provider.

The unit tests cover the OpenRouter client in isolation. This one drives the
whole request path (settings gate, graph, guardrails, retrieval, SSE encoding)
with only the outbound HTTP call replaced, so a wiring mistake between those
layers fails here rather than in production.
"""

from __future__ import annotations

import json
from io import BytesIO
from typing import Any, Iterator

import pytest
from fastapi.testclient import TestClient

from app.chatbot.openrouter import client as or_client
from app.core.settings import get_settings
from app.main import app

_ANSWER = "RadCrew builds full stack products."


def _sse_stream(text: str) -> BytesIO:
    chunk = "data: " + json.dumps({"choices": [{"delta": {"content": text}}]})
    return BytesIO(f"{chunk}\ndata: [DONE]\n".encode("utf-8"))


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
def openrouter_env(monkeypatch: pytest.MonkeyPatch) -> Iterator[list[dict[str, Any]]]:
    """Select OpenRouter and capture every outbound payload.

    Settings are lru_cached and every module resolves them through the same
    ``get_settings``, so clearing the cache after setting the environment is
    enough to reconfigure the whole app. It is cleared again on the way out so
    later tests do not inherit this provider.
    """
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-integration-test")
    # Keep the regex rails on and the two inference-backed rails off, so the
    # test asserts one deliberate generation call rather than three.
    monkeypatch.setenv("GUARDRAIL_INPUT_HARMFUL_ENABLED", "false")
    monkeypatch.setenv("GUARDRAIL_OUTPUT_GROUNDEDNESS_ENABLED", "false")
    get_settings.cache_clear()

    payloads: list[dict[str, Any]] = []

    def fake_open(payload: dict[str, Any]) -> BytesIO:
        payloads.append(payload)
        return _sse_stream(_ANSWER)

    monkeypatch.setattr(or_client, "_open", fake_open)
    # Force lexical retrieval so the test never reaches out for embeddings.
    monkeypatch.setattr(
        "app.chatbot.graph.nodes.rag_answer.retrieval.semantic_similarities",
        lambda documents, query: [0.0] * len(documents),
    )

    yield payloads

    get_settings.cache_clear()


def test_chat_streams_an_answer_through_openrouter(
    openrouter_env: list[dict[str, Any]],
) -> None:
    with TestClient(app) as client:
        response = client.post(
            "/chat",
            json={
                "message": "what services does radcrew offer?",
                "history": [
                    {"role": "user", "content": "hello"},
                    {"role": "assistant", "content": "Hi there."},
                ],
            },
        )

    assert response.status_code == 200
    assert _ANSWER in _stream_content(response.text)
    assert '"type": "done"' in response.text or '"type":"done"' in response.text

    assert openrouter_env, "no request reached the OpenRouter client"
    generation = openrouter_env[-1]
    assert generation["stream"] is True
    assert generation["messages"][0]["role"] == "system"
    assert generation["messages"][-1]["role"] == "user"


def test_chat_provider_selection_survives_the_whole_request(
    openrouter_env: list[dict[str, Any]],
) -> None:
    """Nothing in the request path may fall back to the Hugging Face client."""
    with TestClient(app) as client:
        client.post(
            "/chat",
            json={
                "message": "what services does radcrew offer?",
                "history": [{"role": "user", "content": "hello"}],
            },
        )

    assert get_settings().llm_provider() == "openrouter"
    assert all("model" in payload for payload in openrouter_env)
