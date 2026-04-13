"""LangGraph for /chat: classify intent, then feedback submission or RAG answer stream."""

from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from app.chatbot.graph.nodes import (
    feedback_handler_node,
    feedback_router_node,
    rag_answer_node,
    route_feedback_or_rag,
)
from app.chatbot.graph.state import ChatState


def build_chat_graph() -> StateGraph:
    builder = StateGraph(ChatState)

    builder.add_node("route", feedback_router_node)
    builder.add_node("feedback", feedback_handler_node)
    builder.add_node("rag", rag_answer_node)

    builder.add_edge(START, "route")
    builder.add_conditional_edges(
        "route",
        route_feedback_or_rag,
        {"feedback": "feedback", "rag": "rag"},
    )
    builder.add_edge("feedback", END)
    builder.add_edge("rag", END)

    return builder


chat_graph = build_chat_graph().compile()
