"""Orchestrate provider retries for feedback intent routing."""

from __future__ import annotations

import logging
from typing import Any

from app.config import get_settings
from app.chat.huggingface.common import providers_to_try

from .completion import feedback_route_completion, feedback_route_messages
from .parse import extract_message_content, parse_tool_calls_from_route_reply
from .types import ParsedToolCall

logger = logging.getLogger(__name__)


def route_tool_calls(messages: list[dict[str, Any]]) -> list[ParsedToolCall]:
    """
    Run non-stream ``chat_completion`` for routing: append the structured-reply instruction,
    then per provider try ``response_format: json_object`` and a plain completion. Parse
    ``{"tool_calls": [...]}`` from the assistant message content.
    """
    settings = get_settings()
    model = settings.HUGGINGFACE_MODEL
    access_token = settings.HUGGINGFACE_API_KEY
    providers = providers_to_try(settings.HUGGINGFACE_PROVIDER)

    messages_for_route = feedback_route_messages(messages)
    for provider in providers:
        for use_json_object_format in (True, False):
            try:
                resp = feedback_route_completion(
                    model,
                    access_token,
                    messages_for_route,
                    provider,
                    use_json_object_format,
                )
                content = extract_message_content(resp)
                parsed = parse_tool_calls_from_route_reply(content)
                if parsed is not None:
                    return parsed
            except Exception as err:
                logger.error(
                    "[HF feedback routing provider=%s json_object_format=%s] %s",
                    provider,
                    use_json_object_format,
                    err,
                )

    return []


def route_send_feedback_call(messages: list[dict[str, Any]]) -> ParsedToolCall | None:
    return next(
        (call for call in route_tool_calls(messages) if call.name == "send_feedback"),
        None,
    )
