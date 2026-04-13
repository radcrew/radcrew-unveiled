from unittest.mock import patch

from app.chatbot.rag.retrieval import (
    RETRIEVAL_FALLBACK_SIMILARITY_THRESHOLD,
    build_knowledge_chunks,
    retrieval_fallback_needed,
    retrieve_relevant_chunks,
)
from app.chatbot.knowledge.models import KnowledgeDocument


def test_one_chunk_per_document():
    doc = KnowledgeDocument(
        id="x",
        title="t",
        text="Only one sentence here.",
    )
    chunks = build_knowledge_chunks([doc])
    assert len(chunks) == 1
    assert chunks[0].id == "x:0"
    assert chunks[0].text == doc.text


def test_one_chunk_per_document_keeps_full_text():
    text = "First sentence here. Second one follows. Third is last."
    doc = KnowledgeDocument(id="d", title="T", text=text)
    chunks = build_knowledge_chunks([doc])
    assert len(chunks) == 1
    assert chunks[0].text == text


def test_skips_empty_text_documents():
    doc = KnowledgeDocument(id="e", title="E", text="   ")
    assert build_knowledge_chunks([doc]) == []


@patch("app.chatbot.rag.retrieval._semantic_similarities")
def test_retrieve_sorts_by_similarity_and_respects_limit(mock_sim: object) -> None:
    docs = [
        KnowledgeDocument(id="a", title="A", text="alpha beta gamma delta."),
        KnowledgeDocument(id="b", title="B", text="unrelated text."),
    ]
    mock_sim.return_value = [0.9, 0.1]
    corpus = build_knowledge_chunks(docs)
    out, top = retrieve_relevant_chunks(corpus, "alpha beta", limit=1)
    assert len(out) == 1
    assert out[0].title == "A"
    assert top == 0.9


@patch("app.chatbot.rag.retrieval._semantic_similarities")
def test_retrieve_empty_when_no_positive_scores(mock_sim: object) -> None:
    doc = KnowledgeDocument(id="a", title="A", text="hello world.")
    mock_sim.return_value = [0.0]
    corpus = build_knowledge_chunks([doc])
    out, top = retrieve_relevant_chunks(corpus, "hello", limit=5)
    assert out == []
    assert top == 0.0


def test_retrieve_empty_when_query_blank() -> None:
    doc = KnowledgeDocument(id="a", title="A", text="hello world.")
    corpus = build_knowledge_chunks([doc])
    out, top = retrieve_relevant_chunks(corpus, "   ", limit=5)
    assert out == []
    assert top == 0.0


def test_retrieval_fallback_threshold() -> None:
    assert retrieval_fallback_needed(0.0) is True
    assert retrieval_fallback_needed(0.34) is True
    assert retrieval_fallback_needed(RETRIEVAL_FALLBACK_SIMILARITY_THRESHOLD) is False
    assert retrieval_fallback_needed(0.99) is False
