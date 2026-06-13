"""Parse the routing classifier's JSON reply into an intent label."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Literal

from pydantic import ValidationError

from app.chatbot.graph.nodes.feedback_router.message import RoutingReply

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ParsedToolCall:
    id: str
    name: str
    arguments: str


def parse_routing_intent(text: str | None) -> Literal["question", "feedback"]:
    """Intent from the classifier reply; any malformed reply defaults to question (→ RAG)."""
    if not text:
        return "question"
    try:
        reply = RoutingReply.model_validate_json(text)
    except ValidationError:
        logger.warning("[feedback routing] model reply does not match routing schema")
        return "question"
    return reply.intent
