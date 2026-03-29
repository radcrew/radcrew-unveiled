from app.chat.retrieval import (
    RETRIEVAL_FALLBACK_SCORE_THRESHOLD,
    build_knowledge_chunks,
    retrieval_fallback_needed,
    retrieve_relevant_chunks,
    tokenize,
)
from app.models import KnowledgeChunkScored, KnowledgeDocument


def test_tokenize_filters_single_character_tokens():
    assert tokenize("a bc de") == ["bc", "de"]


def test_chunk_single_block_when_few_sentences():
    doc = KnowledgeDocument(
        id="x",
        title="t",
        text="Only one sentence here.",
    )
    chunks = build_knowledge_chunks([doc])
    assert len(chunks) == 1
    assert chunks[0].id == "x:0"
    assert "sentence" in chunks[0].tokens


def test_chunk_pairs_sentences_when_many():
    text = "First sentence here. Second one follows. Third is last."
    doc = KnowledgeDocument(id="d", title="T", text=text)
    chunks = build_knowledge_chunks([doc])
    assert len(chunks) == 2
    assert chunks[0].text.startswith("First sentence")
    assert "Third" in chunks[1].text


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
    low = KnowledgeChunkScored(
        id="1",
        title="t",
        text="x",
        tokens=["hello"],
        score=1.19,
    )
    high = KnowledgeChunkScored(
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
