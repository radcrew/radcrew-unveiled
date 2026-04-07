"""Prompt copy and OpenAPI-style tool schema for feedback routing."""

from __future__ import annotations

from typing import Any

# Prepended to the routing completion so the model defaults to *no* tool call; without this,
# a single exposed tool is often invoked on every turn (especially with user-only transcripts).
TOOL_ROUTING_SYSTEM_MESSAGE = (
    "You are an intent router for a chat assistant. One optional tool exists: "
    "send_feedback. Your default is to call NO tools. "
    "Call send_feedback only when the user's latest message clearly means they want to "
    "submit feedback, suggestions, or a bug report to the company—e.g. they explicitly ask to "
    "send feedback, email the team with feedback, or share product feedback meant for staff. "
    "Do not call it for greetings, general questions, small talk, or normal FAQ-style questions."
)

# OpenAPI-style function tool exposed to the router (only ``send_feedback`` in this app).
_SEND_FEEDBACK_TOOL: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "send_feedback",
            "description": (
                "Submit structured feedback to the team on behalf of the user. "
                "Call ONLY when they clearly intend to send feedback—not for ordinary questions "
                "or conversation."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "The feedback body to deliver.",
                    },
                    "subject": {
                        "type": "string",
                        "description": "Optional short subject line for the feedback.",
                    },
                },
                "required": ["message"],
            },
        },
    }
]

_JSON_FALLBACK_SUFFIX = (
    "Based on the conversation and the routing rules in the system message, decide whether "
    "the user's latest message clearly intends to submit feedback via send_feedback. "
    'Reply with ONLY a single JSON object (no markdown fences) of the form: '
    '{"tool_calls":[]} when no tool call is appropriate (this should be the usual case), or '
    '{"tool_calls":[{"name":"send_feedback","arguments":{"message":"<text>",'
    '"subject":"<optional>"}}]} only when they clearly want to send feedback to the company.'
)
