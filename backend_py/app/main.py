from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.chat.retrieval import build_knowledge_chunks, persist_knowledge_index
from app.config import get_settings
from app.knowledge import get_static_site_documents, load_contentful_documents
from app.models import KnowledgeChunk

_settings = get_settings()
PORT = _settings.PORT
FRONTEND_ORIGIN = _settings.FRONTEND_ORIGIN

knowledge_chunks: list[KnowledgeChunk] = []


@asynccontextmanager
async def lifespan(_app: FastAPI):
    global knowledge_chunks
    settings = get_settings()
    documents = [*get_static_site_documents(), *await load_contentful_documents(settings)]
    knowledge_chunks = build_knowledge_chunks(documents)
    persist_knowledge_index(knowledge_chunks)
    yield


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"ok": True, "chunks": len(knowledge_chunks)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=PORT)
