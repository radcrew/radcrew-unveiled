"""Supervisor graph nodes: feedback intent routing, Web3Forms handler, RAG answer stream."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Literal

from app.chatbot.feedback.tool_branch import (
    classify_feedback_route,
    stream_feedback_tool_response,
)
from app.chatbot.graph.state import ChatState
from app.chatbot.rag.stream import stream_rag_chat_answer


def feedback_router_node(state: ChatState) -> dict[str, object]:
    """Classify user message as feedback tool vs general chat (RAG)."""
    body = state["body"]
    message = body.message
    history = body.history or []
    call = classify_feedback_route(message, history)

    if call is not None:
        return {"route": "feedback", "feedback_call": call}

    return {"route": "rag"}


def route_feedback_or_rag(state: ChatState) -> Literal["feedback", "rag"]:
    return state["route"]


def feedback_handler_node(state: ChatState) -> dict[str, Iterator[str]]:
    call = state["feedback_call"]
    return {"output_stream": stream_feedback_tool_response(call)}


def rag_answer_node(state: ChatState) -> dict[str, Iterator[str]]:
    return {
        "output_stream": stream_rag_chat_answer(
            state["body"],
            state["knowledge_chunks"],
        ),
    }
