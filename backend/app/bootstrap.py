"""Startup wiring for loading knowledge chunks."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator, Callable

from fastapi import FastAPI

from app.chat.retrieval import build_knowledge_chunks, persist_knowledge_index
from app.config import get_settings
from app.knowledge import get_static_site_documents, load_contentful_documents
from app.models import KnowledgeChunk


def create_lifespan(
    on_chunks_loaded: Callable[[list[KnowledgeChunk]], None],
) -> Callable[[FastAPI], AsyncIterator[None]]:
    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        settings = get_settings()
        documents = [*get_static_site_documents(), *await load_contentful_documents(settings)]
        chunks = build_knowledge_chunks(documents)
        persist_knowledge_index(chunks)
        on_chunks_loaded(chunks)
        yield

    return lifespan
