"""Feedback router pre-gate (Solution A): questions bypass the LLM."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from app.schemas import ChatHistoryMessage, ChatRequest
from app.chatbot.messages import MSG_FEEDBACK_CONFIRM
from app.chatbot.graph.nodes.feedback_router import router
from app.chatbot.graph.nodes.feedback_router.parse import parse_routing_intent
from app.chatbot.graph.nodes.feedback_router.confirm import is_affirmation, is_negation
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


@patch.object(router, "parse_routing_intent", return_value="question")
@patch.object(router, "InferenceClient")
def test_non_question_consults_llm(mock_client: MagicMock, _parse: MagicMock) -> None:
    mock_client.return_value.chat_completion.return_value.choices = [
        MagicMock(message=MagicMock(content="{}"))
    ]
    out = router.feedback_router_node(_state("The new homepage layout looks great."))
    assert out == {"route": "rag"}  # classifier said question → rag, but LLM ran
    mock_client.assert_called_once()


@pytest.mark.parametrize(
    "text, expected",
    [
        ('{"intent": "feedback"}', "feedback"),
        ('{"intent": "question"}', "question"),
        ("not json at all", "question"),  # malformed → safe default
        (None, "question"),
    ],
)
def test_parse_routing_intent(text, expected) -> None:
    assert parse_routing_intent(text) == expected


# --- Solution D: confirm before sending ---


@pytest.mark.parametrize("yes", ["yes", "yes please", "sure", "ok", "go ahead", "send it"])
def test_affirmations(yes: str) -> None:
    assert is_affirmation(yes)


@pytest.mark.parametrize("no", ["no", "nope", "cancel", "don't", "never mind", "not now"])
def test_negations(no: str) -> None:
    assert is_negation(no)


@patch.object(router, "parse_routing_intent", return_value="feedback")
@patch.object(router, "InferenceClient")
def test_detected_feedback_asks_before_sending(mock_client: MagicMock, _parse: MagicMock) -> None:
    mock_client.return_value.chat_completion.return_value.choices = [
        MagicMock(message=MagicMock(content="{}"))
    ]
    out = router.feedback_router_node(_state("Pass this note to the crew about the layout."))
    assert out["route"] == "feedback"
    assert out["feedback_phase"] == "ask"  # does NOT send on first contact
    assert json.loads(out["feedback_call"].arguments)["message"] == "Pass this note to the crew about the layout."


def _confirm_history(original: str):
    return [
        ChatHistoryMessage(role="user", content=original),
        ChatHistoryMessage(role="assistant", content=MSG_FEEDBACK_CONFIRM.format(body=original)),
    ]


@patch.object(router, "InferenceClient")
def test_confirmation_yes_sends_original(mock_client: MagicMock) -> None:
    body = ChatRequest(message="yes please", history=_confirm_history("The contact form is broken."))
    out = router.feedback_router_node({"body": body, "knowledge_chunks": []})
    assert out["route"] == "feedback"
    assert out["feedback_phase"] == "send"
    assert json.loads(out["feedback_call"].arguments)["message"] == "The contact form is broken."
    mock_client.assert_not_called()  # no LLM re-classification on confirm


@patch.object(router, "InferenceClient")
def test_confirmation_no_cancels(mock_client: MagicMock) -> None:
    body = ChatRequest(message="no thanks", history=_confirm_history("The contact form is broken."))
    out = router.feedback_router_node({"body": body, "knowledge_chunks": []})
    assert out == {"route": "feedback", "feedback_phase": "cancel"}
    mock_client.assert_not_called()
