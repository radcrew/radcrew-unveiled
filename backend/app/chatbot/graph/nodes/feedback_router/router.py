import json
import logging
from typing import Literal

from huggingface_hub import InferenceClient
from huggingface_hub.inference._generated.types.chat_completion import (
    ChatCompletionInputResponseFormatJSONSchema,
    ChatCompletionInputJSONSchema
)

from .message import RoutingReply
from app.core.settings import get_settings
from app.chatbot.graph.state import ChatState
from app.chatbot.huggingface.common import DETERMINISTIC_GENERATION_SEED
from app.chatbot.messages import MSG_FEEDBACK_CONFIRM_MARKER
from app.schemas import ChatHistoryMessage
from .message import build_feedback_routing_messages
from .parse import ParsedToolCall, parse_routing_intent
from .pregate import should_skip_llm_route_to_rag
from .confirm import is_affirmation, is_negation

logger = logging.getLogger(__name__)


def route_feedback_or_rag(state: ChatState) -> Literal["feedback", "rag"]:
    return state["route"]


def _awaiting_feedback_confirmation(history: list[ChatHistoryMessage]) -> bool:
    """True when our most recent reply was the confirmation prompt."""
    for msg in reversed(history):
        if msg.role == "assistant":
            return MSG_FEEDBACK_CONFIRM_MARKER in msg.content
    return False


def _last_user_message(history: list[ChatHistoryMessage]) -> str:
    for msg in reversed(history):
        if msg.role == "user":
            return msg.content
    return ""


def _feedback_call(message: str, call_id: str) -> ParsedToolCall:
    return ParsedToolCall(
        id=call_id,
        name="send_feedback",
        arguments=json.dumps({"message": message, "subject": None}),
    )


def feedback_router_node(state: ChatState) -> dict[str, object]:
    settings = get_settings()
    body = state["body"]
    history = body.history or []

    # Solution D: if we just asked the user to confirm, act on their reply
    # instead of re-classifying it.
    if _awaiting_feedback_confirmation(history):
        if is_affirmation(body.message):
            logger.info("[feedback routing] confirmation → send")
            original = _last_user_message(history)
            return {
                "route": "feedback",
                "feedback_call": _feedback_call(original, "confirmed"),
                "feedback_phase": "send",
            }
        if is_negation(body.message):
            logger.info("[feedback routing] confirmation → cancel")
            return {"route": "feedback", "feedback_phase": "cancel"}
        # Neither yes nor no — drop the pending feedback and route normally.

    # Deterministic pre-gate (Solution A): a plain question with no feedback
    # signal goes straight to RAG, bypassing the over-eager LLM classifier.
    if should_skip_llm_route_to_rag(body.message):
        logger.info("[feedback routing] pre-gate → rag (question)")
        return {"route": "rag"}

    routing_msgs = build_feedback_routing_messages(body.message)

    try:
        client = InferenceClient(
            model=settings.HUGGINGFACE_MODEL,
            token=settings.HF_TOKEN,
            provider=settings.HUGGINGFACE_PROVIDER
        )  # type: ignore[arg-type]
        resp = client.chat_completion(
            messages=routing_msgs,
            max_tokens=512,
            temperature=0,
            top_p=1,
            seed=DETERMINISTIC_GENERATION_SEED,
            response_format=ChatCompletionInputResponseFormatJSONSchema(
                type="json_schema",
                json_schema=ChatCompletionInputJSONSchema(
                    name="routing_reply",
                    description="Label the message intent: question (→ RAG) or feedback.",
                    schema=RoutingReply.model_json_schema(),
                    strict=True,
                ),
            )
        )

        intent = parse_routing_intent(resp.choices[0].message.content)

        if intent == "feedback":
            # Solution D: don't send yet — ask the user to confirm first.
            logger.info("[feedback routing] llm → feedback (ask to confirm)")
            return {
                "route": "feedback",
                "feedback_call": _feedback_call(body.message, "ask"),
                "feedback_phase": "ask",
            }

    except Exception as err:
        logger.error("[HF feedback routing] %s", err)

    return {"route": "rag"}
