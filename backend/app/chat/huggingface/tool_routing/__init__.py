"""Non-stream chat completion to route ``send_feedback`` intent; optional JSON fallback."""

from __future__ import annotations

from .parse import parse_tool_calls_from_completion, parse_tool_calls_from_json_text
from .route import route_send_feedback_call, route_tool_calls
from .routing_messages import build_feedback_routing_messages
from .types import ParsedToolCall

__all__ = [
    "ParsedToolCall",
    "build_feedback_routing_messages",
    "parse_tool_calls_from_completion",
    "parse_tool_calls_from_json_text",
    "route_send_feedback_call",
    "route_tool_calls",
]
