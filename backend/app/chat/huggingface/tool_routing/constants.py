"""Prompt copy for JSON-based ``send_feedback`` intent routing."""

from __future__ import annotations

# Router system prompt; the final user turn uses ``_FEEDBACK_ROUTE_REPLY_SUFFIX``.
TOOL_ROUTING_SYSTEM_MESSAGE = (
    "You route chat intents. Default: no tool. Use send_feedback only when the user clearly "
    "wants to submit feedback, a bug report, or a message to the company—not for greetings, "
    "FAQ, or follow-ups about your previous answer."
)

_FEEDBACK_ROUTE_REPLY_SUFFIX = (
    "Reply with ONLY one JSON object (no markdown fences): "
    '{"tool_call": null} (default), or '
    '{"tool_call":{"name":"send_feedback","arguments":{"message":"<text>","subject":"<optional>"}}}. '
    'Include the key "tool_call" exactly once.'
)
