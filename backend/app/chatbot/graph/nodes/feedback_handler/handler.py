import json

from collections.abc import Iterator

from app.core.settings import get_settings
from app.chatbot.utils import get_text_chunk_stream
from app.chatbot.graph.state import ChatState
from app.chatbot.messages import MSG_FEEDBACK_SEND_FAILED, MSG_FEEDBACK_THANKS
from .submit import submit_feedback

def get_message_stream(message: str) -> Iterator[str]:
    settings = get_settings()
    return get_text_chunk_stream(message.format(email=settings.COMPANY_FEEDBACK_EMAIL))

def feedback_handler_node(state: ChatState) -> dict[str, Iterator[str]]:
    feedback_call = state["feedback_call"]

    args = json.loads(feedback_call.arguments)
    body = args["message"]
    subject = args["subject"]

    try:
        submit_feedback(body, subject)
    except Exception:
        return {"output_stream": get_message_stream(MSG_FEEDBACK_SEND_FAILED)}
    
    return {"output_stream": get_message_stream(MSG_FEEDBACK_THANKS)}