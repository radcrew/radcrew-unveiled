"""Feedback handler phases (Solution D): ask, cancel, send."""

from __future__ import annotations

import json
from unittest.mock import patch

from app.chatbot.graph.nodes.feedback_handler import handler
from app.chatbot.graph.nodes.feedback_router.parse import ParsedToolCall


def _call(message: str) -> ParsedToolCall:
    return ParsedToolCall(
        id="x", name="send_feedback",
        arguments=json.dumps({"message": message, "subject": None}),
    )


def _text(stream) -> str:
    return "".join(stream)


@patch.object(handler, "submit_feedback")
def test_ask_phase_does_not_send(mock_submit) -> None:
    state = {"feedback_call": _call("The login page is broken."), "feedback_phase": "ask"}
    out = _text(handler.feedback_handler_node(state)["output_stream"])
    mock_submit.assert_not_called()
    assert "Should I forward it to the team?" in out
    assert "The login page is broken." in out


@patch.object(handler, "submit_feedback")
def test_cancel_phase_does_not_send(mock_submit) -> None:
    out = _text(handler.feedback_handler_node({"feedback_phase": "cancel"})["output_stream"])
    mock_submit.assert_not_called()
    assert "won't send" in out


@patch.object(handler, "submit_feedback")
def test_send_phase_submits(mock_submit) -> None:
    state = {"feedback_call": _call("The login page is broken."), "feedback_phase": "send"}
    out = _text(handler.feedback_handler_node(state)["output_stream"])
    mock_submit.assert_called_once_with("The login page is broken.", None)
    assert "has been sent" in out
