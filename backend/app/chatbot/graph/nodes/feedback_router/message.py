import json

from typing import Any, Literal
from pydantic import BaseModel, Field

class SendFeedbackArguments(BaseModel):
    message: str = Field(..., description="User feedback body.")
    subject: str | None = Field(None, description="Optional short subject line.")

class SendFeedbackToolCall(BaseModel):
    name: Literal["send_feedback"] = "send_feedback"
    arguments: SendFeedbackArguments

class FeedbackRoutingReply(BaseModel):
    tool_call: SendFeedbackToolCall | None = Field(
        None,
        description='null = normal chat/RAG; object = call send_feedback with arguments.',
    )


_ROUTING_INSTRUCTIONS = (
    "You route chat intents for a company website chatbot. Default: no tool.\n"
    "Use send_feedback ONLY when the user clearly wants to submit feedback, a bug report, "
    "a complaint, or a direct message to the company.\n"
    "Do NOT use send_feedback for: greetings, questions about the company or team, "
    "FAQ queries, or follow-ups about a previous answer.\n"
    "Use the conversation history to understand context — the user may express intent "
    "across multiple turns.\n\n"
    "Reply with ONLY one JSON object (no markdown fences) matching this schema:\n"
)

_FEW_SHOT_EXAMPLES = (
    "\n\nExamples:\n"
    'User: "I want to report a bug on the contact page"\n'
    '→ {"tool_call": {"name": "send_feedback", "arguments": {"message": "I want to report a bug on the contact page", "subject": "Bug report"}}}\n\n'
    'User: "What services does RadCrew offer?"\n'
    '→ {"tool_call": null}\n\n'
    'User: "The mobile layout is broken on my iPhone"\n'
    '→ {"tool_call": {"name": "send_feedback", "arguments": {"message": "The mobile layout is broken on my iPhone", "subject": "Mobile layout issue"}}}\n\n'
    'User: "Who are the team members?"\n'
    '→ {"tool_call": null}\n\n'
    'User: "Great website!" (after normal conversation)\n'
    '→ {"tool_call": null}\n'
)

TOOL_ROUTING_SYSTEM_MESSAGE = (
    _ROUTING_INSTRUCTIONS
    + json.dumps(FeedbackRoutingReply.model_json_schema(), indent=2)
    + _FEW_SHOT_EXAMPLES
)

_MAX_ROUTING_HISTORY = 4


def build_feedback_routing_messages(
    message: str,
    history: list[dict[str, str]] | None = None,
) -> list[dict[str, Any]]:
    msgs = [{"role": "system", "content": TOOL_ROUTING_SYSTEM_MESSAGE}]
    for h in (history or [])[-_MAX_ROUTING_HISTORY:]:
        msgs.append({"role": h["role"], "content": h["content"]})
    msgs.append({"role": "user", "content": message})
    return msgs
