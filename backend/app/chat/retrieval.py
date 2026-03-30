"""Chunking and lexical overlap retrieval (parity with backend/src/chat/retrieval.ts)."""

from __future__ import annotations

import re

from app.models import KnowledgeChunk, KnowledgeChunkScored, KnowledgeDocument

TOKEN_RE = re.compile(r"[a-z0-9]+", re.IGNORECASE)
SENTENCE_SPLIT = re.compile(r"(?<=[.?!])\s+")

# Same threshold as backend/src/server.ts (`relevantChunks[0].score < 1.2`).
RETRIEVAL_FALLBACK_SCORE_THRESHOLD = 1.2


def tokenize(text: str) -> list[str]:
    return [t for t in TOKEN_RE.findall(text.lower()) if len(t) > 1]


def _chunk_document(doc: KnowledgeDocument) -> list[KnowledgeChunk]:
    sentence_chunks = [p.strip() for p in SENTENCE_SPLIT.split(doc.text) if p.strip()]

    if len(sentence_chunks) <= 2:
        return [
            KnowledgeChunk(
                id=f"{doc.id}:0",
                title=doc.title,
                text=doc.text,
                tokens=tokenize(doc.text),
                url=doc.url,
            )
        ]

    chunks: list[KnowledgeChunk] = []
    i = 0
    while i < len(sentence_chunks):
        pair = sentence_chunks[i : i + 2]
        chunk_text = " ".join(pair).strip()
        chunk_idx = i // 2
        chunks.append(
            KnowledgeChunk(
                id=f"{doc.id}:{chunk_idx}",
                title=doc.title,
                text=chunk_text,
                tokens=tokenize(chunk_text),
                url=doc.url,
            )
        )
        i += 2
    return chunks


def build_knowledge_chunks(documents: list[KnowledgeDocument]) -> list[KnowledgeChunk]:
    out: list[KnowledgeChunk] = []
    for doc in documents:
        for ch in _chunk_document(doc):
            if len(ch.tokens) > 0:
                out.append(ch)
    return out


def retrieve_relevant_chunks(
    chunks: list[KnowledgeChunk],
    query: str,
    limit: int = 5,
) -> list[KnowledgeChunkScored]:
    query_tokens = set(tokenize(query))
    if len(query_tokens) == 0:
        return []

    scored: list[KnowledgeChunkScored] = []
    for chunk in chunks:
        overlap = sum(1 for t in chunk.tokens if t in query_tokens)
        density = overlap / max(len(chunk.tokens), 1)
        score = overlap + density
        if score > 0:
            scored.append(
                KnowledgeChunkScored(
                    id=chunk.id,
                    title=chunk.title,
                    text=chunk.text,
                    tokens=chunk.tokens,
                    score=score,
                    url=chunk.url,
                )
            )

    # Stable tie-breaking keeps context ordering deterministic across runs.
    scored.sort(key=lambda c: (-c.score, c.id, c.title))
    return scored[:limit]


def retrieval_fallback_needed(chunks: list[KnowledgeChunkScored]) -> bool:
    """True when the chat handler should use the low-context fallback response."""
    return len(chunks) == 0 or chunks[0].score < RETRIEVAL_FALLBACK_SCORE_THRESHOLD
