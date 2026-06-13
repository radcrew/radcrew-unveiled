"""LangGraph node: handle the three feedback phases — ask, cancel, send.

Feedback is never sent on first detection. The router asks the user to confirm
("ask"); the next turn resolves to "send" (submit) or "cancel" (acknowledge,
send nothing). See the confirmation flow in feedback_router/confirm.py.
"""

from __future__ import annotations

import json
from collections.abc import Iterator

from app.chatbot.graph.state import ChatState
from app.chatbot.messages import (
    MSG_FEEDBACK_CANCELLED,
    MSG_FEEDBACK_CONFIRM,
    MSG_FEEDBACK_SEND_FAILED,
    MSG_FEEDBACK_THANKS,
)
from app.chatbot.utils import get_text_chunk_stream
from app.core.settings import get_settings

from .submit import submit_feedback


def _formatted_message_stream(template: str) -> Iterator[str]:
    """Stream a message template with the company feedback email filled in."""
    settings = get_settings()
    return get_text_chunk_stream(template.format(email=settings.COMPANY_FEEDBACK_EMAIL))


def feedback_handler_node(state: ChatState) -> dict[str, Iterator[str]]:
    phase = state.get("feedback_phase", "send")

    # Cancelled confirmation — acknowledge, send nothing.
    if phase == "cancel":
        return {"output_stream": get_text_chunk_stream(MSG_FEEDBACK_CANCELLED)}

    feedback_call = state["feedback_call"]
    args = json.loads(feedback_call.arguments)
    body = args["message"]
    subject = args.get("subject")

    # First contact — ask the user to confirm before sending.
    if phase == "ask":
        return {"output_stream": get_text_chunk_stream(MSG_FEEDBACK_CONFIRM.format(body=body))}

    try:
        submit_feedback(body, subject)
    except Exception:
        return {"output_stream": _formatted_message_stream(MSG_FEEDBACK_SEND_FAILED)}

    return {"output_stream": _formatted_message_stream(MSG_FEEDBACK_THANKS)}