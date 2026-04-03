from __future__ import annotations

from app.chat.huggingface.generate import generate_answer
from app.chat.huggingface.tool_routing import (
    COMPANY_ADVICE_TOOLS,
    ParsedToolCall,
    parse_tool_calls_from_completion,
    parse_tool_calls_from_json_text,
    route_tool_calls,
)

__all__ = [
    "COMPANY_ADVICE_TOOLS",
    "ParsedToolCall",
    "generate_answer",
    "parse_tool_calls_from_completion",
    "parse_tool_calls_from_json_text",
    "route_tool_calls",
]
