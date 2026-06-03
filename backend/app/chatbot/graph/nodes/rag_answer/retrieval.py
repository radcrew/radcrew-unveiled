"""Knowledge indexing (one row per document) and retrieval.

Semantic retrieval (HF embeddings) is primary. When it finds nothing above the
similarity threshold, a lexical keyword fallback rescues name-based questions
("who is X", "what did X build") whose phrasing the embeddings miss but whose
terms appear verbatim in a profile title or body.
"""

from __future__ import annotations

import logging
import re

from app.chatbot.knowledge.embeddings import semantic_similarities
from app.chatbot.knowledge.models import KnowledgeDocument

logger = logging.getLogger(__name__)

# Best semantic similarity among returned docs; below this → try the lexical fallback.
RETRIEVAL_FALLBACK_SIMILARITY_THRESHOLD = 0.25

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


def query_matches_known_title(corpus: list[KnowledgeDocument], query: str) -> bool:
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
    return any(query_tokens & set(_tokenize(doc.title)) for doc in corpus)


def _semantic_similarities(corpus: list[KnowledgeDocument], query: str) -> list[float]:
    """Cosine of the query against the cached corpus vectors (query-only embed).

    Document vectors are embedded once at startup (see knowledge/embeddings.py);
    here we embed only the query and score locally. Returns zeros when embeddings
    are unavailable so the lexical fallback below still applies.
    """
    return semantic_similarities(corpus, query)


def _lexical_scores(corpus: list[KnowledgeDocument], query: str) -> list[float]:
    """Distinct-token overlap with each doc; title matches weighted over body."""
    query_tokens = set(_tokenize(query))
    if not query_tokens:
        return [0.0] * len(corpus)

    scores: list[float] = []
    for doc in corpus:
        title_hits = len(query_tokens & set(_tokenize(doc.title)))
        text_hits = len(query_tokens & set(_tokenize(doc.text)))
        scores.append(float(2 * title_hits + text_hits))
    return scores


def _top_documents(
    corpus: list[KnowledgeDocument],
    scores: list[float],
    limit: int,
) -> list[KnowledgeDocument]:
    ranked = sorted(enumerate(scores), key=lambda pair: -pair[1])
    positive = [(i, s) for i, s in ranked if s > 0.0]
    return [corpus[i] for i, _ in positive[:limit]]


def retrieve_with_confidence(
    corpus: list[KnowledgeDocument],
    query: str,
    limit: int = 8,
) -> tuple[list[KnowledgeDocument], float]:
    """Retrieve top docs and report a confidence score.

    Confidence is the best semantic similarity found (0.0–1.0). Callers use it to
    decide whether the knowledge base actually covers the question or a fallback
    (e.g. deep search) is warranted. When semantic retrieval is weak, results come
    from the lexical keyword fallback but confidence still reflects the (low)
    semantic signal.
    """
    semantic_scores = _semantic_similarities(corpus, query)
    semantic_ranked = sorted(enumerate(semantic_scores), key=lambda pair: -pair[1])
    positive = [(i, s) for i, s in semantic_ranked if s > 0.0]
    best_similarity = positive[0][1] if positive else 0.0

    if positive and best_similarity >= RETRIEVAL_FALLBACK_SIMILARITY_THRESHOLD:
        return [corpus[i] for i, _ in positive[:limit]], best_similarity

    # Semantic retrieval came up empty/weak — fall back to lexical keyword matching.
    return _top_documents(corpus, _lexical_scores(corpus, query), limit), best_similarity


def retrieve_relevant_chunks(
    corpus: list[KnowledgeDocument],
    query: str,
    limit: int = 8,
) -> list[KnowledgeDocument]:
    documents, _ = retrieve_with_confidence(corpus, query, limit)
    return documents
