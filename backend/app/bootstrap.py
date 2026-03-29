"""Startup wiring for loading knowledge chunks."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator, Callable

from fastapi import FastAPI

from app.chat.retrieval import build_knowledge_chunks, persist_knowledge_index
from app.knowledge import get_static_site_documents
from app.models import KnowledgeChunk


def create_lifespan(
    on_chunks_loaded: Callable[[list[KnowledgeChunk]], None],
) -> Callable[[FastAPI], AsyncIterator[None]]:
    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        documents = [*get_static_site_documents()]
        chunks = build_knowledge_chunks(documents)
        persist_knowledge_index(chunks)
        on_chunks_loaded(chunks)
        yield

    return lifespan
