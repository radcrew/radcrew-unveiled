from typing import Literal

from app.chatbot.graph.state import ChatState
from app.chatbot.huggingface.tool_routing import route_send_feedback_call
from .message import build_feedback_routing_messages

def route_feedback_or_rag(state: ChatState) -> Literal["feedback", "rag"]:
    return state["route"]


def feedback_router_node(state: ChatState) -> dict[str, object]:
    body = state["body"]
    
    routing_msgs = build_feedback_routing_messages(body.message)
    feedback_call = route_send_feedback_call(routing_msgs)

    if feedback_call is not None:
        return {"route": "feedback", "feedback_call": feedback_call}

    return {"route": "rag"}
