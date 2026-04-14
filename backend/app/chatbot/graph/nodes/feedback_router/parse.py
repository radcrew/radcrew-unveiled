from dataclasses import dataclass
from pydantic import ValidationError
import logging
from typing import Any

from app.chatbot.huggingface.common import safe_get
from app.chatbot.graph.nodes.feedback_router.message import FeedbackRoutingReply

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ParsedToolCall:
    id: str
    name: str
    arguments: str

class RouteReplyUnparseable(ValueError):
    """Reply is not a valid routing JSON envelope; caller may retry another completion."""

def _strip_json_fences(text: str) -> str:
    t = text.strip()
    if not t.startswith("```"):
        return t

    lines = t.splitlines()[1:]
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]

    return "\n".join(lines).strip()

def parse_tool_call_reply(text: str) -> ParsedToolCall | None:
    raw = _strip_json_fences(text)
    if not raw:
        raise RouteReplyUnparseable("empty reply")

    try:
        reply = FeedbackRoutingReply.model_validate_json(raw)
    except ValidationError:
        logger.warning("[feedback routing] model reply does not match routing schema")
        raise RouteReplyUnparseable("invalid routing reply") from None

    tc = reply.tool_call
    if tc is None:
        return None

    return ParsedToolCall(
        id="route-reply",
        name=tc.name,
        arguments=tc.arguments.model_dump_json(),
    )
