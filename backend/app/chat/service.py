"""Chat orchestration for /chat route."""

from __future__ import annotations
from collections.abc import Iterator

from app.chat.graph.graph import run_chat_stream
from app.knowledge.models import KnowledgeChunk
from app.schemas import ChatRequest


def generate_chat_stream(
    body: ChatRequest,
    knowledge_chunks: list[KnowledgeChunk],
) -> Iterator[str]:

    return run_chat_stream(body, knowledge_chunks)
