"""LangGraph state for /chat routing (feedback vs RAG)."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Literal, TypedDict

from app.chatbot.huggingface.tool_routing.types import ParsedToolCall
from app.chatbot.knowledge.models import KnowledgeDocument
from app.schemas import ChatRequest


class ChatState(TypedDict, total=False):
    """State passed through classify → feedback | RAG terminal nodes."""

    body: ChatRequest
    knowledge_chunks: list[KnowledgeDocument]
    route: Literal["feedback", "rag"]
    feedback_call: ParsedToolCall
    output_stream: Iterator[str]
