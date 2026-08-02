"""Retrieval: semantic primary, lexical keyword fallback, in memory or via pgvector."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import numpy as np

from app.chatbot.knowledge.models import KnowledgeDocument
from app.chatbot.graph.nodes.rag_answer import retrieval
from app.chatbot.graph.nodes.rag_answer.retrieval import (
    retrieve_relevant_documents,
    retrieve_with_confidence,
)


def _documents() -> list[KnowledgeDocument]:
    return [
        KnowledgeDocument(id="1", title="Ada Lovelace", text="Built the analytics dashboard."),
        KnowledgeDocument(id="2", title="Grace Hopper", text="Wrote the compiler service."),
        KnowledgeDocument(id="3", title="Alan Turing", text="Designed the chat backend."),
    ]


@patch.object(retrieval, "_semantic_similarities")
def test_semantic_results_used_when_above_threshold(mock_sem) -> None:
    mock_sem.return_value = [0.1, 0.9, 0.2]
    out = retrieve_relevant_documents(_documents(), "who wrote the compiler", limit=2)
    assert [d.id for d in out] == ["2", "3"]  # ranked by semantic score, top 2


@patch.object(retrieval, "_semantic_similarities")
def test_lexical_fallback_rescues_name_question(mock_sem) -> None:
    # All semantic scores below the threshold → lexical fallback kicks in.
    mock_sem.return_value = [0.05, 0.05, 0.05]
    out = retrieve_relevant_documents(_documents(), "what did Ada Lovelace build?", limit=2)
    assert out[0].id == "1"  # name matches the title


@patch.object(retrieval, "_semantic_similarities")
def test_returns_empty_when_nothing_matches(mock_sem) -> None:
    mock_sem.return_value = [0.0, 0.0, 0.0]
    out = retrieve_relevant_documents(_documents(), "zzz qqq", limit=2)
    assert out == []


_MODULE = "app.chatbot.graph.nodes.rag_answer.retrieval"


def _store_settings() -> MagicMock:
    settings = MagicMock()
    settings.vector_store_enabled.return_value = True
    settings.RETRIEVAL_FALLBACK_SIMILARITY_THRESHOLD = 0.25
    return settings


def _with_store(hits: list[tuple[str, float]]):
    """Patch the store path: query embedding available, search returning `hits`."""
    return (
        patch(f"{_MODULE}.get_settings", return_value=_store_settings()),
        patch(f"{_MODULE}.embed_query", return_value=np.ones(3, dtype="float32")),
        patch(f"{_MODULE}.vector_store.search", return_value=hits),
    )


def test_store_results_resolve_to_documents_in_rank_order() -> None:
    settings, embed, search = _with_store([("3", 0.9), ("1", 0.6)])
    with settings, embed, search:
        out, confidence = retrieve_with_confidence(_documents(), "who wrote the compiler", limit=2)

    assert [d.id for d in out] == ["3", "1"]
    assert confidence == 0.9


def test_store_ids_with_no_matching_document_are_skipped() -> None:
    """A row can outlive the content it came from; it must not take a live slot."""
    settings, embed, search = _with_store([("gone", 0.95), ("2", 0.80)])
    with settings, embed, search:
        out, confidence = retrieve_with_confidence(_documents(), "compiler", limit=2)

    assert [d.id for d in out] == ["2"]
    assert confidence == 0.80


def test_store_failure_falls_back_to_lexical() -> None:
    # search() returns [] on any database error, which must read as "no semantic
    # signal" and hand over to keyword matching rather than answering nothing.
    settings, embed, search = _with_store([])
    with settings, embed, search:
        out, confidence = retrieve_with_confidence(_documents(), "Ada Lovelace", limit=2)

    assert out and out[0].id == "1"
    assert confidence == 0.0


def test_store_hits_below_the_threshold_fall_back_to_lexical() -> None:
    settings, embed, search = _with_store([("3", 0.10)])
    with settings, embed, search:
        out, confidence = retrieve_with_confidence(
            _documents(), "what did Ada Lovelace build?", limit=2
        )

    assert out[0].id == "1"  # lexical name match, not the weak semantic hit
    assert confidence == 0.10


def test_store_path_without_embeddings_falls_back_to_lexical() -> None:
    with patch(f"{_MODULE}.get_settings", return_value=_store_settings()), patch(
        f"{_MODULE}.embed_query", return_value=None
    ), patch(f"{_MODULE}.vector_store.search") as search:
        out, confidence = retrieve_with_confidence(_documents(), "Grace Hopper", limit=2)

    search.assert_not_called()  # no query vector, nothing to search with
    assert out[0].id == "2"
    assert confidence == 0.0
