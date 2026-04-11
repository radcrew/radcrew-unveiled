"""LangGraph for /chat: classify intent, then feedback submission or RAG answer stream."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Literal

from langgraph.graph import END, START, StateGraph

from app.chat.feedback.tool_branch import (
    classify_feedback_route,
    stream_feedback_tool_response,
)
from app.chat.graph.state import ChatState
from app.chat.rag.stream import stream_rag_chat_answer
from app.knowledge.models import KnowledgeChunk
from app.schemas import ChatRequest


def _classify_node(state: ChatState) -> dict[str, object]:
    body = state["body"]
    message = body.message
    history = body.history or []
    call = classify_feedback_route(message, history)
    if call is not None:
        return {"route": "feedback", "feedback_call": call}
    return {"route": "rag"}


def _route_after_classify(state: ChatState) -> Literal["feedback", "rag"]:
    r = state.get("route")
    if r == "feedback":
        return "feedback"
    return "rag"


def _feedback_node(state: ChatState) -> dict[str, Iterator[str]]:
    call = state["feedback_call"]
    return {"output_stream": stream_feedback_tool_response(call)}


def _rag_node(state: ChatState) -> dict[str, Iterator[str]]:
    return {
        "output_stream": stream_rag_chat_answer(
            state["body"],
            state["knowledge_chunks"],
        )
    }


def build_chat_graph() -> StateGraph:
    builder = StateGraph(ChatState)
    builder.add_node("classify", _classify_node)
    builder.add_node("feedback", _feedback_node)
    builder.add_node("rag", _rag_node)
    builder.add_edge(START, "classify")
    builder.add_conditional_edges(
        "classify",
        _route_after_classify,
        {"feedback": "feedback", "rag": "rag"},
    )
    builder.add_edge("feedback", END)
    builder.add_edge("rag", END)
    return builder


_compiled_routing_graph = build_chat_graph().compile()


def run_chat_stream(
    body: ChatRequest,
    knowledge_chunks: list[KnowledgeChunk],
) -> Iterator[str]:

    result = _compiled_routing_graph.invoke(
        {
            "body": body,
            "knowledge_chunks": knowledge_chunks,
        }
    )

    return result["output_stream"]
