"""Chatbot state, startup knowledge load, and stream generation."""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable, Iterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.chatbot.knowledge import get_static_site_documents
from app.chatbot.knowledge.github_loader import get_resume_documents
from app.chatbot.knowledge.models import KnowledgeChunk
from app.chatbot.langchain_service import run_chat_stream
from app.chatbot.rag.retrieval import build_knowledge_chunks
from app.core.settings import get_settings
from app.schemas import ChatRequest

knowledge_chunks: list[KnowledgeChunk] = []


def set_knowledge_chunks(chunks: list[KnowledgeChunk]) -> None:
    global knowledge_chunks
    knowledge_chunks = chunks


def create_lifespan(
    on_chunks_loaded: Callable[[list[KnowledgeChunk]], None],
) -> Callable[[FastAPI], AsyncIterator[None]]:
    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        settings = get_settings()
        documents = [
            *get_static_site_documents(),
            *get_resume_documents(
                repo_url=settings.GITHUB_KB_REPO_URL,
                token=settings.GITHUB_KB_TOKEN,
                branch=settings.GITHUB_KB_BRANCH,
                path_prefix=settings.GITHUB_KB_PATH,
            ),
        ]
        chunks = build_knowledge_chunks(documents)
        on_chunks_loaded(chunks)
        yield

    return lifespan


def generate_chat_stream(
    body: ChatRequest,
    chunks: list[KnowledgeChunk],
) -> Iterator[str]:
    return run_chat_stream(body, chunks)
