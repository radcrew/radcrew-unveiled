"""LLM tool routing for user feedback + Web3Forms submission (runs before RAG when HF key is set)."""

from __future__ import annotations

import json
import logging
from collections.abc import Iterator
from typing import Any

from app.config import get_settings
from app.chat.utils import get_text_chunk_stream
from app.chat.feedback.web3forms import FeedbackError, submit_feedback_via_web3forms
from app.chat.huggingface.tool_routing import (
    build_feedback_routing_messages,
    route_send_feedback_call,
)
from app.chat.huggingface.tool_routing.types import ParsedToolCall
from app.chat.messages import MSG_FEEDBACK_SEND_FAILED, MSG_FEEDBACK_THANKS
from app.schemas import ChatHistoryMessage

logger = logging.getLogger(__name__)


def classify_feedback_route(
    message: str,
    history: list[ChatHistoryMessage],
) -> ParsedToolCall | None:
    """
    Run feedback-intent routing; return a ``send_feedback`` tool call only when
    the model routed to feedback and arguments contain a usable ``message`` string.
    Otherwise ``None`` so the RAG path should run.
    """
    settings = get_settings()
    if not settings.HUGGINGFACE_API_KEY:
        return None

    try:
        routing_msgs = build_feedback_routing_messages(message, history)
        feedback_call = route_send_feedback_call(routing_msgs)
    except Exception as exc:
        logger.exception("[chat] tool routing failed: %s", exc)
        return None

    if feedback_call is None:
        return None

    args: dict[str, Any] | None = None
    try:
        parsed = json.loads(feedback_call.arguments)
        args = parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        logger.warning("[chat] could not parse send_feedback arguments as JSON")

    if args is None or not isinstance(args.get("message"), str):
        return None

    return feedback_call


def stream_feedback_tool_response(feedback_call: ParsedToolCall) -> Iterator[str]:
    """Submit validated ``send_feedback`` args via Web3Forms and stream thanks or error text."""
    settings = get_settings()
    args: dict[str, Any] | None = None
    try:
        parsed = json.loads(feedback_call.arguments)
        args = parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        args = None

    if args is None or not isinstance(args.get("message"), str):
        return iter(())

    body_text = args["message"]
    raw_subj = args.get("subject")
    subject = raw_subj if isinstance(raw_subj, str) else None
    email = settings.COMPANY_FEEDBACK_EMAIL

    try:
        submit_feedback_via_web3forms(
            body_text,
            subject,
        )
    except FeedbackError as exc:
        logger.warning("Feedback submission failed: %s", exc)
        return get_text_chunk_stream(MSG_FEEDBACK_SEND_FAILED.format(email=email))

    return get_text_chunk_stream(MSG_FEEDBACK_THANKS.format(email=email))
