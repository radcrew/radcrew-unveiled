"""Parse JSON ``tool_calls`` payloads from model message content."""

from __future__ import annotations

import json
import logging
from typing import Any

from app.chat.huggingface.common import safe_get

from .types import ParsedToolCall

logger = logging.getLogger(__name__)


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


def parse_tool_calls_from_route_reply(text: str) -> list[ParsedToolCall] | None:
    """
    Parse ``{"tool_calls": [...]}`` from the assistant message (routing completion).

    Returns ``None`` if the payload is not valid JSON with a ``tool_calls`` array.
    Returns an empty list when ``tool_calls`` is valid but empty.
    """
    raw = _strip_json_fences(text)
    if not raw:
        return None
    
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        logger.warning("[feedback routing] could not parse model reply as JSON")
        return None
    
    if not isinstance(data, dict):
        return None
    
    calls = data.get("tool_calls")
    if not isinstance(calls, list):
        return None
    
    out: list[ParsedToolCall] = []
    for i, item in enumerate(calls):
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        if not isinstance(name, str) or not name.strip():
            continue
        args = item.get("arguments")
        if isinstance(args, dict):
            arg_str = json.dumps(args)
        elif isinstance(args, str):
            arg_str = args
        else:
            arg_str = "{}"
        out.append(
            ParsedToolCall(
                id=f"route-reply-{i}",
                name=name.strip(),
                arguments=arg_str,
            )
        )
    return out
