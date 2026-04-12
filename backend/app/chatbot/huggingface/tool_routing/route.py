"""Orchestrate provider retries for feedback intent routing."""

from __future__ import annotations

import logging
from typing import Any

from app.core.config import get_settings
from app.chatbot.huggingface.common import providers_to_try

from .completion import feedback_route_completion, feedback_route_messages
from .parse import (
    RouteReplyUnparseable,
    extract_message_content,
    parse_tool_call_from_route_reply,
)
from .types import ParsedToolCall

logger = logging.getLogger(__name__)


def route_send_feedback_call(messages: list[dict[str, Any]]) -> ParsedToolCall | None:
    """
    Run non-stream ``chat_completion`` for routing: append the structured-reply instruction,
    then per provider try ``response_format: json_object`` and a plain completion. Parse
    ``{"tool_call": null | {...}}`` from the assistant message.

    Returns ``ParsedToolCall`` only when the model emitted ``send_feedback``; ``None``
    when there is no feedback tool (including ``tool_call``: null, another tool name, or
    no usable reply after all attempts).
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

                try:
                    call = parse_tool_call_from_route_reply(content)
                except RouteReplyUnparseable:
                    continue

                if call is not None and call.name == "send_feedback":
                    return call
                return None
            except Exception as err:
                logger.error(
                    "[HF feedback routing provider=%s json_object_format=%s] %s",
                    provider,
                    use_json_object_format,
                    err,
                )

    return None
