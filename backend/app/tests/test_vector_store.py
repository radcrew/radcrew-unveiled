"""Vector store: SQL issued, freshness predicate, deletion, and fail-open behaviour.

Runs without a database. A fake connection stands in for psycopg, recording the
SQL and parameters, so the unit tests assert what is sent rather than what a
server does with it. The one test that needs a real Postgres skips unless
DATABASE_URL is set.
"""

from __future__ import annotations

import os
from contextlib import contextmanager
from unittest.mock import patch

import numpy as np
import pytest

from app.chatbot.knowledge import vector_store
from app.chatbot.knowledge.chunking import Chunk

_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


class FakeCursor:
    def __init__(self, rows: list | None = None, rowcount: int = 0) -> None:
        self.rows = rows or []
        self.rowcount = rowcount
        self.calls: list[tuple[str, object]] = []

    def __enter__(self) -> "FakeCursor":
        return self

    def __exit__(self, *_: object) -> None:
        return None

    def execute(self, sql: str, params: object = None) -> None:
        self.calls.append((sql, params))

    def executemany(self, sql: str, params: object = None) -> None:
        self.calls.append((sql, params))

    def fetchall(self) -> list:
        return self.rows


class FakeConnection:
    def __init__(self, cursor: FakeCursor) -> None:
        self._cursor = cursor

    def cursor(self) -> FakeCursor:
        return self._cursor


@contextmanager
def _fake_connection(cursor: FakeCursor):
    yield FakeConnection(cursor)


def _patched(cursor: FakeCursor):
    return patch.object(vector_store, "_connection", lambda: _fake_connection(cursor))


def _raising():
    @contextmanager
    def boom():
        raise RuntimeError("connection refused")
        yield  # pragma: no cover - generator marker

    return patch.object(vector_store, "_connection", boom)


def _chunk(document_id: str = "hero", index: int = 0, body: str = "text") -> Chunk:
    return Chunk(document_id=document_id, chunk_index=index, title="Title", body=body)


def _vectors(count: int) -> np.ndarray:
    return np.ones((count, 3), dtype="float32")


def test_chunk_hash_tracks_the_embedded_text() -> None:
    assert vector_store.chunk_hash(_chunk()) == vector_store.chunk_hash(_chunk())
    assert vector_store.chunk_hash(_chunk(body="a")) != vector_store.chunk_hash(_chunk(body="b"))


def test_vector_literal_is_pgvector_text_form() -> None:
    assert vector_store._vector_literal(np.array([0.5, -0.25], dtype="float32")) == "[0.5,-0.25]"


def test_ensure_schema_creates_extension_table_and_indexes() -> None:
    cursor = FakeCursor()
    with _patched(cursor):
        assert vector_store.ensure_schema() is True

    sql = cursor.calls[0][0]
    assert "CREATE EXTENSION IF NOT EXISTS vector" in sql
    assert "CREATE TABLE IF NOT EXISTS knowledge_chunk" in sql
    assert "USING hnsw (embedding vector_cosine_ops)" in sql
    assert f"vector({vector_store.EMBEDDING_DIMENSIONS})" in sql


def test_upsert_skips_unchanged_rows_and_refreshes_on_a_model_change() -> None:
    cursor = FakeCursor()
    with _patched(cursor):
        written = vector_store.upsert_chunks([_chunk()], _vectors(1), _MODEL)

    assert written == 1
    sql, rows = cursor.calls[0]
    assert "ON CONFLICT (document_id, chunk_index) DO UPDATE" in sql
    # Both halves of the freshness key: text alone would leave vectors stale
    # after a model swap, with every hash still matching.
    assert "content_hash <> EXCLUDED.content_hash" in sql
    assert "embedding_model <> EXCLUDED.embedding_model" in sql
    assert rows[0][6] == _MODEL


def test_upsert_sends_the_vector_as_a_bound_parameter() -> None:
    cursor = FakeCursor()
    with _patched(cursor):
        vector_store.upsert_chunks([_chunk()], _vectors(1), _MODEL)

    sql, rows = cursor.calls[0]
    assert "%s::vector" in sql  # cast in SQL, value bound, never interpolated
    assert rows[0][7] == "[1,1,1]"


def test_upsert_of_nothing_touches_no_connection() -> None:
    with _raising():
        assert vector_store.upsert_chunks([], _vectors(0), _MODEL) == 0


