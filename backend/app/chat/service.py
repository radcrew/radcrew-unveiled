"""Chat orchestration for /chat route."""

from __future__ import annotations

from collections.abc import Iterator

from app.chat.feedback.tool_branch import try_feedback_tool_call
from app.chat.rag.stream import stream_rag_chat_answer
from app.config import get_settings
from app.knowledge.models import KnowledgeChunk
from app.schemas import ChatRequest


def generate_chat_stream(
    body: ChatRequest,
    knowledge_chunks: list[KnowledgeChunk],
) -> Iterator[str]:
    settings = get_settings()
    message = body.message
    history = body.history or []

    if settings.HUGGINGFACE_API_KEY:
        response_stream = try_feedback_tool_call(settings, message, history)
        if response_stream is not None:
            return response_stream

    return stream_rag_chat_answer(body, knowledge_chunks, settings)
