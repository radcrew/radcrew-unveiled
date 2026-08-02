"""Corpus embeddings in Postgres, via pgvector.

The in-process cache in ``embeddings.py`` re-embeds the whole corpus every time
the process starts, which on serverless means every cold start spends embedding
calls on content that has not changed. This store keeps the vectors between
restarts, so indexing costs something only when the text or the embedding model
actually changes.

Rows are chunks (see ``chunking.py``) but ``search`` returns document ids, so
retrieval, hints, and the prompt all stay document-shaped.

Every entry point fails open. A database that is unreachable, slow, or empty
returns nothing and retrieval falls back to lexical keyword matching, exactly as
it does without ``HF_TOKEN``. Postgres blinking must never fail a chat.
"""

from __future__ import annotations

import logging
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from hashlib import sha256
from typing import Any

import numpy as np

from app.chatbot.knowledge.chunking import Chunk
from app.core.settings import get_settings

logger = logging.getLogger(__name__)

# Dimension of sentence-transformers/all-MiniLM-L6-v2. Baked into the column, so
# changing HUGGINGFACE_EMBEDDING_MODEL means an ALTER TABLE and a full re-embed.
EMBEDDING_DIMENSIONS = 384

# A query matches chunks, but callers rank documents. Over-fetch so a document
# whose chunks cluster at the top cannot crowd the rest out of the result.
OVERFETCH_FACTOR = 4

# Long enough for a cold pooled connection, short enough that a stuck query
# trips the fallback instead of holding a chat request open.
STATEMENT_TIMEOUT_MS = 3000

_SCHEMA = f"""
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS knowledge_chunk (
  id              bigserial PRIMARY KEY,
  document_id     text NOT NULL,
  chunk_index     int  NOT NULL,
  title           text NOT NULL,
  body            text NOT NULL,
  url             text,
  content_hash    text NOT NULL,
  embedding_model text NOT NULL,
  embedding       vector({EMBEDDING_DIMENSIONS}) NOT NULL,
  updated_at      timestamptz NOT NULL DEFAULT now(),
  UNIQUE (document_id, chunk_index)
);

CREATE INDEX IF NOT EXISTS knowledge_chunk_embedding_idx
  ON knowledge_chunk USING hnsw (embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS knowledge_chunk_document_idx
  ON knowledge_chunk (document_id);
"""

_pool: Any = None


def chunk_hash(chunk: Chunk) -> str:
    """Content fingerprint for one chunk, used to skip unchanged rows."""
    return sha256(chunk.embed_text.encode("utf-8")).hexdigest()


def _get_pool() -> Any:
    """Lazily build the connection pool, or None when unconfigured."""
    global _pool

    settings = get_settings()
    if not settings.DATABASE_URL:
        return None
    if _pool is not None:
        return _pool

    from psycopg_pool import ConnectionPool

    _pool = ConnectionPool(
        conninfo=settings.DATABASE_URL,
        # Serverless runs many short-lived instances against a connection cap,
        # so hold as few as possible and open them only on demand.
        min_size=0,
        max_size=2,
        timeout=5.0,
        open=True,
        kwargs={
            "application_name": "radcrew-chat",
            "options": f"-c statement_timeout={STATEMENT_TIMEOUT_MS}",
        },
    )
    return _pool


def reset_pool() -> None:
    """Drop the cached pool. For tests and for reconfiguration."""
    global _pool
    if _pool is not None:
        try:
            _pool.close()
        except Exception:  # closing a broken pool must not raise
            logger.debug("[vector store] pool close failed", exc_info=True)
    _pool = None


@contextmanager
def _connection() -> Iterator[Any]:
    pool = _get_pool()
    if pool is None:
        raise RuntimeError("vector store is not configured")
    with pool.connection() as connection:
        yield connection


def _vector_literal(vector: np.ndarray) -> str:
    """pgvector's text form, cast with ``::vector`` at the call site.

    Sent as a bound parameter, never interpolated. Passing the literal keeps the
    driver free of a registered vector type, which would otherwise have to be
    looked up on every new connection and fails before the extension exists.
    """
    return "[" + ",".join(f"{float(value):.7g}" for value in vector) + "]"


def is_available() -> bool:
    """Whether the store is configured and answering.

    Configured-but-unreachable is the silent degradation ``/health`` exists to
    expose: retrieval keeps working, quietly, on lexical matching alone.
    """
    try:
        with _connection() as connection, connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            return True
    except Exception as err:
        logger.warning("[vector store] unavailable: %s", err)
        return False


def ensure_schema() -> bool:
    """Create the extension, table, and indexes if they are absent."""
    try:
        with _connection() as connection, connection.cursor() as cursor:
            cursor.execute(_SCHEMA)
        return True
    except Exception as err:
        logger.error("[vector store] schema setup failed: %s", err)
        return False


