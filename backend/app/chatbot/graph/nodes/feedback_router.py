from typing import Literal

from app.chatbot.graph.state import ChatState
from app.chatbot.feedback.tool_branch import classify_feedback_route


def route_feedback_or_rag(state: ChatState) -> Literal["feedback", "rag"]:
    return state["route"]


def feedback_router_node(state: ChatState) -> dict[str, object]:
    """Classify user message as feedback tool vs general chat (RAG)."""
    body = state["body"]
    message = body.message
    history = body.history or []
    call = classify_feedback_route(message, history)

    if call is not None:
        return {"route": "feedback", "feedback_call": call}

    return {"route": "rag"}
