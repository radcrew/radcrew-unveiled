"""HTTP app setup (middleware, limiter, and shared handlers)."""

from __future__ import annotations

import logging

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

logger = logging.getLogger(__name__)


def create_http_app(cors_origins: list[str], rate_limit: str) -> FastAPI:
    # A browser blocked by CORS sees only "No 'Access-Control-Allow-Origin'
    # header", with no hint about what the server would have accepted, and
    # CORSMiddleware answers a rejected preflight with a bare 400 that reads
    # like a malformed request. Stating the allowlist at startup turns that
    # into a one-line comparison. Origins are configuration, not secrets.
    logger.info("[cors] allowed origins: %s", cors_origins)
    if "*" in cors_origins:
        logger.warning(
            "[cors] wildcard origin is enabled; any site can call this API. "
            "Set FRONTEND_ORIGINS to an explicit list outside local development."
        )

    limiter = Limiter(key_func=get_remote_address, default_limits=[rate_limit])

    app = FastAPI(lifespan=create_lifespan(set_knowledge_documents))
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # Restrict to the configured frontend origins. A literal "*" is accepted but
    # not equivalent to "no CORS": with allow_credentials set, Starlette echoes
    # the caller's origin back instead of sending "*", so browsers do not reject
    # it and every site on the internet can call this API and read the response.
    # Keep the list explicit outside local development.
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
