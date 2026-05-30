"""Feedback router pre-gate (Solution A): questions bypass the LLM."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from app.schemas import ChatRequest
from app.chatbot.graph.nodes.feedback_router import router
from app.chatbot.graph.nodes.feedback_router.pregate import (
    has_feedback_signal,
    looks_like_question,
    should_skip_llm_route_to_rag,
)


@pytest.mark.parametrize(
    "message",
    [
        "What is RadCrew good at building?",
        "Who are the engineers on the team?",
        "List the services RadCrew offers.",
        "Tell me about the tech stack.",
        "Does RadCrew work with Solana?",
        "how do you handle testing?",
        "What's the contact email?",
    ],
)
def test_questions_detected(message: str) -> None:
    assert looks_like_question(message)


@pytest.mark.parametrize(
    "message",
    [
        "I want to report a bug in the login flow.",
        "Please pass this suggestion to the team.",
        "I have a complaint about the service.",
        "Here is some feedback for you.",
    ],
)
def test_feedback_signals_detected(message: str) -> None:
    assert has_feedback_signal(message)


def test_question_with_feedback_word_defers_to_llm() -> None:
    # A question that also mentions feedback is ambiguous → not auto-RAG.
    assert not should_skip_llm_route_to_rag("What is your feedback process?")


def _state(message: str) -> dict:
    return {"body": ChatRequest(message=message), "knowledge_chunks": []}


@patch.object(router, "InferenceClient")
def test_plain_question_skips_llm_and_routes_to_rag(mock_client: MagicMock) -> None:
    out = router.feedback_router_node(_state("Who is on the RadCrew team?"))
    assert out == {"route": "rag"}
    mock_client.assert_not_called()  # the LLM was never consulted


@patch.object(router, "parse_tool_call_reply", return_value=None)
@patch.object(router, "InferenceClient")
def test_non_question_consults_llm(mock_client: MagicMock, _parse: MagicMock) -> None:
    mock_client.return_value.chat_completion.return_value.choices = [
        MagicMock(message=MagicMock(content="{}"))
    ]
    out = router.feedback_router_node(_state("Here is some feedback for the team."))
    assert out == {"route": "rag"}  # parse returned None → rag, but LLM ran
    mock_client.assert_called_once()
