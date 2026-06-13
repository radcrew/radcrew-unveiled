"""Routing-classifier schema, instructions, and few-shot message builder."""

from __future__ import annotations

import json
from typing import Any, Literal

from pydantic import BaseModel, Field


class RoutingReply(BaseModel):
    """Flat intent label — easier for a small model than a nullable object."""

    intent: Literal["question", "feedback"] = Field(
        "question",
        description=(
            'Use "feedback" only when the user explicitly wants to send a message, '
            'bug report, complaint, or suggestion to the RadCrew team. Otherwise "question".'
        ),
    )


_ROUTING_INSTRUCTIONS = (
    "You label one chat message with the user's intent.\n"
    'Default to "question". Choose "feedback" ONLY when the user explicitly wants to '
    "send a message, bug report, complaint, or suggestion TO the RadCrew team — never "
    "when they are merely asking about RadCrew, its work, or its people.\n\n"
    "Reply with ONLY one JSON object (no markdown fences) matching this JSON Schema:\n"
)

TOOL_ROUTING_SYSTEM_MESSAGE = (
    _ROUTING_INSTRUCTIONS + json.dumps(RoutingReply.model_json_schema(), indent=2)
)

# Few-shot examples steer the small model toward the RAG-biased default.
_FEWSHOT: tuple[tuple[str, str], ...] = (
    ("What does RadCrew build?", "question"),
    ("Who is on the team and what do they do?", "question"),
    ("Can you tell me about your AI work?", "question"),
    ("I want to report a bug on the contact page.", "feedback"),
    ("Please pass this suggestion to the team: add a dark mode.", "feedback"),
)


def build_feedback_routing_messages(message: str) -> list[dict[str, Any]]:
    msgs: list[dict[str, Any]] = [{"role": "system", "content": TOOL_ROUTING_SYSTEM_MESSAGE}]
    for example_message, example_intent in _FEWSHOT:
        msgs.append({"role": "user", "content": example_message})
        msgs.append({"role": "assistant", "content": json.dumps({"intent": example_intent})})
    msgs.append({"role": "user", "content": message})
    return msgs
