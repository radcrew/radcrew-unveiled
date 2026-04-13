from typing import Any

from app.schemas import ChatHistoryMessage

TOOL_ROUTING_SYSTEM_MESSAGE = (
    "You route chat intents. Default: no tool. Use send_feedback only when the user clearly "
    "wants to submit feedback, a bug report, or a message to the company—not for greetings, "
    "FAQ, or follow-ups about your previous answer."
    "Reply with ONLY one JSON object (no markdown fences): "
    '{"tool_call": null} (default), or '
    '{"tool_call":{"name":"send_feedback","arguments":{"message":"<text>","subject":"<optional>"}}}. '
    'Include the key "tool_call" exactly once.'
)

_FEEDBACK_ROUTE_REPLY_SUFFIX = (
)

def build_feedback_routing_messages(
    message: str,
    history: list[ChatHistoryMessage],
) -> list[dict[str, Any]]:
    msgs = [{"role": "system", "content": TOOL_ROUTING_SYSTEM_MESSAGE}]

    for m in history:
        msgs.append({"role": m.role, "content": m.content})
    msgs.append({"role": "user", "content": message})

    return msgs