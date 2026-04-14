"""LLM tool routing for user feedback + Web3Forms submission (runs before RAG when HF key is set)."""

from __future__ import annotations

import json
import logging
from collections.abc import Iterator
from typing import Any

from app.core.settings import get_settings
from app.chatbot.utils import get_text_chunk_stream
from app.chatbot.feedback.web3forms import FeedbackError, submit_feedback_via_web3forms

from app.chatbot.graph.nodes.feedback_router.parse import ParsedToolCall
from app.chatbot.messages import MSG_FEEDBACK_SEND_FAILED, MSG_FEEDBACK_THANKS

logger = logging.getLogger(__name__)


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
