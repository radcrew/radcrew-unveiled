"""LLM tool routing for user feedback + Web3Forms submission (runs before RAG when HF key is set)."""

from __future__ import annotations

import json
import logging
from collections.abc import Iterator
from typing import Any

from app.chat.cache.response import get_text_chunk_stream
from app.chat.feedback.web3forms import (
    FeedbackNotConfiguredError,
    FeedbackSubmissionError,
    FeedbackValidationError,
    submit_feedback_via_web3forms,
)
from app.chat.huggingface.tool_routing import (
    build_feedback_routing_messages,
    route_tool_calls,
)
from app.chat.messages import (
    MSG_FEEDBACK_NOT_CONFIGURED,
    MSG_FEEDBACK_SEND_FAILED,
    MSG_FEEDBACK_THANKS,
)
from app.config import Settings
from app.schemas import ChatHistoryMessage

logger = logging.getLogger(__name__)


def try_feedback_tool_call(
    settings: Settings,
    message: str,
    history: list[ChatHistoryMessage],
) -> Iterator[str] | None:
    """
    If the model returns ``send_feedback``, submit the user's message via Web3Forms and stream a reply.

    Returns ``None`` when the normal RAG path should run instead.
    """

    if not settings.HUGGINGFACE_API_KEY:
        return None;

    try:
        tool_msgs = build_feedback_routing_messages(message, history)
        routed = route_tool_calls(
            settings.HUGGINGFACE_MODEL,
            settings.HUGGINGFACE_API_KEY,
            tool_msgs,
            settings.HUGGINGFACE_PROVIDER,
        )
    except Exception as exc:
        logger.exception("[chat] tool routing failed: %s", exc)
        return None

    feedback_call = next((c for c in routed if c.name == "send_feedback"), None)
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

    body_text = args["message"]
    raw_subj = args.get("subject")
    subject = raw_subj if isinstance(raw_subj, str) else None
    email = settings.COMPANY_FEEDBACK_EMAIL

    try:
        submit_feedback_via_web3forms(
            body_text,
            subject,
            settings=settings,
        )
    except FeedbackNotConfiguredError:
        logger.warning(
            "Feedback submission unavailable: WEB3FORMS_ACCESS_KEY is not set."
        )
        return get_text_chunk_stream(MSG_FEEDBACK_NOT_CONFIGURED.format(email=email))
    except (FeedbackValidationError, FeedbackSubmissionError) as exc:
        logger.warning("Feedback submission failed: %s", exc)
        return get_text_chunk_stream(MSG_FEEDBACK_SEND_FAILED.format(email=email))

    return get_text_chunk_stream(MSG_FEEDBACK_THANKS.format(email=email))
