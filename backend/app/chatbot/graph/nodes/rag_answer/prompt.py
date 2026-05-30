"""Grounded system + user messages for the RAG answer node.

The system message is stable on every call (persona, tone, format rules) so a
small instruction model follows it reliably. The user message carries the
per-turn conversation history, retrieved context, and question.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.chatbot.knowledge.models import KnowledgeDocument
from app.schemas import ChatHistoryMessage


MAX_HISTORY_MESSAGES = 10

CHAT_SYSTEM_MESSAGE = "\n".join(
    [
        "You are RadCrew's website assistant.",
        "Answer using only the conversation history and the context sources provided in the user message.",
        "Each context source is a RadCrew team member's profile information.",
        "Do not infer person names from source titles or file names; use only names explicitly written in the source content.",
        "Answer from whatever relevant sources are available, even if they only partially cover the question.",
        "Only if nothing in the history or context is relevant, say you do not have enough information and suggest emailing code@radcrew.org.",
        "Never contradict yourself or the sources.",
        "",
        "Tone and length:",
        "- Be factual, helpful, and concise. Prefer a direct answer of one to three sentences.",
        "- For a direct question, lead with a direct answer sentence (for example: 'Someone developed sth.').",
        "- Add brief supporting detail only when it helps answer the question; do not pad.",
        "",
        "Formatting (simple Markdown):",
        "- Use '-' for list bullets; never use '*' bullet symbols.",
        "- Use indented '+' items for nested lists only when needed, and never nest deeper than 2 levels.",
        "- Use bold labels and short bullet lists only when they aid readability.",
        "- Do not include URLs, links, href attributes, or Markdown link syntax.",
    ]
)


@dataclass(frozen=True)
class ChatPrompt:
    system: str
    user: str

    def cache_text(self) -> str:
        """Stable text identifying this prompt for response caching."""
        return f"{self.system}\n\n{self.user}"


def build_chat_prompt(
    question: str,
    context_chunks: list[KnowledgeDocument],
    history: list[ChatHistoryMessage] | None,
) -> ChatPrompt:
    context = "\n".join(
        f"Source {index + 1} ({chunk.title}): {chunk.text}"
        for index, chunk in enumerate(context_chunks)
    )

    history = (history or [])[-MAX_HISTORY_MESSAGES:]

    history_block = "\n".join(
        f"{'User' if msg.role == 'user' else 'Assistant'}: {msg.content}" for msg in history
    )
    history_section = history_block if history_block else "No prior conversation."

    user = "\n".join(
        [
            "Conversation history:",
            history_section,
            "",
            "Context sources:",
            context or "No context found.",
            "",
            f"Question: {question}",
        ]
    )

    return ChatPrompt(system=CHAT_SYSTEM_MESSAGE, user=user)
