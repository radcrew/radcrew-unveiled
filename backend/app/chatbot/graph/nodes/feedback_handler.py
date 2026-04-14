import json
import logging

from collections.abc import Iterator

from app.core.settings import get_settings
from app.chatbot.utils import get_text_chunk_stream
from app.chatbot.graph.state import ChatState
from app.chatbot.feedback.web3forms import FeedbackError, submit_feedback_via_web3forms
from app.chatbot.messages import MSG_FEEDBACK_SEND_FAILED, MSG_FEEDBACK_THANKS

logger = logging.getLogger(__name__)

def feedback_handler_node(state: ChatState) -> dict[str, Iterator[str]]:
    settings = get_settings()
    email = settings.COMPANY_FEEDBACK_EMAIL
    
    feedback_call = state["feedback_call"]
    args = json.loads(feedback_call.arguments)

    try:
        submit_feedback_via_web3forms(args["message"], args["subject"])
    except FeedbackError as exc:
        logger.warning("Feedback submission failed: %s", exc)
        return {"output_stream": get_text_chunk_stream(MSG_FEEDBACK_SEND_FAILED.format(email=email))}
    
    return {"output_stream": get_text_chunk_stream(MSG_FEEDBACK_THANKS.format(email=email))}