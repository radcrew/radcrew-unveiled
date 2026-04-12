"""Knowledge indexing (one unit per document) and hybrid retrieval (lexical + semantic embeddings)."""

from __future__ import annotations
import logging
import re
from huggingface_hub import InferenceClient
from app.core.config import get_settings
from app.chatbot.rag.models import EmbeddingInferenceConfig
from app.chatbot.knowledge.models import KnowledgeChunk, KnowledgeDocument

TOKEN_RE = re.compile(r"[a-z0-9]+", re.IGNORECASE)

# Same threshold as backend/src/server.ts (`relevantChunks[0].score < 1.2`).
RETRIEVAL_FALLBACK_SCORE_THRESHOLD = 1.2
SEMANTIC_SCORE_WEIGHT = 2.0

logger = logging.getLogger(__name__)


def tokenize(text: str) -> list[str]:
    return [t for t in TOKEN_RE.findall(text.lower()) if len(t) > 1]


def _get_semantic_scores(
    chunks: list[KnowledgeChunk],
    query: str,
) -> list[float]:
    settings = get_settings()

    token = settings.HUGGINGFACE_API_KEY
    model = settings.HUGGINGFACE_EMBEDDING_MODEL
    provider=settings.HUGGINGFACE_EMBEDDING_PROVIDER

    if not chunks:
        return []

    if not token or not model:
        return [0.0] * len(chunks)

    client = InferenceClient(
        model=model,
        token=token,
        provider=provider,  # type: ignore[arg-type]
    )

    candidates = [f"{chunk.title}\n{chunk.text}" for chunk in chunks]

    similarities = client.sentence_similarity(
        sentence=query,
        other_sentences=candidates,
        model=model,
    )
    # Clamp negatives to 0 so semantic score only boosts, never penalizes lexical matches.
    return [max(0.0, float(s)) for s in similarities]


def build_knowledge_chunks(documents: list[KnowledgeDocument]) -> list[KnowledgeChunk]:
    """One retrieval row per document (full body text; no sentence splitting)."""
    out: list[KnowledgeChunk] = []

    for doc in documents:
        tokens = tokenize(doc.text)
        if len(tokens) == 0:
            continue

        out.append(
            KnowledgeChunk(
                id=f"{doc.id}:0",
                title=doc.title,
                text=doc.text,
                tokens=tokens,
                url=doc.url,
            )
        )

    return out


def retrieve_relevant_chunks(
    chunks: list[KnowledgeChunk],
    query: str,
    limit: int = 5,
) -> list[KnowledgeChunk]:
    query_tokens = set(tokenize(query))
    if len(query_tokens) == 0:
        return []

    semantic_scores = []

    try:
        semantic_scores = _get_semantic_scores(chunks, query)
    except Exception as exc:
        logger.warning("Semantic retrieval unavailable, using lexical fallback: %s", exc)

    relevant_chunks: list[KnowledgeChunk] = []
    for idx, chunk in enumerate(chunks):
        overlap = sum(1 for t in chunk.tokens if t in query_tokens)
        density = overlap / max(len(chunk.tokens), 1)
        lexical_score = overlap + density
        score = lexical_score + (SEMANTIC_SCORE_WEIGHT * semantic_scores[idx])

        if score > 0:
            relevant_chunks.append(
                KnowledgeChunk(
                    id=chunk.id,
                    title=chunk.title,
                    text=chunk.text,
                    tokens=chunk.tokens,
                    url=chunk.url,
                    score=score,
                )
            )

    # Stable tie-breaking keeps context ordering deterministic across runs.
    relevant_chunks.sort(key=lambda c: (-(c.score or 0.0), c.id, c.title))
    return relevant_chunks[:limit]


def retrieval_fallback_needed(chunks: list[KnowledgeChunk]) -> bool:
    """True when the chat handler should use the low-context fallback response."""
    if len(chunks) == 0:
        return True
    top = chunks[0].score
    return top is None or top < RETRIEVAL_FALLBACK_SCORE_THRESHOLD
