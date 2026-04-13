"""Chatbot state, startup knowledge load, and stream generation."""

from __future__ import annotations

from collections.abc import Iterator

from app.core.settings import get_settings
from app.chatbot.knowledge.models import KnowledgeDocument
from app.chatbot.graph.build import chat_graph
from app.chatbot.messages import MSG_AI_UNAVAILABLE
from app.schemas import ChatRequest

knowledge_chunks: list[KnowledgeDocument] = []


def set_knowledge_chunks(chunks: list[KnowledgeDocument]) -> None:
    global knowledge_chunks
    knowledge_chunks = chunks


def generate_chat_stream(
    body: ChatRequest,
) -> Iterator[str]:
    settings = get_settings()
    if not settings.HUGGINGFACE_API_KEY:
        return iter([MSG_AI_UNAVAILABLE])

    result = chat_graph.invoke(
        {
            "body": body,
            "knowledge_chunks": knowledge_chunks,
        }
    )
    return result["output_stream"]
