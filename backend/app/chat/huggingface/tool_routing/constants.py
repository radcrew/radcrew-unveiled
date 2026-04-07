"""Prompt copy for JSON-based ``send_feedback`` intent routing."""

from __future__ import annotations

# Router system prompt: model must follow JSON shape described in ``_JSON_FALLBACK_SUFFIX``.
TOOL_ROUTING_SYSTEM_MESSAGE = (
    "You are an intent router for a chat assistant. One optional action exists: "
    "send_feedback. Your default is to indicate NO feedback submission is needed. "
    "Use send_feedback only when the user's latest message clearly means they want to "
    "submit feedback, suggestions, or a bug report to the company—e.g. they explicitly ask to "
    "send feedback, email the team with feedback, or share product feedback meant for staff. "
    "Do not use it for greetings, general questions, small talk, or normal FAQ-style questions."
)

_JSON_FALLBACK_SUFFIX = (
    "Based on the conversation and the routing rules in the system message, decide whether "
    "the user's latest message clearly intends to submit feedback via send_feedback. "
    'Reply with ONLY a single JSON object (no markdown fences) of the form: '
    '{"tool_calls":[]} when no tool call is appropriate (this should be the usual case), or '
    '{"tool_calls":[{"name":"send_feedback","arguments":{"message":"<text>",'
    '"subject":"<optional>"}}]} only when they clearly want to send feedback to the company.'
)
