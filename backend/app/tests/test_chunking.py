"""Chunking: short documents unchanged, long ones split coherently and overlapped."""

from __future__ import annotations

from app.chatbot.knowledge.chunking import (
    MAX_CHUNK_CHARS,
    OVERLAP_CHARS,
    chunk_document,
    chunk_documents,
)
from app.chatbot.knowledge.models import KnowledgeDocument
from app.chatbot.knowledge.site_content import get_static_site_documents


def _document(text: str, title: str = "Title", doc_id: str = "doc") -> KnowledgeDocument:
    return KnowledgeDocument(id=doc_id, title=title, text=text)


def test_short_document_embeds_exactly_as_before() -> None:
    # The pre-chunking behaviour was to embed f"{title}\n{text}". Short documents
    # must still produce that byte for byte, or every stored score shifts.
    document = _document("RadCrew builds software.")
    chunks = chunk_document(document)

    assert len(chunks) == 1
    assert chunks[0].embed_text == f"{document.title}\n{document.text}"
    assert chunks[0].chunk_index == 0


def test_every_static_site_document_stays_a_single_chunk() -> None:
    """The static corpus is inside the model's limit, so chunking must not touch it."""
    for document in get_static_site_documents():
        assert len(chunk_document(document)) == 1, document.id


def test_blank_document_yields_no_chunks() -> None:
    # An embedding of "" is a meaningless vector that still matches queries.
    assert chunk_document(_document("   \n\n  ")) == []


def test_long_document_splits_at_headings() -> None:
    section = "word " * 60  # ~300 chars each, so headings decide the split
    text = "\n\n".join(f"# Heading {i}\n\n{section}" for i in range(6))
    chunks = chunk_document(_document(text))

    assert len(chunks) > 1
    # A chunk starts at a heading rather than mid-sentence.
    assert chunks[0].body.startswith("# Heading 0")


def test_many_short_sections_pack_together_instead_of_one_chunk_each() -> None:
    """Packing runs across sections, not within them.

    A document of many short headed sections must not become one tiny chunk per
    heading: that spends an embedding per heading and leaves passages too small
    to carry meaning.
    """
    text = "\n\n".join(
        f"## Engagement {i}\n\nDelivered a production system for client {i}, "
        "covering architecture, delivery and handover."
        for i in range(12)
    )
    chunks = chunk_document(_document(text))

    assert len(chunks) <= 4
    # Filling to the budget means most chunks carry several sections.
    assert chunks[0].body.count("## Engagement") > 1


def test_no_chunk_exceeds_the_budget() -> None:
    text = "\n\n".join(f"Paragraph {i}. " + "filler " * 40 for i in range(40))
    for chunk in chunk_document(_document(text, title="A fairly long document title")):
        assert len(chunk.embed_text) <= MAX_CHUNK_CHARS


def test_an_oversized_paragraph_is_broken_on_word_boundaries() -> None:
    # One paragraph, no headings, no blank lines: the last-resort path.
    text = "supercalifragilistic " * 300
    chunks = chunk_document(_document(text))

    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk.embed_text) <= MAX_CHUNK_CHARS
        assert "supercalifragilistic" in chunk.body
        # Splitting on words never leaves a truncated token.
        assert not chunk.body.startswith("calif")


def test_consecutive_chunks_overlap() -> None:
    text = "\n\n".join(f"Paragraph number {i} about radcrew engineering work." for i in range(60))
    chunks = chunk_document(_document(text))

    assert len(chunks) > 1
    tail = chunks[0].body[-OVERLAP_CHARS:]
    assert any(word and word in chunks[1].body for word in tail.split("\n\n")[-1:])


def test_chunk_indexes_are_contiguous_and_stable() -> None:
    document = _document("\n\n".join(f"Paragraph {i} " + "text " * 40 for i in range(20)))

    first = chunk_document(document)
    second = chunk_document(document)

    assert [c.chunk_index for c in first] == list(range(len(first)))
    # Re-running must not churn ids, or every reindex rewrites every row.
    assert [(c.chunk_index, c.body) for c in first] == [(c.chunk_index, c.body) for c in second]


def test_chunk_documents_keeps_document_ids() -> None:
    documents = [_document("short one", doc_id="a"), _document("short two", doc_id="b")]
    assert [c.document_id for c in chunk_documents(documents)] == ["a", "b"]
