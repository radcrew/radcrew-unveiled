from collections.abc import Iterator
from app.chatbot.graph.state import ChatState

from app.chatbot.feedback.tool_branch import stream_feedback_tool_response

def feedback_handler_node(state: ChatState) -> dict[str, Iterator[str]]:
    call = state["feedback_call"]
    return {"output_stream": stream_feedback_tool_response(call)}