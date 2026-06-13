"""LangGraph node: run NeMo input rails before intent routing."""
from __future__ import annotations

import logging

from app.chatbot.graph.state import ChatState
from app.chatbot.guardrails import apply_input_rail
from app.chatbot.utils import get_text_chunk_stream

logger = logging.getLogger(__name__)


def guardrail_input_node(state: ChatState) -> dict[str, object]:
    """Gate the pipeline before routing.

    Blocked messages short-circuit directly to END via the
    'guardrail_blocked' route — the route and rag nodes are never reached.
    """
    message = state["body"].message
    result = apply_input_rail(message)

    if result.blocked:
        logger.info("[guardrail] input blocked message=%r", message[:120])
        return {
            "route": "guardrail_blocked",
            "output_stream": get_text_chunk_stream(result.response),
        }

    return {}
