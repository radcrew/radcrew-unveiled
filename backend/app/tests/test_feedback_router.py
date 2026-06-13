"""feedback_router_node: maps a (mocked) model reply to a routing decision.

The HuggingFace InferenceClient is patched so no network/LLM call is made; we
only assert how the node translates the reply into ChatState updates.
"""

from __future__ import annotations

import json
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from app.chatbot.graph.nodes.feedback_router.router import (
    feedback_router_node,
    route_feedback_or_rag,
)
from app.schemas import ChatRequest


def _state(message: str = "hello there") -> dict[str, object]:
    return {"body": ChatRequest(message=message), "route": "rag"}


def _completion(content: str) -> SimpleNamespace:
    """Mimic client.chat_completion(...).choices[0].message.content."""
    message = SimpleNamespace(content=content)
    return SimpleNamespace(choices=[SimpleNamespace(message=message)])


def _patched_client(content: str) -> MagicMock:
    client = MagicMock()
    client.chat_completion.return_value = _completion(content)
    return client


def test_route_feedback_or_rag_returns_state_route() -> None:
    assert route_feedback_or_rag({"route": "feedback"}) == "feedback"
    assert route_feedback_or_rag({"route": "rag"}) == "rag"


@patch("app.chatbot.graph.nodes.feedback_router.router.InferenceClient")
def test_feedback_tool_call_routes_to_feedback(mock_client_cls: MagicMock) -> None:
    reply = json.dumps(
        {"tool_call": {"name": "send_feedback", "arguments": {"message": "Nice work"}}}
    )
    mock_client_cls.return_value = _patched_client(reply)

    result = feedback_router_node(_state("I want to leave feedback"))

    assert result["route"] == "feedback"
    assert result["feedback_call"].name == "send_feedback"


@patch("app.chatbot.graph.nodes.feedback_router.router.InferenceClient")
def test_null_tool_call_routes_to_rag(mock_client_cls: MagicMock) -> None:
    mock_client_cls.return_value = _patched_client(json.dumps({"tool_call": None}))

    result = feedback_router_node(_state("what does radcrew do?"))

    assert result == {"route": "rag"}


@patch("app.chatbot.graph.nodes.feedback_router.router.InferenceClient")
def test_client_error_falls_back_to_rag(mock_client_cls: MagicMock) -> None:
    # Provider/network failure must degrade gracefully to RAG, not crash.
    client = MagicMock()
    client.chat_completion.side_effect = RuntimeError("no provider")
    mock_client_cls.return_value = client

    result = feedback_router_node(_state())

    assert result == {"route": "rag"}
