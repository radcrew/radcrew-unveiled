"""LangGraph for /chat: classify intent, then feedback submission or RAG answer stream."""

from __future__ import annotations

from typing import Literal

from langgraph.graph import END, START, StateGraph

from app.chatbot.graph.state import ChatState
from app.chatbot.graph.nodes.guardrail.input_node import guardrail_input_node
from app.chatbot.graph.nodes.feedback_router.router import feedback_router_node, route_feedback_or_rag
from app.chatbot.graph.nodes.feedback_handler.handler import feedback_handler_node
from app.chatbot.graph.nodes.rag_answer.answer import rag_answer_node


def _route_after_guardrail(
    state: ChatState,
) -> Literal["continue", "guardrail_blocked"]:
    if state.get("route") == "guardrail_blocked":
        return "guardrail_blocked"
    return "continue"


def build_chat_graph() -> StateGraph:
    builder = StateGraph(ChatState)

    builder.add_node("guardrail_input", guardrail_input_node)
    builder.add_node("route", feedback_router_node)
    builder.add_node("feedback", feedback_handler_node)
    builder.add_node("rag", rag_answer_node)

    builder.add_edge(START, "guardrail_input")
    builder.add_conditional_edges(
        "guardrail_input",
        _route_after_guardrail,
        {"continue": "route", "guardrail_blocked": END},
    )
    builder.add_conditional_edges(
        "route",
        route_feedback_or_rag,
        {"feedback": "feedback", "rag": "rag"},
    )
    builder.add_edge("feedback", END)
    builder.add_edge("rag", END)

    return builder


chat_graph = build_chat_graph().compile()
