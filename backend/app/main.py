"""FastAPI application entry — mounts API routers and shared middleware."""

from __future__ import annotations

import uvicorn

from app.api import chat, health
from app.chatbot import chat as chatbot
from app.core.settings import get_settings
from app.core.http import create_http_app
from app.core.logger import configure_logging

configure_logging()

_settings = get_settings()

app = create_http_app(
    frontend_origin=_settings.FRONTEND_ORIGIN,
    lifespan=chatbot.create_lifespan(chatbot.set_knowledge_chunks),
)
app.include_router(health.router)
app.include_router(chat.router)

PORT = _settings.PORT

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=PORT)
