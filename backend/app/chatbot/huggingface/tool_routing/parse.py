"""Parse a single ``tool_call`` object from the model routing reply."""

from __future__ import annotations

import logging
from typing import Any

from pydantic import ValidationError

from app.chatbot.huggingface.common import safe_get
from app.chatbot.graph.nodes.feedback_router.message import FeedbackRoutingReply
from .types import ParsedToolCall

logger = logging.getLogger(__name__)


class RouteReplyUnparseable(ValueError):
    """Reply is not a valid routing JSON envelope; caller may retry another completion."""


def extract_message_content(resp: Any) -> str:
    ch = safe_get(resp, "choices")
    if not isinstance(ch, list) or not ch:
        return ""

    msg = safe_get(ch[0], "message")
    if msg is None:
        return ""

    content = safe_get(msg, "content")
    return content if isinstance(content, str) else ""


def _strip_json_fences(text: str) -> str:
    t = text.strip()
    if not t.startswith("```"):
        return t

    lines = t.splitlines()[1:]
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]

    return "\n".join(lines).strip()


def parse_tool_call_reply(text: str) -> ParsedToolCall | None:
    """
    Parse ``{"tool_call": null | {...}}`` from the assistant message (routing completion).

    Returns ``None`` when ``tool_call`` is null or there is no actionable call.
    Returns ``ParsedToolCall`` when ``tool_call`` is an object with ``name`` and ``arguments``.

    Raises ``RouteReplyUnparseable`` when the text is not a usable routing envelope
    (bad JSON, missing ``tool_call`` key, wrong types, etc.).
    """
    raw = _strip_json_fences(text)
    if not raw:
        raise RouteReplyUnparseable("empty reply")

    try:
        reply = FeedbackRoutingReply.model_validate_json(raw)
    except ValidationError:
        logger.warning("[feedback routing] model reply does not match routing schema")
        raise RouteReplyUnparseable("invalid routing reply") from None

    tc = reply.tool_call
    if tc is None:
        return None

    return ParsedToolCall(
        id="route-reply",
        name=tc.name,
        arguments=tc.arguments.model_dump_json(),
    )
