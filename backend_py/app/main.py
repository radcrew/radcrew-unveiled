import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from app.chat.huggingface import generate_answer
from app.chat.prompt import build_chat_prompt
from app.chat.retrieval import (
    build_knowledge_chunks,
    persist_knowledge_index,
    retrieve_relevant_chunks,
    retrieval_fallback_needed,
)
from app.config import get_settings
from app.knowledge import get_static_site_documents, load_contentful_documents
from app.models import KnowledgeChunk, KnowledgeChunkScored
from app.schemas import ChatRequest

logger = logging.getLogger(__name__)

_settings = get_settings()
PORT = _settings.PORT
FRONTEND_ORIGIN = _settings.FRONTEND_ORIGIN

knowledge_chunks: list[KnowledgeChunk] = []

# User-facing strings (parity with backend/src/server.ts).
_MSG_FALLBACK_LOW_CONTEXT = (
    "I don't have enough verified context for that yet. Please email hello@radcrew.dev "
    "and the team can help directly."
)
_MSG_MISSING_HF_KEY = (
    "The FAQ assistant is not configured yet. Set HUGGINGFACE_API_KEY or HF_TOKEN in "
    "backend_py/.env (see backend_py/.env.example), then restart the server."
)
_MSG_AI_UNAVAILABLE = (
    "The AI service is temporarily unavailable. Please try again in a moment or "
    "email hello@radcrew.dev."
)


def _scored_to_chunk(scored: KnowledgeChunkScored) -> KnowledgeChunk:
    return KnowledgeChunk(
        id=scored.id,
        title=scored.title,
        text=scored.text,
        tokens=scored.tokens,
        url=scored.url,
    )


@asynccontextmanager
async def lifespan(_app: FastAPI):
    global knowledge_chunks
    settings = get_settings()
    documents = [*get_static_site_documents(), *await load_contentful_documents(settings)]
    knowledge_chunks = build_knowledge_chunks(documents)
    persist_knowledge_index(knowledge_chunks)
    yield


limiter = Limiter(key_func=get_remote_address, default_limits=["25/minute"])

app = FastAPI(lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SlowAPIMiddleware)


@app.exception_handler(RequestValidationError)
async def request_validation_handler(_request: Request, _exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"error": "Invalid request payload."})


@app.get("/health")
def health() -> dict:
    return {"ok": True, "chunks": len(knowledge_chunks)}


@app.post("/chat", response_model=None)
def chat(body: ChatRequest) -> dict | JSONResponse:
    try:
        message = body.message
        relevant = retrieve_relevant_chunks(knowledge_chunks, message, 5)

        if retrieval_fallback_needed(relevant):
            return {
                "answer": _MSG_FALLBACK_LOW_CONTEXT,
                "confidence": 0.2,
                "sources": [],
            }

        settings = get_settings()
        if not settings.HUGGINGFACE_API_KEY:
            return {
                "answer": _MSG_MISSING_HF_KEY,
                "confidence": 0,
                "sources": [],
            }

        context_chunks = [_scored_to_chunk(c) for c in relevant]
        prompt = build_chat_prompt(message, context_chunks)
        answer = generate_answer(
            settings.HUGGINGFACE_MODEL,
            settings.HUGGINGFACE_API_KEY,
            prompt,
            settings.HUGGINGFACE_PROVIDER,
        )

        return {
            "answer": answer,
            "confidence": min(1.0, relevant[0].score / 3),
            "sources": [
                {
                    "id": c.id,
                    "title": c.title,
                    "snippet": c.text,
                    **({"url": c.url} if c.url is not None else {}),
                }
                for c in relevant
            ],
        }
    except Exception:
        logger.exception("POST /chat failed")
        return JSONResponse(
            status_code=502,
            content={"error": _MSG_AI_UNAVAILABLE},
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=PORT)
