"""LLM tool routing for user feedback + Web3Forms submission (runs before RAG when HF key is set)."""

from __future__ import annotations
import json
import logging
import re
from collections.abc import Iterator
from typing import Any
from app.config import get_settings
from app.chat.utils import get_text_chunk_stream
from app.chat.feedback.web3forms import FeedbackError, submit_feedback_via_web3forms
from app.chat.huggingface.tool_routing import (
    build_feedback_routing_messages,
    route_send_feedback_call,
)
from app.chat.messages import MSG_FEEDBACK_SEND_FAILED, MSG_FEEDBACK_THANKS
from app.schemas import ChatHistoryMessage

logger = logging.getLogger(__name__)

# If the user message clearly looks like Q&A continuation, skip the HF router unless explicit
# feedback-to-company wording is present (avoids misroutes like "and their skills?" -> send_feedback).
_FEEDBACK_SUBMISSION_HINT = re.compile(
    r"\b("
    r"feedback|bug(\s*report)?|file\s+a\s+bug|suggestion|suggestions|complaint|complaints|"
    r"feature\s*request|contact\s+(the\s+)?(team|company)|reach\s+out(\s+to)?|"
    r"send\s+(this|my|the\s+)?(message|note|feedback|report)|"
    r"email\s+(the\s+)?team|report(\s+(a|the|an))?\s+(bug|issue|problem)|"
    r"tell\s+the\s+team|submit\s+(a\s+)?(ticket|report)|"
    r"not\s+working|doesn'?t\s+work|is\s+broken|broken\s+(link|page|site|feature)|"
    r"to\s+the\s+team|to\s+the\s+company|for\s+the\s+team"
    r")\b",
    re.I,
)

_QNA_FOLLOWUP_PREFIX = re.compile(
    r"^\s*(and|also|what about|how about|tell me more(\s+about)?|more details?)\b",
    re.I,
)

# Follow-ups like "Is he the most experienced?" (subject pronouns; we already had "him" only).
_AUX_SUBJECT_QUESTION = re.compile(
    r"\b(is|are|was|were|do|does|did|has|have|can|could|would|will)\s+"
    r"(he|she|they|it|this|that)\b",
    re.I,
)


def should_attempt_feedback_routing(message: str) -> bool:
    """
    When False, skip the Hugging Face intent router and use normal chat (RAG).

    Order matters: explicit feedback wording always allows routing; otherwise obvious
    Q&A follow-ups are excluded.
    """
    text = message.strip()
    if not text:
        return True

    if _FEEDBACK_SUBMISSION_HINT.search(text):
        return True

    if _QNA_FOLLOWUP_PREFIX.match(text):
        return False

    if text.endswith("?"):
        if _AUX_SUBJECT_QUESTION.search(text):
            return False
        if len(text) <= 240 and len(text.split()) <= 22:
            if re.search(
                r"\b("
                r"he|she|they|it|their|his|her|them|those|these|him|"
                r"the\s+team|the\s+developers?|both|each|"
                r"those\s+people|these\s+people"
                r")\b",
                text,
                re.I,
            ):
                return False
    return True


def try_feedback_tool_call(
    message: str,
    history: list[ChatHistoryMessage],
) -> Iterator[str] | None:
    """
    If the model returns ``send_feedback``, submit the user's message via Web3Forms and stream a reply.
    Returns ``None`` when the normal RAG path should run instead.
    """
    settings = get_settings()
    if not settings.HUGGINGFACE_API_KEY:
        return None

    if not should_attempt_feedback_routing(message):
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
