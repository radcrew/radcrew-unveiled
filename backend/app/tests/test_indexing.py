"""Corpus indexing: embed only what changed, keep what is stored when a run fails."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import numpy as np

from app.chatbot.knowledge import indexing
from app.chatbot.knowledge.chunking import chunk_documents
from app.chatbot.knowledge.models import KnowledgeDocument

_MODULE = "app.chatbot.knowledge.indexing"
_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def _documents() -> list[KnowledgeDocument]:
    return [
        KnowledgeDocument(id="hero", title="Hero", text="RadCrew builds software.", url="/"),
        KnowledgeDocument(id="faq", title="FAQ", text="They start within two weeks."),
    ]


def _fingerprints_for(documents: list[KnowledgeDocument]) -> dict:
    """What the store would hold if the corpus were already indexed."""
    from app.chatbot.knowledge.vector_store import chunk_hash

    return {
        (chunk.document_id, chunk.chunk_index): (chunk_hash(chunk), _MODEL)
        for chunk in chunk_documents(documents)
    }


def _store(fingerprints: dict | None = None) -> MagicMock:
    store = MagicMock()
    store.ensure_schema.return_value = True
    store.fingerprints.return_value = fingerprints if fingerprints is not None else {}
    store.upsert_chunks.side_effect = lambda chunks, *_args, **_kw: len(chunks)
    store.delete_missing.return_value = 0
    from app.chatbot.knowledge.vector_store import chunk_hash

    store.chunk_hash = chunk_hash
    return store


def _run(store: MagicMock, embed_result, force: bool = False) -> indexing.IndexReport:
    settings = MagicMock(HUGGINGFACE_EMBEDDING_MODEL=_MODEL)
    with patch(f"{_MODULE}.vector_store", store), patch(
        f"{_MODULE}.embed_batched", return_value=embed_result
    ), patch(f"{_MODULE}.get_settings", return_value=settings):
        return indexing.index_corpus(_documents(), force=force)


def test_first_run_embeds_every_chunk() -> None:
    store = _store()
    report = _run(store, np.ones((2, 3), dtype="float32"))

    assert report.ok is True
    assert report.chunks == 2 and report.embedded == 2
    store.ensure_schema.assert_called_once()


def test_unchanged_corpus_embeds_nothing() -> None:
    """The whole point of the store: a boot that writes nothing."""
    store = _store(_fingerprints_for(_documents()))

    with patch(f"{_MODULE}.embed_batched") as embed:
        report = _run(store, None)

    embed.assert_not_called()
    store.upsert_chunks.assert_not_called()
    assert report.ok is True and report.embedded == 0


def test_a_changed_embedding_model_re_embeds_matching_text() -> None:
    # Same text, different model: hashes all match, every vector is stale.
    stored = {key: (digest, "some/other-model") for key, (digest, _) in _fingerprints_for(_documents()).items()}
    store = _store(stored)

    report = _run(store, np.ones((2, 3), dtype="float32"))

    assert report.embedded == 2


def test_force_re_embeds_even_when_nothing_changed() -> None:
    store = _store(_fingerprints_for(_documents()))
    report = _run(store, np.ones((2, 3), dtype="float32"), force=True)

    store.fingerprints.assert_not_called()
    assert report.embedded == 2


def test_failed_embedding_keeps_the_stored_vectors() -> None:
    """A depleted account must not empty the store; what is there still answers."""
    store = _store()
    report = _run(store, None)

    assert report.ok is False
    store.upsert_chunks.assert_not_called()
    store.delete_missing.assert_not_called()


def test_failed_schema_setup_stops_before_touching_anything() -> None:
    store = _store()
    store.ensure_schema.return_value = False

    report = _run(store, np.ones((2, 3), dtype="float32"))

    assert report.ok is False
    store.fingerprints.assert_not_called()


def test_empty_corpus_leaves_the_store_untouched() -> None:
    store = _store()
    settings = MagicMock(HUGGINGFACE_EMBEDDING_MODEL=_MODEL)

    with patch(f"{_MODULE}.vector_store", store), patch(
        f"{_MODULE}.get_settings", return_value=settings
    ):
        report = indexing.index_corpus([])

    assert report.ok is False
    store.delete_missing.assert_not_called()


def test_deletion_is_told_the_chunk_count_per_document() -> None:
    store = _store()
    _run(store, np.ones((2, 3), dtype="float32"))

    counts = store.delete_missing.call_args[0][0]
    assert counts == {"hero": 1, "faq": 1}


def test_last_index_ok_tracks_the_most_recent_run() -> None:
    assert _run(_store(), np.ones((2, 3), dtype="float32")).ok is True
    assert indexing.last_index_ok() is True

    _run(_store(), None)
    assert indexing.last_index_ok() is False
