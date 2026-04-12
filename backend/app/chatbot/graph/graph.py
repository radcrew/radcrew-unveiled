"""LangGraph for /chat: classify intent, then feedback submission or RAG answer stream."""

from __future__ import annotations

from collections.abc import Iterator

from langgraph.graph import END, START, StateGraph

from app.chatbot.graph.nodes import (
    feedback_handler_node,
    feedback_router_node,
    rag_answer_node,
    route_feedback_or_rag,
)
from app.chatbot.graph.state import ChatState
from app.chatbot.knowledge.models import KnowledgeChunk
from app.schemas import ChatRequest


def build_chat_graph() -> StateGraph:
    builder = StateGraph(ChatState)

    builder.add_node("classify", feedback_router_node)
    builder.add_node("feedback", feedback_handler_node)
    builder.add_node("rag", rag_answer_node)

    builder.add_edge(START, "classify")
    builder.add_conditional_edges(
        "classify",
        route_feedback_or_rag,
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
