"""Grounded system + context string (parity with backend/src/chat/prompt.ts)."""

from __future__ import annotations

from app.knowledge.models import KnowledgeChunk
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

    history = (history or [])[-MAX_HISTORY_MESSAGES:]

    history_block = "\n".join(
        f"{'User' if msg.role == 'user' else 'Assistant'}: {msg.content}" for msg in history
    )
    history_section = history_block if history_block else "No prior conversation."

    return "\n".join(
        [
            "You are RadCrew's website assistant.",
            "Answer only using the conversation history and provided context sources.",
            "For team-member questions, prioritize team profile details found in the loaded knowledge context (including GitHub markdown and Contentful entries).",
            "For team-member answers, use Contentful engineer entries for short summary fields (name and role) and GitHub markdown files for detailed profile information.",
            "Treat the first line of each GitHub team markdown file as the canonical team-member name.",
            "When listing team members, include only people explicitly present in the context.",
            "Do not infer person names from source titles or file names; use names explicitly written in the source content.",
            "If both history and context sources are insufficient, say you do not have enough information and suggest emailing code@radcrew.org.",
            "Keep answers consistent, factual, concise, helpful, and accurate.",
            "Answer as briefly as possible and do not add extra details unless the user explicitly asks for them.",
            "For direct questions, respond with a direct sentence only (for example: 'Someone developed sth.').",
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
            "Format the answer in simple Markdown for readability (use bold labels and short bullet lists when helpful).",
            "Do not use '*' bullet symbols.",
            "Use '-' for list bullets, and keep nested lists as indented '+' items only when needed.",
            "Do not nest content deeper than 2 levels.",
            "Do not include URLs, links, href attributes, or markdown link syntax in the final answer.",
        ]
    )
