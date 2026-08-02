"""Put the corpus into the vector store: chunk, diff, embed what changed, upsert.

This is the whole point of the store. The in-process cache re-embeds everything
on every start; here a boot reads the stored fingerprints, embeds only the
chunks whose text or embedding model differs, and normally writes nothing at
all.

Runs at startup (``core/lifespan.py``) and on demand:

    python -m app.chatbot.knowledge.indexing [--force]
"""

from __future__ import annotations

import argparse
import logging
from collections import Counter
from dataclasses import dataclass

from app.chatbot.knowledge import vector_store
from app.chatbot.knowledge.chunking import chunk_documents
from app.chatbot.knowledge.embeddings import embed_batched
from app.chatbot.knowledge.models import KnowledgeDocument
from app.core.settings import get_settings

logger = logging.getLogger(__name__)

# Whether the last indexing run left the store usable. /health reports this
# rather than probing the database, so a public endpoint stays free of queries.
_last_index_ok = False


@dataclass(frozen=True)
class IndexReport:
    chunks: int = 0
    embedded: int = 0
    deleted: int = 0
    ok: bool = False


def last_index_ok() -> bool:
    return _last_index_ok


def index_corpus(documents: list[KnowledgeDocument], force: bool = False) -> IndexReport:
    """Bring the store in line with the loaded corpus.

    ``force`` re-embeds everything, for recovering from a half-finished run or a
    model change that the fingerprints somehow missed.
    """
    global _last_index_ok
    _last_index_ok = False

    if not vector_store.ensure_schema():
        return IndexReport()

    chunks = chunk_documents(documents)
    if not chunks:
        # Deleting on an empty corpus is refused downstream, and rightly: this
        # is a failed load far more often than an emptied knowledge base.
        logger.warning("[indexing] no chunks to index; leaving the store untouched")
        return IndexReport()

    model = get_settings().HUGGINGFACE_EMBEDDING_MODEL
    stored = {} if force else vector_store.fingerprints()
    stale = [
        chunk
        for chunk in chunks
        if stored.get((chunk.document_id, chunk.chunk_index))
        != (vector_store.chunk_hash(chunk), model)
    ]

    embedded = 0
    if stale:
        vectors = embed_batched([chunk.embed_text for chunk in stale])
        if vectors is None:
            # No credit, no token, or an unreachable provider. Whatever is
            # already stored still serves retrieval, so keep it and report the
            # run as failed rather than half-applying it.
            logger.error("[indexing] embedding failed; keeping the existing vectors")
            return IndexReport(chunks=len(chunks))
        urls = {document.id: document.url for document in documents}
        embedded = vector_store.upsert_chunks(stale, vectors, model, urls)

    deleted = vector_store.delete_missing(Counter(chunk.document_id for chunk in chunks))

    _last_index_ok = True
    logger.info(
        "[indexing] chunks=%d embedded=%d deleted=%d", len(chunks), embedded, deleted
    )
    return IndexReport(chunks=len(chunks), embedded=embedded, deleted=deleted, ok=True)


def main() -> int:
    from app.chatbot.knowledge import get_static_site_documents
    from app.chatbot.knowledge.github_loader import get_resume_documents

    parser = argparse.ArgumentParser(description="Index the knowledge corpus into pgvector.")
    parser.add_argument("--force", action="store_true", help="re-embed every chunk")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

    settings = get_settings()
    if not settings.vector_store_enabled():
        logger.error("DATABASE_URL is not set; nothing to index into")
        return 1

    documents = [
        *get_static_site_documents(),
        *get_resume_documents(
            repo_url=settings.GITHUB_REPO_URL,
            token=settings.GITHUB_TOKEN,
            branch=settings.GITHUB_BRANCH,
            path_prefix=settings.GITHUB_PATH,
        ),
    ]
    report = index_corpus(documents, force=args.force)
    print(
        f"documents={len(documents)} chunks={report.chunks} "
        f"embedded={report.embedded} deleted={report.deleted} ok={report.ok}"
    )
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
