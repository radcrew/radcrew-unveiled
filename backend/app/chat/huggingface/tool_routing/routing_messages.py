"""Build chat message lists for the feedback intent router."""

from __future__ import annotations

from typing import Any

from app.schemas import ChatHistoryMessage

from .constants import TOOL_ROUTING_SYSTEM_MESSAGE


def build_feedback_routing_messages(
    message: str,
    history: list[ChatHistoryMessage],
) -> list[dict[str, Any]]:
    
    msgs: list[dict[str, Any]] = [
        {"role": "system", "content": TOOL_ROUTING_SYSTEM_MESSAGE},
    ]
    for m in history:
        msgs.append({"role": m.role, "content": m.content})
    msgs.append({"role": "user", "content": message})
    
    return msgs
