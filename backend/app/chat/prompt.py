"""Grounded system + context string (parity with backend/src/chat/prompt.ts)."""

from __future__ import annotations

from app.models import KnowledgeChunk
from app.schemas import ChatHistoryMessage


MAX_HISTORY_MESSAGES = 10


def build_chat_prompt(
    question: str,
    context_chunks: list[KnowledgeChunk],
    history: list[ChatHistoryMessage] | None,
) -> str:
    context = "\n".join(
        f"Source {index + 1} ({chunk.title}): {chunk.text}"
        for index, chunk in enumerate(context_chunks)
    )

    history = history or []
    trimmed_history = [m for m in history if m.content]  # defensive; validators should already enforce
    if len(trimmed_history) > MAX_HISTORY_MESSAGES:
        trimmed_history = trimmed_history[-MAX_HISTORY_MESSAGES:]

    history_block = "\n".join(
        f"{'User' if msg.role == 'user' else 'Assistant'}: {msg.content}"
        for msg in trimmed_history
    )
    history_section = history_block if history_block else "No prior conversation."

    return "\n".join(
        [
            "You are RadCrew's website assistant.",
            "Answer only using the conversation history and provided context sources.",
            "For team-member questions, prioritize team profile details found in the loaded knowledge context (including GitHub markdown and Contentful entries).",
            "When listing team members, include only people explicitly present in the context.",
            "If both history and context sources are insufficient, say you do not have enough information and suggest emailing hello@radcrew.dev.",
            "Keep answers consistent, factual, concise, helpful, and accurate.",
            "Never contradict yourself.",
            "",
            "Conversation history:",
            history_section,
            "",
            "Context sources:",
            context or "No context found.",
            "",
            f"Question: {question}",
            "",
            "Respond in plain text.",
        ]
    )
