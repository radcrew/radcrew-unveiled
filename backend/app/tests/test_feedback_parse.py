"""parse_tool_call_reply: turning a model JSON reply into a routing decision."""

from __future__ import annotations

import json

import pytest

from app.chatbot.graph.nodes.feedback_router.parse import (
    ParsedToolCall,
    parse_tool_call_reply,
)


def test_feedback_tool_call_is_parsed() -> None:
    reply = json.dumps(
        {
            "tool_call": {
                "name": "send_feedback",
                "arguments": {"message": "Love the site", "subject": "Praise"},
            }
        }
    )

    result = parse_tool_call_reply(reply)

    assert isinstance(result, ParsedToolCall)
    assert result.id == "route-reply"
    assert result.name == "send_feedback"
    # arguments is serialized JSON of the tool arguments.
    assert json.loads(result.arguments) == {"message": "Love the site", "subject": "Praise"}


def test_optional_subject_defaults_to_null() -> None:
    reply = json.dumps(
        {"tool_call": {"name": "send_feedback", "arguments": {"message": "A bug"}}}
    )

    result = parse_tool_call_reply(reply)

    assert result is not None
    assert json.loads(result.arguments) == {"message": "A bug", "subject": None}


def test_null_tool_call_routes_to_rag() -> None:
    # null tool_call is the "normal chat / RAG" signal — returns None, no raise.
    assert parse_tool_call_reply(json.dumps({"tool_call": None})) is None


def test_invalid_reply_raises_value_error() -> None:
    # Schema-violating / malformed JSON is a hard error, distinct from the None case.
    with pytest.raises(ValueError, match="invalid routing reply"):
        parse_tool_call_reply("not json at all")
