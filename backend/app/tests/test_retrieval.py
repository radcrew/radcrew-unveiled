from app.chatbot.rag.retrieval import (
    RETRIEVAL_FALLBACK_SCORE_THRESHOLD,
    build_knowledge_chunks,
    retrieval_fallback_needed,
    retrieve_relevant_chunks,
    tokenize,
)
from app.chatbot.knowledge.models import KnowledgeChunk, KnowledgeDocument


def test_tokenize_filters_single_character_tokens():
    assert tokenize("a bc de") == ["bc", "de"]


def test_one_chunk_per_document():
    doc = KnowledgeDocument(
        id="x",
        title="t",
        text="Only one sentence here.",
    )
    chunks = build_knowledge_chunks([doc])
    assert len(chunks) == 1
    assert chunks[0].id == "x:0"
    assert chunks[0].score is None
    assert "sentence" in chunks[0].tokens


def test_one_chunk_per_document_keeps_full_text():
    text = "First sentence here. Second one follows. Third is last."
    doc = KnowledgeDocument(id="d", title="T", text=text)
    chunks = build_knowledge_chunks([doc])
    assert len(chunks) == 1
    assert chunks[0].text == text
    assert "first" in chunks[0].tokens and "third" in chunks[0].tokens


def test_retrieve_sorts_by_score_and_respects_limit():
    docs = [
        KnowledgeDocument(id="a", title="A", text="alpha beta gamma delta."),
        KnowledgeDocument(id="b", title="B", text="unrelated text."),
    ]
    chunks = build_knowledge_chunks(docs)
    out = retrieve_relevant_chunks(chunks, "alpha beta", limit=1)
    assert len(out) == 1
    assert out[0].title == "A"


def test_retrieve_empty_when_query_has_no_tokens():
    doc = KnowledgeDocument(id="a", title="A", text="hello world.")
    chunks = build_knowledge_chunks([doc])
    assert retrieve_relevant_chunks(chunks, "a") == []


def test_retrieval_fallback_threshold_boundary():
    low = KnowledgeChunk(
        id="1",
        title="t",
        text="x",
        tokens=["hello"],
        score=1.19,
    )
    high = KnowledgeChunk(
        id="2",
        title="t",
        text="x",
        tokens=["hello"],
        score=1.2,
    )
    assert retrieval_fallback_needed([low]) is True
    assert retrieval_fallback_needed([high]) is False
    assert retrieval_fallback_needed([]) is True
    assert RETRIEVAL_FALLBACK_SCORE_THRESHOLD == 1.2
