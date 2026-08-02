"""Follow-up hints: catalog selection, top-up, and already-asked suppression."""

from __future__ import annotations

from app.chatbot.graph.nodes.rag_answer.hints import (
    DEFAULT_HINTS,
    HINT_CATALOG,
    MAX_HINTS,
    build_hints,
)
from app.chatbot.knowledge.models import KnowledgeDocument
from app.schemas import ChatHistoryMessage


def _document(doc_id: str) -> KnowledgeDocument:
    return KnowledgeDocument(id=doc_id, title=doc_id, text="")


def test_hints_come_from_retrieved_documents_in_rank_order() -> None:
    out = build_hints([_document("faq"), _document("contact")], "tell me about timelines")
    assert out[:2] == HINT_CATALOG["faq"]
    assert out[2] == HINT_CATALOG["contact"][0]


def test_short_catalog_tops_up_from_defaults() -> None:
    out = build_hints([_document("hero")], "who are you")
    assert out[:2] == HINT_CATALOG["hero"]
    assert len(out) == MAX_HINTS
    assert out[2] in DEFAULT_HINTS


def test_no_retrieved_documents_falls_back_to_defaults() -> None:
    assert build_hints([], "hey there") == DEFAULT_HINTS


def test_documents_without_catalog_entries_are_ignored() -> None:
    out = build_hints([_document("github:team/jesus.md")], "who is on the team")
    assert out == DEFAULT_HINTS


def test_duplicate_hints_are_dropped() -> None:
    # "stats" and "testimonial" both offer the client question; it appears once.
    out = build_hints([_document("stats"), _document("testimonial")], "any numbers")
    assert len(out) == len(set(out))
    assert out.count("What kind of clients do you work with?") == 1


def test_hint_matching_the_current_question_is_suppressed() -> None:
    out = build_hints([_document("faq")], "How quickly can you start?")
    assert "How quickly can you start?" not in out


def test_suppression_ignores_punctuation_and_casing() -> None:
    out = build_hints([_document("contact")], "how do i start a project")
    assert "How do I start a project?" not in out


def test_hint_already_asked_earlier_in_the_conversation_is_suppressed() -> None:
    history = [
        ChatHistoryMessage(role="user", content="Do you work with Rust?"),
        ChatHistoryMessage(role="assistant", content="Which frontend stack do you use?"),
    ]
    out = build_hints([_document("tech-stack")], "what about databases", history)
    # The user's own earlier question is dropped; our earlier reply is not a question
    # the user asked, so it must not suppress anything.
    assert "Do you work with Rust?" not in out
    assert "Which frontend stack do you use?" in out


def test_never_returns_more_than_the_cap() -> None:
    documents = [_document(doc_id) for doc_id in HINT_CATALOG]
    assert len(build_hints(documents, "tell me everything")) == MAX_HINTS


def test_catalog_hints_stay_inside_the_reply_contract() -> None:
    every_hint = [h for hints in HINT_CATALOG.values() for h in hints] + list(DEFAULT_HINTS)
    for hint in every_hint:
        assert hint.endswith(("?", ".")), hint
        assert len(hint) <= 60, hint
        assert "*" not in hint, hint
        assert not any(token in hint.lower() for token in ("http", "www.", ".org", ".com", "@")), hint
