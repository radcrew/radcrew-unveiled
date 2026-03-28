"""Grounded system + context string (parity with backend/src/chat/prompt.ts)."""

from __future__ import annotations

from app.models import KnowledgeChunk


def build_chat_prompt(question: str, context_chunks: list[KnowledgeChunk]) -> str:
    context = "\n".join(
        f"Source {index + 1} ({chunk.title}): {chunk.text}"
        for index, chunk in enumerate(context_chunks)
    )

    return "\n".join(
        [
            "You are RadCrew's website assistant.",
            "Answer only using the provided sources.",
            "If the sources are insufficient, say you do not have enough information and suggest emailing hello@radcrew.dev.",
            "Keep answers concise, helpful, and accurate.",
            "",
            "Context sources:",
            context or "No context found.",
            "",
            f"Question: {question}",
            "",
            "Respond in plain text.",
        ]
    )
