"""Orchestrate provider retries and JSON fallback for feedback tool routing."""

from __future__ import annotations

import logging
from typing import Any

from app.config import get_settings
from app.chat.huggingface.common import providers_to_try

from .completion import (
    json_fallback_completion,
    json_fallback_messages,
    tool_router_completion,
)
from .parse import (
    extract_message_content,
    parse_tool_calls_from_completion,
    parse_tool_calls_from_json_text,
)
from .types import ParsedToolCall

logger = logging.getLogger(__name__)


def route_tool_calls(messages: list[dict[str, Any]]) -> list[ParsedToolCall]:
    """
    Run non-stream ``chat_completion`` with the ``send_feedback`` tool and
    ``tool_choice="auto"``, parse ``choices[0].message.tool_calls``, and return
    structured calls.

    If every provider fails that request (HTTP/validation errors), runs a
    JSON-only completion (with and without ``response_format: json_object``)
    and parses ``{"tool_calls": [...]}`` from the assistant message content.
    """
    settings = get_settings()
    model = settings.HUGGINGFACE_MODEL
    access_token = settings.HUGGINGFACE_API_KEY
    providers = providers_to_try(settings.HUGGINGFACE_PROVIDER)

    for provider in providers:
        try:
            resp = tool_router_completion(
                model,
                access_token,
                messages,
                provider,
            )
            return parse_tool_calls_from_completion(resp)
        except Exception as err:
            logger.error("[HF chatCompletionTools provider=%s] %s", provider, err)

    # JSON fallback: same providers; try json_object response format first, then plain.
    fallback_msgs = json_fallback_messages(messages)
    for provider in providers:
        for use_json_fmt in (True, False):
            try:
                resp = json_fallback_completion(
                    model,
                    access_token,
                    fallback_msgs,
                    provider,
                    use_json_object_format=use_json_fmt,
                )
                content = extract_message_content(resp)
                parsed = parse_tool_calls_from_json_text(content)
                if parsed is not None:
                    return parsed
            except Exception as err:
                logger.error(
                    "[HF chatCompletionJsonFallback provider=%s json_fmt=%s] %s",
                    provider,
                    use_json_fmt,
                    err,
                )

    return []


def route_send_feedback_call(messages: list[dict[str, Any]]) -> ParsedToolCall | None:
    return next(
        (call for call in route_tool_calls(messages) if call.name == "send_feedback"),
        None,
    )
