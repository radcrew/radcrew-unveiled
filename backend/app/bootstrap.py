"""Startup wiring for loading knowledge chunks."""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.chat.retrieval import build_knowledge_chunks
from app.config import get_settings
from app.knowledge import get_static_site_documents
from app.knowledge.contentful_loader import get_contentful_documents
from app.knowledge.github_loader import get_github_markdown_documents
from app.models import KnowledgeChunk


def create_lifespan(
    on_chunks_loaded: Callable[[list[KnowledgeChunk]], None],
) -> Callable[[FastAPI], AsyncIterator[None]]:
    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        settings = get_settings()
        github_repo_url = str(settings.GITHUB_KB_REPO_URL) if settings.GITHUB_KB_REPO_URL else None
        documents = [
            *get_static_site_documents(),
            *get_contentful_documents(
                space_id=settings.CONTENTFUL_SPACE_ID,
                access_token=settings.CONTENTFUL_DELIVERY_TOKEN,
                environment=settings.CONTENTFUL_ENVIRONMENT,
                content_types_csv=settings.CONTENTFUL_RAG_CONTENT_TYPES,
                site_base_url=settings.FRONTEND_ORIGIN,
            ),
            *get_github_markdown_documents(
                repo_url=github_repo_url,
                token=settings.GITHUB_KB_TOKEN,
                branch=settings.GITHUB_KB_BRANCH,
                path_prefix=settings.GITHUB_KB_PATH,
            ),
        ]
        chunks = build_knowledge_chunks(documents)
        on_chunks_loaded(chunks)
        yield

    return lifespan
