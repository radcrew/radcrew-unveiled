"""LangGraph for /chat: classify intent, then feedback submission or RAG answer stream."""

from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from app.chatbot.graph.state import ChatState
from app.chatbot.graph.nodes.feedback_router.router import feedback_router_node, route_feedback_or_rag
from app.chatbot.graph.nodes.feedback_handler import feedback_handler_node
from app.chatbot.graph.nodes.rag_answer import rag_answer_node

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
