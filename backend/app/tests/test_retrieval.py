"""Retrieval: semantic primary, lexical keyword fallback."""

from __future__ import annotations

from unittest.mock import patch

from app.chatbot.knowledge.models import KnowledgeDocument
from app.chatbot.graph.nodes.rag_answer import retrieval
from app.chatbot.graph.nodes.rag_answer.retrieval import retrieve_relevant_documents


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
