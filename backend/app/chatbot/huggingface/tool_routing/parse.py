"""Parse a single ``tool_call`` object from the model routing reply."""

from __future__ import annotations

import json
import logging
from typing import Any

from app.chatbot.huggingface.common import safe_get

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


def _arguments_json(arguments: object) -> str | None:
    if isinstance(arguments, dict):
        return json.dumps(arguments)

    if isinstance(arguments, str):
        return arguments

    if arguments is None:
        return "{}"

    return None


def parse_tool_call_from_route_reply(text: str) -> ParsedToolCall | None:
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
        data = json.loads(raw)
    except json.JSONDecodeError:
        logger.warning("[feedback routing] could not parse model reply as JSON")
        raise RouteReplyUnparseable("invalid json") from None

    if not isinstance(data, dict):
        raise RouteReplyUnparseable("not a json object")

    if "tool_call" not in data:
        raise RouteReplyUnparseable("missing tool_call key")

    tc = data.get("tool_call")
    if tc is None:
        return None
    if not isinstance(tc, dict):
        raise RouteReplyUnparseable("tool_call must be object or null")

    name = tc.get("name")
    if not isinstance(name, str) or not name.strip():
        return None

    arg_str = _arguments_json(tc.get("arguments"))
    if arg_str is None:
        return None

    return ParsedToolCall(
        id="route-reply",
        name=name.strip(),
        arguments=arg_str,
    )