def test_fingerprints_key_on_document_and_chunk_index() -> None:
    cursor = FakeCursor(rows=[("hero", 0, "hash-a", _MODEL), ("faq", 1, "hash-b", _MODEL)])
    with _patched(cursor):
        assert vector_store.fingerprints() == {
            ("hero", 0): ("hash-a", _MODEL),
            ("faq", 1): ("hash-b", _MODEL),
        }


def test_delete_missing_removes_dropped_documents_and_trimmed_tails() -> None:
    cursor = FakeCursor(rowcount=2)
    with _patched(cursor):
        removed = vector_store.delete_missing({"hero": 1, "faq": 3})

    assert removed == 4  # rowcount counted once per statement
    dropped_documents, trimmed_tails = cursor.calls[0][0], cursor.calls[1][0]
    assert "document_id <> ALL" in dropped_documents
    assert "chunk_index >= keep.chunk_count" in trimmed_tails
    assert cursor.calls[1][1] == (["hero", "faq"], [1, 3])


def test_delete_missing_refuses_to_wipe_the_table_on_an_empty_corpus() -> None:
    """An empty corpus is a failed load far more often than an intentional wipe.

    `document_id <> ALL('{}')` matches every row, and the store holds the only
    copy of the vectors.
    """
    with _raising():
        assert vector_store.delete_missing({}) == 0


def test_search_returns_the_best_chunk_per_document_in_rank_order() -> None:
    # Rows arrive best first; "hero" appears twice because two of its chunks matched.
    cursor = FakeCursor(rows=[("hero", 0.91), ("faq", 0.72), ("hero", 0.55), ("contact", 0.40)])
    with _patched(cursor):
        results = vector_store.search(np.ones(3, dtype="float32"), limit=3)

    assert results == [("hero", 0.91), ("faq", 0.72), ("contact", 0.40)]


def test_search_overfetches_so_one_document_cannot_crowd_out_the_rest() -> None:
    cursor = FakeCursor(rows=[])
    with _patched(cursor):
        vector_store.search(np.ones(3, dtype="float32"), limit=5)

    sql, params = cursor.calls[0]
    assert params[2] == 5 * vector_store.OVERFETCH_FACTOR
    # Ordering on the alias would discard the HNSW index and scan the table.
    assert "ORDER BY embedding <=> %s::vector" in sql


def test_search_honours_the_limit_after_collapsing() -> None:
    cursor = FakeCursor(rows=[("a", 0.9), ("b", 0.8), ("c", 0.7), ("d", 0.6)])
    with _patched(cursor):
        assert len(vector_store.search(np.ones(3, dtype="float32"), limit=2)) == 2


@pytest.mark.parametrize(
    "call",
    [
        lambda: vector_store.ensure_schema(),
        lambda: vector_store.fingerprints(),
        lambda: vector_store.search(np.ones(3, dtype="float32"), limit=3),
        lambda: vector_store.upsert_chunks([_chunk()], _vectors(1), _MODEL),
        lambda: vector_store.delete_missing({"hero": 1}),
        lambda: vector_store.is_available(),
    ],
)
def test_every_entry_point_fails_open(call) -> None:
    """An unreachable database degrades to lexical retrieval, it never raises."""
    with _raising():
        assert not call()


@pytest.mark.skipif(not os.getenv("DATABASE_URL"), reason="needs a live Postgres with pgvector")
def test_round_trip_against_a_real_database() -> None:
    vector_store.reset_pool()
    assert vector_store.ensure_schema() is True

    chunk = Chunk(document_id="test-doc", chunk_index=0, title="Test", body="RadCrew builds software.")
    vector = np.zeros(vector_store.EMBEDDING_DIMENSIONS, dtype="float32")
    vector[0] = 1.0

    assert vector_store.upsert_chunks([chunk], vector.reshape(1, -1), _MODEL) == 1
    assert ("test-doc", 0) in vector_store.fingerprints()

    results = vector_store.search(vector, limit=3)
    assert results and results[0][0] == "test-doc"
    assert results[0][1] == pytest.approx(1.0, abs=1e-3)

    # A non-empty corpus that excludes test-doc; an empty one is refused by design.
    vector_store.delete_missing({"kept-doc": 1})
    assert ("test-doc", 0) not in vector_store.fingerprints()