def fingerprints() -> dict[tuple[str, int], tuple[str, str]]:
    """``(document_id, chunk_index) -> (content_hash, embedding_model)`` for stored rows.

    The caller diffs this against the loaded corpus and embeds only the
    difference. Returns empty on failure, which re-embeds everything: wasteful,
    but never wrong.
    """
    try:
        with _connection() as connection, connection.cursor() as cursor:
            cursor.execute(
                "SELECT document_id, chunk_index, content_hash, embedding_model FROM knowledge_chunk"
            )
            return {
                (document_id, chunk_index): (content_hash, model)
                for document_id, chunk_index, content_hash, model in cursor.fetchall()
            }
    except Exception as err:
        logger.error("[vector store] reading fingerprints failed: %s", err)
        return {}


def upsert_chunks(
    chunks: Sequence[Chunk],
    vectors: np.ndarray,
    embedding_model: str,
    urls: dict[str, str | None] | None = None,
) -> int:
    """Insert or refresh the given chunks. Returns the number of rows written.

    The predicate makes an unchanged chunk a no-op, and a changed embedding
    model re-embed even when the text is identical. Without that second half,
    swapping models leaves every hash matching and every vector stale, so
    retrieval silently compares vectors from two different models.
    """
    if len(chunks) == 0:
        return 0

    urls = urls or {}
    rows = [
        (
            chunk.document_id,
            chunk.chunk_index,
            chunk.title,
            chunk.body,
            urls.get(chunk.document_id),
            chunk_hash(chunk),
            embedding_model,
            _vector_literal(vector),
        )
        for chunk, vector in zip(chunks, vectors)
    ]

    try:
        with _connection() as connection, connection.cursor() as cursor:
            cursor.executemany(
                """
                INSERT INTO knowledge_chunk
                  (document_id, chunk_index, title, body, url, content_hash, embedding_model, embedding)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s::vector)
                ON CONFLICT (document_id, chunk_index) DO UPDATE SET
                  title = EXCLUDED.title,
                  body = EXCLUDED.body,
                  url = EXCLUDED.url,
                  content_hash = EXCLUDED.content_hash,
                  embedding_model = EXCLUDED.embedding_model,
                  embedding = EXCLUDED.embedding,
                  updated_at = now()
                WHERE knowledge_chunk.content_hash <> EXCLUDED.content_hash
                   OR knowledge_chunk.embedding_model <> EXCLUDED.embedding_model
                """,
                rows,
            )
        logger.info("[vector store] upserted %d chunks", len(rows))
        return len(rows)
    except Exception as err:
        logger.error("[vector store] upsert failed: %s", err)
        return 0


def delete_missing(chunk_counts: dict[str, int]) -> int:
    """Drop rows for documents no longer in the corpus, and for trimmed tails.

    Without this a deleted GitHub file keeps matching queries forever. Its id no
    longer resolves to a document, so it just vanishes from results with no
    explanation anywhere.
    """
    if not chunk_counts:
        # `document_id <> ALL('{}')` is true for every row, so an empty corpus
        # would delete the whole table. That is a failed load far more often
        # than an intentional wipe (GitHub unreachable, startup half-finished),
        # and the store is the only copy of the vectors. Keep what is there.
        logger.warning("[vector store] refusing to delete: the corpus is empty")
        return 0

    document_ids = list(chunk_counts)
    counts = [chunk_counts[document_id] for document_id in document_ids]

    try:
        with _connection() as connection, connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM knowledge_chunk WHERE document_id <> ALL(%s::text[])",
                (document_ids,),
            )
            removed = cursor.rowcount or 0

            # A document that shrank keeps its high chunk_index rows otherwise.
            cursor.execute(
                """
                DELETE FROM knowledge_chunk kc
                USING unnest(%s::text[], %s::int[]) AS keep(document_id, chunk_count)
                WHERE kc.document_id = keep.document_id
                  AND kc.chunk_index >= keep.chunk_count
                """,
                (document_ids, counts),
            )
            removed += cursor.rowcount or 0

        if removed:
            logger.info("[vector store] deleted %d stale chunks", removed)
        return removed
    except Exception as err:
        logger.error("[vector store] delete failed: %s", err)
        return 0


def search(query_vector: np.ndarray, limit: int) -> list[tuple[str, float]]:
    """``(document_id, cosine similarity)`` best first, one entry per document."""
    try:
        with _connection() as connection, connection.cursor() as cursor:
            cursor.execute(
                # Order by the distance operator, not by the similarity alias:
                # ordering on the alias discards the HNSW index and scans.
                """
                SELECT document_id, 1 - (embedding <=> %s::vector) AS similarity
                FROM knowledge_chunk
                ORDER BY embedding <=> %s::vector
                LIMIT %s
                """,
                (
                    _vector_literal(query_vector),
                    _vector_literal(query_vector),
                    limit * OVERFETCH_FACTOR,
                ),
            )
            rows = cursor.fetchall()
    except Exception as err:
        logger.error("[vector store] search failed: %s", err)
        return []

    # Rows arrive best first, so the first sighting of a document is its best chunk.
    best: dict[str, float] = {}
    for document_id, similarity in rows:
        if document_id not in best:
            best[document_id] = float(similarity)
    return list(best.items())[:limit]
