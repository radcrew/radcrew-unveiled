"""Parse native tool calls or JSON fallback text into ``ParsedToolCall`` rows."""

from __future__ import annotations

import json
import logging
from typing import Any

from app.chat.huggingface.common import safe_get

from .types import ParsedToolCall

logger = logging.getLogger(__name__)


def _choices(resp: Any) -> list[Any]:
    ch = safe_get(resp, "choices")
    return ch if isinstance(ch, list) else []


def _first_message(resp: Any) -> Any:
    ch = _choices(resp)
    if not ch:
        return None
    return safe_get(ch[0], "message")


def parse_tool_calls_from_completion(resp: Any) -> list[ParsedToolCall]:
    """Parse ``choices[0].message.tool_calls`` from a chat completion response."""
    msg = _first_message(resp)
    if msg is None:
        return []
    raw_calls = safe_get(msg, "tool_calls")
    if not raw_calls:
        return []
    out: list[ParsedToolCall] = []
    for tc in raw_calls:
        tc_id = safe_get(tc, "id")
        fn = safe_get(tc, "function")
        name = safe_get(fn, "name") if fn is not None else None
        args = safe_get(fn, "arguments") if fn is not None else None
        if isinstance(args, str):
            arg_str = args
        elif args is None:
            arg_str = "{}"
        else:
            arg_str = json.dumps(args)
        out.append(
            ParsedToolCall(
                id=str(tc_id) if tc_id is not None else "",
                name=str(name) if name is not None else "",
                arguments=arg_str,
            )
        )
    return out


def extract_message_content(resp: Any) -> str:
    msg = _first_message(resp)
    if msg is None:
        return ""
    content = safe_get(msg, "content")
    return content if isinstance(content, str) else ""


def _strip_json_fences(text: str) -> str:
    t = text.strip()
    if not t.startswith("```"):
        return t
    lines = t.split("\n")
    if lines and lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]
    return "\n".join(lines).strip()


def parse_tool_calls_from_json_text(text: str) -> list[ParsedToolCall] | None:
    """
    Parse fallback JSON ``{"tool_calls": [...]}`` from model text.

    Returns ``None`` if the payload is not valid JSON with a ``tool_calls`` array.
    Returns an empty list when ``tool_calls`` is valid but empty.
    """
    raw = _strip_json_fences(text)
    if not raw:
        return None
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        logger.warning("[tool routing] JSON fallback could not parse model output")
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
                id=f"json-fallback-{i}",
                name=name.strip(),
                arguments=arg_str,
            )
        )
    return out
