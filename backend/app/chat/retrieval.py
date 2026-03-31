"""Knowledge indexing (one unit per document) and hybrid retrieval (lexical + semantic embeddings)."""

from __future__ import annotations

import logging
import re

from huggingface_hub import InferenceClient
from app.models import KnowledgeChunk, KnowledgeChunkScored, KnowledgeDocument

TOKEN_RE = re.compile(r"[a-z0-9]+", re.IGNORECASE)

# Same threshold as backend/src/server.ts (`relevantChunks[0].score < 1.2`).
RETRIEVAL_FALLBACK_SCORE_THRESHOLD = 1.2
SEMANTIC_SCORE_WEIGHT = 2.0

logger = logging.getLogger(__name__)


def tokenize(text: str) -> list[str]:
    return [t for t in TOKEN_RE.findall(text.lower()) if len(t) > 1]


def _semantic_scores(
    *,
    chunks: list[KnowledgeChunk],
    query: str,
    embedding_access_token: str,
    embedding_model: str,
    embedding_provider: str,
) -> list[float]:
    if not chunks:
        return []
    client = InferenceClient(
        model=embedding_model,
        token=embedding_access_token,
        provider=embedding_provider,  # type: ignore[arg-type]
    )
    candidates = [f"{chunk.title}\n{chunk.text}" for chunk in chunks]
    similarities = client.sentence_similarity(
        sentence=query,
        other_sentences=candidates,
        model=embedding_model,
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
    *,
    embedding_access_token: str | None = None,
    embedding_model: str | None = None,
    embedding_provider: str = "hf-inference",
) -> list[KnowledgeChunkScored]:
    query_tokens = set(tokenize(query))
    if len(query_tokens) == 0:
        return []

    semantic_by_index = [0.0] * len(chunks)
    if embedding_access_token and embedding_model:
        try:
            semantic_by_index = _semantic_scores(
                chunks=chunks,
                query=query,
                embedding_access_token=embedding_access_token,
                embedding_model=embedding_model,
                embedding_provider=embedding_provider,
            )
        except Exception as exc:
            logger.warning("Semantic retrieval unavailable, using lexical fallback: %s", exc)

    scored: list[KnowledgeChunkScored] = []
    for idx, chunk in enumerate(chunks):
        overlap = sum(1 for t in chunk.tokens if t in query_tokens)
        density = overlap / max(len(chunk.tokens), 1)
        lexical_score = overlap + density
        score = lexical_score + (SEMANTIC_SCORE_WEIGHT * semantic_by_index[idx])
        if score > 0:
            scored.append(
                KnowledgeChunkScored(
                    id=chunk.id,
                    title=chunk.title,
                    text=chunk.text,
                    tokens=chunk.tokens,
                    score=score,
                    url=chunk.url,
                )
            )

    # Stable tie-breaking keeps context ordering deterministic across runs.
    scored.sort(key=lambda c: (-c.score, c.id, c.title))
    return scored[:limit]


def retrieval_fallback_needed(chunks: list[KnowledgeChunkScored]) -> bool:
    """True when the chat handler should use the low-context fallback response."""
    return len(chunks) == 0 or chunks[0].score < RETRIEVAL_FALLBACK_SCORE_THRESHOLD
