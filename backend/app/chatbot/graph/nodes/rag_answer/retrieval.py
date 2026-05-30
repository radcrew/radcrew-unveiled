"""Knowledge indexing (one row per document) and retrieval.

Semantic retrieval (HF embeddings) is primary. When it finds nothing above the
similarity threshold, a lexical keyword fallback rescues name-based questions
("who is X", "what did X build") whose phrasing the embeddings miss but whose
terms appear verbatim in a profile title or body.
"""

from __future__ import annotations

import logging
import re

from huggingface_hub import InferenceClient

from app.chatbot.knowledge.models import KnowledgeDocument
from app.core.settings import get_settings

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


def _semantic_similarities(corpus: list[KnowledgeDocument], query: str) -> list[float]:
    settings = get_settings()
    token = settings.HF_TOKEN
    model = settings.HUGGINGFACE_EMBEDDING_MODEL
    provider = settings.HUGGINGFACE_EMBEDDING_PROVIDER

    if not corpus:
        return []

    if not token or not model:
        return [0.0] * len(corpus)

    client = InferenceClient(
        model=model,
        token=token,
        provider=provider,  # type: ignore[arg-type]
    )

    candidates = [f"{doc.title}\n{doc.text}" for doc in corpus]
    similarities = client.sentence_similarity(
        sentence=query,
        other_sentences=candidates,
        model=model,
    )
    return [max(0.0, float(s)) for s in similarities]


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


def retrieve_relevant_chunks(
    corpus: list[KnowledgeDocument],
    query: str,
    limit: int = 8,
) -> list[KnowledgeDocument]:
    semantic_scores = _semantic_similarities(corpus, query)
    semantic_ranked = sorted(enumerate(semantic_scores), key=lambda pair: -pair[1])
    positive = [(i, s) for i, s in semantic_ranked if s > 0.0]

    if positive and positive[0][1] >= RETRIEVAL_FALLBACK_SIMILARITY_THRESHOLD:
        return [corpus[i] for i, _ in positive[:limit]]

    # Semantic retrieval came up empty/weak — fall back to lexical keyword matching.
    return _top_documents(corpus, _lexical_scores(corpus, query), limit)
