"""Feedback router: pre-gate, confirmation flow, and routing-decision tests."""

from __future__ import annotations

import json
import logging
from unittest.mock import MagicMock, patch

import pytest

from app.schemas import ChatHistoryMessage, ChatRequest
from app.chatbot.messages import MSG_FEEDBACK_CONFIRM
from app.chatbot.graph.nodes.feedback_router import router
from app.chatbot.graph.nodes.feedback_router.parse import parse_routing_intent
from app.chatbot.graph.nodes.feedback_router.confirm import (
    classify_confirmation,
    is_affirmation,
    is_negation,
)
from app.chatbot.graph.nodes.feedback_router.fuzzy import damerau_levenshtein, fuzzy_in
from app.chatbot.graph.nodes.feedback_router.pregate import (
    has_feedback_signal,
    is_smalltalk,
    looks_like_question,
    should_skip_llm_route_to_rag,
)


@pytest.mark.parametrize(
    "message",
    [
        "hi", "hello", "hey", "Hello!", "hey there", "Hi there!",
        "good morning", "good evening", "thanks", "thank you",
        "Thanks a lot!", "thank you so much", "cheers", "ok cool",
        "hiya", "yo", "how are you?", "what's up", "HELLO", "   hi   ",
    ],
)
def test_smalltalk_detected(message: str) -> None:
    assert is_smalltalk(message)


@pytest.mark.parametrize(
    "message",
    [
        "hi, what does RadCrew do?",
        "who is on the team?",
        "tell me about radcrew",
        "hello can you help me build an app",
        "thanks for the info, who is jesus?",
        "team",  # ambiguous single word, not a greeting token
        "is this thing on?",
    ],
)
def test_non_smalltalk_not_detected(message: str) -> None:
    assert not is_smalltalk(message)


def test_smalltalk_skips_llm_and_routes_to_rag() -> None:
    # Greetings should bypass the LLM classifier and go straight to RAG.
    assert should_skip_llm_route_to_rag("hello")
    assert should_skip_llm_route_to_rag("thanks!")


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
        # Option 1: typo tolerance — "waht"/"explian" still read as questions.
        "waht does RadCrew build",
        "explian the tech stack",
    ],
)
def test_questions_detected(message: str) -> None:
    assert looks_like_question(message)


def test_typo_question_does_not_overmatch_feedback() -> None:
    # A short non-question first word must not fuzzy-match a question starter.
    assert not looks_like_question("the homepage looks great")


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
    return {"body": ChatRequest(message=message), "knowledge_documents": []}


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


@pytest.mark.parametrize(
    "yes",
    [
        "yes", "yes please", "sure", "ok", "go ahead", "send it",
        # Option 2: terse single tokens.
        "y", "ya", "k", "yeah!",
        # Option 1: typo tolerance for longer tokens.
        "definitley", "confrim", "absolutley",
    ],
)
def test_affirmations(yes: str) -> None:
    assert is_affirmation(yes)


@pytest.mark.parametrize(
    "no",
    [
        "no", "nope", "cancel", "don't", "never mind", "not now",
        # Option 2: terse single tokens.
        "n", "nvm",
        # Option 1: typo tolerance for longer tokens.
        "cancl", "cancel",
    ],
)
def test_negations(no: str) -> None:
    assert is_negation(no)


def test_short_tokens_are_not_fuzzed_across_intents() -> None:
    # "go" must not become "no": short tokens require an exact match.
    assert not is_negation("go")
    assert not is_affirmation("not really")


@pytest.mark.parametrize(
    "a, b, expected",
    [("yes", "yes", 0), ("yse", "yes", 1), ("cancl", "cancel", 1), ("abc", "xyz", 3)],
)
def test_damerau_levenshtein(a: str, b: str, expected: int) -> None:
    assert damerau_levenshtein(a, b) == expected


def test_fuzzy_in_respects_min_length() -> None:
    assert fuzzy_in("definitley", {"definitely"})
    assert not fuzzy_in("go", {"no"})  # too short to fuzzy-match


