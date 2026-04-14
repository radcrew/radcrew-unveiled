import json

from typing import Any, Literal
from pydantic import BaseModel, Field
class SendFeedbackArguments(BaseModel):
    message: str = Field(None)
    subject: str | None = Field(None)

class SendFeedbackToolCall(BaseModel):
    name: Literal["send_feedback"] = "send_feedback"
    arguments: SendFeedbackArguments = Field(None)

class FeedbackRoutingReply(BaseModel):
    tool_call: SendFeedbackToolCall = Field(None)


_ROUTING_INSTRUCTIONS = (
    "You route chat intents. Default: no tool. Use send_feedback only when the user clearly "
    "wants to submit feedback, a bug report, or a message to the company—not for greetings, "
    "FAQ, or follow-ups about your previous answer.\n\n"
    "Reply with ONLY one JSON object (no markdown fences) that conforms to this JSON Schema:\n"
)

TOOL_ROUTING_SYSTEM_MESSAGE = (
    _ROUTING_INSTRUCTIONS + json.dumps(FeedbackRoutingReply.model_json_schema(), indent=2)
)


def build_feedback_routing_messages(message: str) -> list[dict[str, Any]]:
    msgs = [{"role": "system", "content": TOOL_ROUTING_SYSTEM_MESSAGE}]
    msgs.append({"role": "user", "content": message})
    return msgs
