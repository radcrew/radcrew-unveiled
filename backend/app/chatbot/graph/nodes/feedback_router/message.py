from typing import Any

TOOL_ROUTING_SYSTEM_MESSAGE = (
    "You route chat intents. Default: no tool. Use send_feedback only when the user clearly "
    "wants to submit feedback, a bug report, or a message to the company—not for greetings, "
    "FAQ, or follow-ups about your previous answer."
    "Reply with ONLY one JSON object (no markdown fences): "
    '{"tool_call": null} (default), or '
    '{"tool_call":{"name":"send_feedback","arguments":{"message":"<text>","subject":"<optional>"}}}. '
    'Include the key "tool_call" exactly once.'
)

def build_feedback_routing_messages(message: str) -> list[dict[str, Any]]:
    msgs = [{"role": "system", "content": TOOL_ROUTING_SYSTEM_MESSAGE}]
    msgs.append({"role": "user", "content": message})
    return msgs