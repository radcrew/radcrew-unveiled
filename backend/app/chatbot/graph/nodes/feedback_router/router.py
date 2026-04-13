import logging
from typing import Literal

from huggingface_hub import InferenceClient
from huggingface_hub.inference._generated.types.chat_completion import ChatCompletionInputResponseFormatJSONObject

from app.core.settings import get_settings
from app.chatbot.graph.state import ChatState
from app.chatbot.huggingface.common import DETERMINISTIC_GENERATION_SEED
from .message import build_feedback_routing_messages
from app.chatbot.huggingface.tool_routing.parse import (
    extract_message_content,
    parse_tool_call_reply,
)

logger = logging.getLogger(__name__)

def route_feedback_or_rag(state: ChatState) -> Literal["feedback", "rag"]:
    return state["route"]


def feedback_router_node(state: ChatState) -> dict[str, object]:
    settings = get_settings()
    body = state["body"]
    
    routing_msgs = build_feedback_routing_messages(body.message)

    try:
        client = InferenceClient(
            model=settings.HUGGINGFACE_MODEL,
            token=settings.HUGGINGFACE_API_KEY,
            provider=settings.HUGGINGFACE_PROVIDER
        )  # type: ignore[arg-type]
        resp = client.chat_completion(
            messages=routing_msgs,
            max_tokens=512,
            temperature=0,
            top_p=1,
            seed=DETERMINISTIC_GENERATION_SEED,
            response_format=ChatCompletionInputResponseFormatJSONObject(type="json_object")
        )
        content = extract_message_content(resp)
        feedback_call = parse_tool_call_reply(content)

        if feedback_call is not None:
            return feedback_call
        
    except Exception as err:
        logger.error("[HF feedback routing] %s", err)

    return {"route": "rag"}
