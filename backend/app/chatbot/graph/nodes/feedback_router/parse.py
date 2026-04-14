from dataclasses import dataclass
from pydantic import ValidationError
import logging

from app.chatbot.graph.nodes.feedback_router.message import FeedbackRoutingReply

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class ParsedToolCall:
    id: str
    name: str
    arguments: str

def parse_tool_call_reply(text: str) -> ParsedToolCall | None:
    try:
        reply = FeedbackRoutingReply.model_validate_json(text)
    except ValidationError:
        logger.warning("[feedback routing] model reply does not match routing schema")
        raise ValueError("invalid routing reply") from None

    tool_call = reply.tool_call
    if tool_call is None:
        return None

    return ParsedToolCall(
        id="route-reply",
        name=tool_call.name,
        arguments=tool_call.arguments.model_dump_json(),
    )
