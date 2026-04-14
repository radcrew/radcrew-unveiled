"""Knowledge indexing (one row per document) and semantic retrieval (HF embeddings)."""

from __future__ import annotations

import logging

from huggingface_hub import InferenceClient

from app.chatbot.knowledge.models import KnowledgeDocument
from app.core.settings import get_settings

logger = logging.getLogger(__name__)

# Best semantic similarity among returned docs; below this → low-context fallback (no history).
RETRIEVAL_FALLBACK_SIMILARITY_THRESHOLD = 0.35


def _semantic_similarities(corpus: list[KnowledgeDocument], query: str) -> list[float]:
    settings = get_settings()
    token = settings.HUGGINGFACE_API_KEY
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


def build_knowledge_chunks(documents: list[KnowledgeDocument]) -> list[KnowledgeDocument]:
    """One retrieval row per document (full body text; no sentence splitting)."""
    out: list[KnowledgeDocument] = []
    for doc in documents:
        if not doc.text.strip():
            continue
        out.append(
            KnowledgeDocument(
                id=f"{doc.id}:0",
                title=doc.title,
                text=doc.text,
                url=doc.url,
            )
        )
    return out


def retrieve_relevant_chunks(
    corpus: list[KnowledgeDocument],
    query: str,
    limit: int = 5,
) -> tuple[list[KnowledgeDocument], float]:
    scores = _semantic_similarities(corpus, query)

    ranked = sorted(enumerate(scores), key=lambda x: -x[1])
    positive = [(i, s) for i, s in ranked if s > 0.0]
    if not positive:
        return []

    top_pairs = positive[:limit]
    top_similarity = top_pairs[0][1]
    if top_similarity < RETRIEVAL_FALLBACK_SIMILARITY_THRESHOLD:
        return []

    out = [corpus[i] for i, _ in top_pairs]
    return out
