from contextlib import asynccontextmanager
from collections.abc import AsyncIterator, Callable

from fastapi import FastAPI

from app.chatbot.knowledge.models import KnowledgeDocument
from app.core.settings import get_settings
from app.chatbot.knowledge import get_static_site_documents
from app.chatbot.knowledge.github_loader import get_resume_documents

def create_lifespan(
    on_chunks_loaded: Callable[[list[KnowledgeDocument]], None],
) -> Callable[[FastAPI], AsyncIterator[None]]:
    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        settings = get_settings()
        documents = [
            *get_static_site_documents(),
            *get_resume_documents(
                repo_url=settings.GITHUB_REPO_URL,
                token=settings.GITHUB_TOKEN,
                branch=settings.GITHUB_BRANCH,
                path_prefix=settings.GITHUB_PATH,
            ),
        ]
        on_chunks_loaded(documents)
        yield

    return lifespan