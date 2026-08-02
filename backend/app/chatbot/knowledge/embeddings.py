"""Cached document embeddings for semantic retrieval.

The knowledge corpus is fixed for the life of the process (loaded once at
startup). Embedding it on every ``/chat`` request — as a one-shot
``sentence_similarity`` call does — re-embeds the entire corpus over the network
each time and scales badly as the knowledge base grows.

This module embeds the corpus once (``index_documents``) and keeps the resulting
L2-normalized vectors in memory. Per request, only the short query is embedded
(``semantic_similarities``); similarity is then a local dot product, so cosine
scores match the previous behaviour while removing the per-request corpus
embedding.

Everything degrades gracefully: with no ``HF_TOKEN``/model, or before the corpus
is indexed, ``semantic_similarities`` returns zeros so callers fall back to
lexical retrieval exactly as before.
"""

from __future__ import annotations

import logging
import threading
from time import sleep

import numpy as np
from huggingface_hub import InferenceClient

from app.chatbot.huggingface.common import is_retryable_error
from app.chatbot.knowledge.models import KnowledgeDocument
from app.core.settings import get_settings

logger = logging.getLogger(__name__)

# Indexing attempts per batch, with the same linear backoff and the same
# retryable/permanent split as answer streaming. A reindex is many calls, so one
# transient 429 partway through should not throw away the whole run.
EMBEDDING_ATTEMPTS = 3
RETRY_BACKOFF_SECONDS = 0.25

# id -> L2-normalized embedding (float32). Populated once at startup.
_document_vectors: dict[str, np.ndarray] = {}
_lock = threading.Lock()

_client: InferenceClient | None = None
_client_key: tuple[str | None, str | None, str | None] | None = None


def _get_client() -> InferenceClient | None:
    """Return a cached InferenceClient for the embedding model, or None if unconfigured."""
    global _client, _client_key

    settings = get_settings()
    token = settings.HF_TOKEN
    model = settings.HUGGINGFACE_EMBEDDING_MODEL
    provider = settings.HUGGINGFACE_EMBEDDING_PROVIDER

    if not token or not model:
        return None

    key = (token, model, provider)
    if _client is None or _client_key != key:
        _client = InferenceClient(model=model, token=token, provider=provider)  # type: ignore[arg-type]
        _client_key = key
    return _client


def _embed_raw(texts: list[str]) -> np.ndarray:
    """One embedding call. Raises on transport or provider errors."""
    client = _get_client()
    if client is None:
        raise RuntimeError("embeddings are not configured")

    model = get_settings().HUGGINGFACE_EMBEDDING_MODEL
    vectors = np.asarray(client.feature_extraction(texts, model=model), dtype="float32")

    # A single string can come back 1-D; always work with (n, dim).
    if vectors.ndim == 1:
        vectors = vectors.reshape(1, -1)

    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms[norms == 0.0] = 1.0  # avoid divide-by-zero for empty/degenerate text
    return vectors / norms


def _embed(texts: list[str]) -> np.ndarray | None:
    """Embed texts to an (n, dim) L2-normalized float32 array, or None on failure.

    Deliberately not retried: this serves the per-request query embed, where a
    failure already degrades to lexical matching. Waiting out a backoff there
    would delay every answer to rescue a few.
    """
    if not texts:
        return None

    try:
        return _embed_raw(texts)
    except Exception as err:  # network/model errors must not break retrieval
        logger.error("[embeddings] feature_extraction failed: %s", err)
        return None


def embed_batched(texts: list[str]) -> np.ndarray | None:
    """Embed a whole corpus in batches, retrying transient failures.

    Indexing differs from the query path: it is a background cost, so waiting is
    cheap and losing a run is expensive. One oversized request also fails as a
    unit, which is what batching avoids.

    Returns None if any batch is unrecoverable, since callers match vectors to
    chunks by position and a short array would silently misalign them.
    """
    if not texts:
        return None

    batch_size = get_settings().EMBEDDING_BATCH_SIZE
    batches: list[np.ndarray] = []

    for start in range(0, len(texts), batch_size):
        batch = texts[start : start + batch_size]
        vectors = _embed_with_retry(batch)
        if vectors is None:
            return None
        batches.append(vectors)

    return np.vstack(batches)


def _embed_with_retry(batch: list[str]) -> np.ndarray | None:
    for attempt in range(1, EMBEDDING_ATTEMPTS + 1):
        try:
            return _embed_raw(batch)
        except Exception as err:
            logger.error(
                "[embeddings] batch of %d failed (attempt %d/%d): %s",
                len(batch),
                attempt,
                EMBEDDING_ATTEMPTS,
                err,
            )
            if not is_retryable_error(err) or attempt == EMBEDDING_ATTEMPTS:
                return None
            sleep(RETRY_BACKOFF_SECONDS * attempt)
    return None


def index_documents(documents: list[KnowledgeDocument]) -> None:
    """Embed the documents once and cache the normalized vectors by document id.

    Safe to call when embeddings are unconfigured: it simply leaves the store
    empty, and ``semantic_similarities`` will report zeros (→ lexical fallback).
    """
    candidates = [f"{doc.title}\n{doc.text}" for doc in documents]
    vectors = _embed(candidates)

    with _lock:
        _document_vectors.clear()
        if vectors is None:
            logger.warning("[embeddings] documents not indexed (embeddings unavailable)")
            return
        for doc, vector in zip(documents, vectors):
            _document_vectors[doc.id] = vector

    logger.info("[embeddings] indexed %d documents", len(_document_vectors))


def semantic_similarities(documents: list[KnowledgeDocument], query: str) -> list[float]:
    """Cosine similarity of ``query`` against each document, in input order.

    Uses the cached document vectors and embeds only the query. Returns 0.0 for
    any document missing from the store (or all zeros when unavailable), matching
    the old behaviour so the lexical fallback still kicks in.
    """
    if not documents:
        return []

    query_vectors = _embed([query])
    if query_vectors is None:
        return [0.0] * len(documents)
    query_vector = query_vectors[0]

    with _lock:
        scores: list[float] = []
        for doc in documents:
            stored = _document_vectors.get(doc.id)
            if stored is None:
                scores.append(0.0)
                continue
            scores.append(max(0.0, float(stored @ query_vector)))
    return scores
