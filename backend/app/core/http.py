"""HTTP app setup (middleware, limiter, and shared handlers)."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from app.core.lifespan import create_lifespan
from app.chatbot.chat import set_knowledge_documents


def create_http_app(cors_origins: list[str], rate_limit: str) -> FastAPI:
    limiter = Limiter(key_func=get_remote_address, default_limits=[rate_limit])

    app = FastAPI(lifespan=create_lifespan(set_knowledge_documents))
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # Restrict to the configured frontend origins. A wildcard cannot be combined
    # with allow_credentials (browsers reject it), so the explicit list matters.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(SlowAPIMiddleware)

    @app.exception_handler(RequestValidationError)
    async def request_validation_handler(_request: Request, _exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(status_code=400, content={"error": "Invalid request payload."})

    return app
