"""Knowledge indexing (one row per document) and retrieval.

Semantic retrieval (HF embeddings) is primary. When it finds nothing above the
similarity threshold, a lexical keyword fallback rescues name-based questions
("who is X", "what did X build") whose phrasing the embeddings miss but whose
terms appear verbatim in a profile title or body.

Semantic ranking comes from one of two places. With ``DATABASE_URL`` set it is a
pgvector query, which ranks chunks and returns document ids; otherwise it is the
in-process vector cache scoring the whole corpus locally. Both produce ranked
``(document, similarity)`` pairs, so the thresholds and the lexical fallback
below are shared and behave identically either way.
"""

from __future__ import annotations

import logging
import re

from app.chatbot.knowledge import vector_store
from app.chatbot.knowledge.embeddings import embed_query, semantic_similarities
from app.chatbot.knowledge.models import KnowledgeDocument
from app.core.settings import get_settings

logger = logging.getLogger(__name__)

_TOKEN_RE = re.compile(r"[a-z0-9]+")

# Common words that would otherwise create spurious lexical matches.
_STOPWORDS = frozenset(
    {
        "a", "an", "and", "any", "are", "as", "at", "be", "by", "can", "did",
        "do", "does", "for", "from", "has", "have", "how", "in", "is", "it",
        "its", "of", "on", "or", "tell", "that", "the", "their", "them", "they",
        "this", "to", "us", "was", "were", "what", "when", "where", "which",
        "who", "whom", "whose", "why", "will", "with", "you", "your", "me",
        "about", "give", "please", "could", "would",
    }
)


def _tokenize(text: str) -> list[str]:
    return [t for t in _TOKEN_RE.findall(text.lower()) if len(t) > 1 and t not in _STOPWORDS]


def query_matches_known_title(documents: list[KnowledgeDocument], query: str) -> bool:
    """True when a distinctive query token appears in any document title.

    Titles name the entities and topics the knowledge base explicitly covers
    (team members like "Jesus Monroig", plus "Services", "Technologies", and so
    on). A match means the KB already covers the question, so a web-search
    fallback would only inject off-topic noise — e.g. "who is Jesus?" matches the
    "Jesus Monroig" profile and must not pull general web results about a
    same-named public figure. Stopwords and one-character tokens are ignored, so
    only meaningful overlaps count.
    """
    query_tokens = set(_tokenize(query))
    if not query_tokens:
        return False
    return any(query_tokens & set(_tokenize(doc.title)) for doc in documents)


def _semantic_similarities(documents: list[KnowledgeDocument], query: str) -> list[float]:
    """Cosine of the query against the cached document vectors (query-only embed).

    Document vectors are embedded once at startup (see knowledge/embeddings.py);
    here we embed only the query and score locally. Returns zeros when embeddings
    are unavailable so the lexical fallback below still applies.
    """
    return semantic_similarities(documents, query)


def _lexical_scores(documents: list[KnowledgeDocument], query: str) -> list[float]:
    """Distinct-token overlap with each doc; title matches weighted over body."""
    query_tokens = set(_tokenize(query))
    if not query_tokens:
        return [0.0] * len(documents)

    scores: list[float] = []
    for doc in documents:
        title_hits = len(query_tokens & set(_tokenize(doc.title)))
        text_hits = len(query_tokens & set(_tokenize(doc.text)))
        scores.append(float(2 * title_hits + text_hits))
    return scores


def _top_documents(
    documents: list[KnowledgeDocument],
    scores: list[float],
    limit: int,
) -> list[KnowledgeDocument]:
    ranked = sorted(enumerate(scores), key=lambda pair: -pair[1])
    positive = [(i, s) for i, s in ranked if s > 0.0]
    return [documents[i] for i, _ in positive[:limit]]


def _ranked_from_memory(
    documents: list[KnowledgeDocument],
    query: str,
) -> list[tuple[KnowledgeDocument, float]]:
    """Rank the whole corpus against the in-process vector cache."""
    scores = _semantic_similarities(documents, query)
    ranked = sorted(enumerate(scores), key=lambda pair: -pair[1])
    return [(documents[i], score) for i, score in ranked if score > 0.0]


def _ranked_from_store(
    documents: list[KnowledgeDocument],
    query: str,
    limit: int,
) -> list[tuple[KnowledgeDocument, float]]:
    """Rank via pgvector, resolving the returned document ids against the corpus.

    Ids that no longer match a loaded document are skipped rather than raising:
    the store can hold rows for content that has since left the corpus, and a
    stale row must not take a slot away from a live one.
    """
    query_vector = embed_query(query)
    if query_vector is None:
        return []

    by_id = {document.id: document for document in documents}
    return [
        (by_id[document_id], score)
        for document_id, score in vector_store.search(query_vector, limit)
        if document_id in by_id and score > 0.0
    ]


def retrieve_with_confidence(
    documents: list[KnowledgeDocument],
    query: str,
    limit: int = 8,
) -> tuple[list[KnowledgeDocument], float]:
    """Retrieve the top documents and report a confidence score.

    Confidence is the best semantic similarity found (0.0–1.0). Callers use it to
    decide whether the knowledge base actually covers the question or a fallback
    (e.g. deep search) is warranted. When semantic retrieval is weak, results come
    from the lexical keyword fallback but confidence still reflects the (low)
    semantic signal.
    """
    if get_settings().vector_store_enabled():
        ranked = _ranked_from_store(documents, query, limit)
    else:
        ranked = _ranked_from_memory(documents, query)

    best_similarity = ranked[0][1] if ranked else 0.0

    fallback_threshold = get_settings().RETRIEVAL_FALLBACK_SIMILARITY_THRESHOLD
    if ranked and best_similarity >= fallback_threshold:
        return [document for document, _ in ranked[:limit]], best_similarity

    # Semantic retrieval came up empty/weak — fall back to lexical keyword matching.
    return _top_documents(documents, _lexical_scores(documents, query), limit), best_similarity


def retrieve_relevant_documents(
    documents: list[KnowledgeDocument],
    query: str,
    limit: int = 8,
) -> list[KnowledgeDocument]:
    retrieved, _ = retrieve_with_confidence(documents, query, limit)
    return retrieved
