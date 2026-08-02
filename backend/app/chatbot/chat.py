"""Chatbot state, startup knowledge load, and stream generation."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass

from app.core.settings import get_settings
from app.chatbot.knowledge.models import KnowledgeDocument
from app.chatbot.graph.build import chat_graph
from app.chatbot.messages import MSG_AI_UNAVAILABLE
from app.schemas import ChatRequest

knowledge_documents: list[KnowledgeDocument] = []


def set_knowledge_documents(documents: list[KnowledgeDocument]) -> None:
    global knowledge_documents
    knowledge_documents = documents


@dataclass(frozen=True)
class ChatStream:
    """An answer stream plus the follow-up hints to offer under it.

    Hints are plain data, known before the first token because the graph runs
    its nodes eagerly, so the endpoint can hold them while the stream drains.
    """

    chunks: Iterator[str]
    hints: tuple[str, ...] = ()


def generate_chat_stream(body: ChatRequest) -> ChatStream:
    settings = get_settings()
    if settings.llm_provider() == "none":
        return ChatStream(iter([MSG_AI_UNAVAILABLE]))

    result = chat_graph.invoke(
        {
            "body": body,
            "knowledge_documents": knowledge_documents,
        }
    )
    return ChatStream(result["output_stream"], tuple(result.get("hints", ())))