@pytest.mark.parametrize(
    "message, expected",
    [
        ("yes please", "yes"),
        ("no thanks", "no"),
        ("definitley", "yes"),
        ("yse", "unknown"),      # transposed typo on a 3-char token → defer to LLM
        ("tell me more", "unknown"),
    ],
)
def test_classify_confirmation(message: str, expected: str) -> None:
    assert classify_confirmation(message) == expected


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
    out = router.feedback_router_node({"body": body, "knowledge_documents": []})
    assert out["route"] == "feedback"
    assert out["feedback_phase"] == "send"
    assert json.loads(out["feedback_call"].arguments)["message"] == "The contact form is broken."
    mock_client.assert_not_called()  # no LLM re-classification on confirm


@patch.object(router, "InferenceClient")
def test_confirmation_no_cancels(mock_client: MagicMock) -> None:
    body = ChatRequest(message="no thanks", history=_confirm_history("The contact form is broken."))
    out = router.feedback_router_node({"body": body, "knowledge_documents": []})
    assert out == {"route": "feedback", "feedback_phase": "cancel"}
    mock_client.assert_not_called()


# --- Option 3: LLM fallback for ambiguous confirmation replies ---


@patch.object(router, "classify_confirmation_via_llm")
@patch.object(router, "InferenceClient")
def test_clear_confirmation_skips_llm_fallback(
    mock_client: MagicMock, mock_llm: MagicMock
) -> None:
    # A deterministic "yes" must not pay for the LLM round-trip.
    body = ChatRequest(message="yes please", history=_confirm_history("x"))
    router.feedback_router_node({"body": body, "knowledge_documents": []})
    mock_llm.assert_not_called()


@patch.object(router, "classify_confirmation_via_llm", return_value="yes")
@patch.object(router, "InferenceClient")
def test_ambiguous_confirmation_uses_llm_and_sends(
    mock_client: MagicMock, mock_llm: MagicMock
) -> None:
    # "yse" is unknown to the deterministic gate → LLM resolves it → send.
    body = ChatRequest(message="yse", history=_confirm_history("The contact form is broken."))
    out = router.feedback_router_node({"body": body, "knowledge_documents": []})
    assert out["route"] == "feedback"
    assert out["feedback_phase"] == "send"
    assert json.loads(out["feedback_call"].arguments)["message"] == "The contact form is broken."
    mock_llm.assert_called_once()
    mock_client.assert_not_called()  # main routing LLM never consulted


@patch.object(router, "classify_confirmation_via_llm", return_value="unsure")
@patch.object(router, "parse_routing_intent", return_value="question")
@patch.object(router, "InferenceClient")
def test_ambiguous_confirmation_llm_unsure_routes_normally(
    mock_client: MagicMock, _parse: MagicMock, _llm: MagicMock
) -> None:
    mock_client.return_value.chat_completion.return_value.choices = [
        MagicMock(message=MagicMock(content="{}"))
    ]
    body = ChatRequest(message="hmm what about it", history=_confirm_history("x"))
    out = router.feedback_router_node({"body": body, "knowledge_documents": []})
    assert out == {"route": "rag"}  # pending feedback dropped, re-classified


# --- Solution F: routing decisions are logged ---


def test_routing_decision_is_logged(caplog) -> None:
    with caplog.at_level(logging.INFO, logger="app.chatbot.graph.nodes.feedback_router.router"):
        router.feedback_router_node(_state("What does RadCrew build?"))
    assert any(
        "[routing]" in m and "route=rag" in m and "stage=pregate_question" in m
        for m in caplog.messages
    )


# Ported from main: route_feedback_or_rag is a pure passthrough of state["route"].
def test_route_feedback_or_rag_returns_state_route() -> None:
    assert router.route_feedback_or_rag({"route": "feedback"}) == "feedback"
    assert router.route_feedback_or_rag({"route": "rag"}) == "rag"
