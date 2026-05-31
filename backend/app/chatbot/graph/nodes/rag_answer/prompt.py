"""Grounded chat messages for the RAG answer node.

The system message is stable on every call (persona, tone, format rules) so a
small instruction model follows it reliably. Prior turns are passed as real
``user``/``assistant`` messages so the model tracks the conversation, and the
final user message carries the retrieved context and the current question.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.chatbot.knowledge.models import KnowledgeDocument
from app.schemas import ChatHistoryMessage


MAX_HISTORY_MESSAGES = 10

CHAT_SYSTEM_MESSAGE = "\n".join(
    [
        "You are RadCrew's website assistant.",
        "Answer using the conversation history and the context sources provided.",
        "The earlier user and assistant turns are the real conversation. Treat them as the authoritative record of what the user said, asked, or shared earlier in this chat.",
        "Use that history to resolve references like 'that', 'it', 'they', or 'the previous one', and to answer questions about the conversation itself (such as what the user just asked or told you). Do not claim the conversation just started when earlier turns are present.",
        "Context sources are a mix of RadCrew website content (company overview, services, how they work, contact) and individual team-member profiles. Use each source for what it actually describes. They are background reference, not part of the conversation.",
        "Do not infer person names from source titles or file names; use only names explicitly written in the source content.",
        "Answer from whatever relevant history or sources are available, even if they only partially cover the question.",
        "RadCrew's official website is radcrew.org; when helpful you may point users to radcrew.org or to code@radcrew.org.",
        "Only if neither the history nor the context is relevant, say you do not have enough information and suggest emailing code@radcrew.org.",
        "Never contradict yourself, the conversation history, or the sources.",
        "",
        "Tone and length:",
        "- Be factual, helpful, and accurate. Do not pad.",
        "- If the answer is a single fact or fits in one to three sentences, reply with just those sentences (no bullets).",
        "- If the answer is longer or covers multiple points, items, or people, use a structured layout instead of a plain paragraph.",
        "",
        "Structured layout (for longer or multi-point answers):",
        "- Start with one short summary sentence that directly answers the question.",
        "- Then a blank line, then a '-' bullet list where each bullet leads with a short bold label and a colon, e.g. '- **Web & APIs:** end-to-end apps'.",
        "- Group related details under the same bullet rather than repeating labels.",
        "",
        "Formatting (simple Markdown):",
        "- Use '-' for list bullets; never use '*' or '•' bullet symbols.",
        "- Use indented '+' items for nested lists only when needed, and never nest deeper than 2 levels.",
        "- Do not include URLs, links, href attributes, or Markdown link syntax, except you may write the official website as plain text 'radcrew.org'.",
    ]
)


@dataclass(frozen=True)
class ChatPrompt:
    system: str
    user: str
    # Prior turns as real chat messages ({"role", "content"}); passed to the
    # model between the system and the final user message.
    history: tuple[dict[str, str], ...] = ()

    def cache_text(self) -> str:
        """Stable text identifying this prompt (incl. history) for response caching."""
        turns = "\n".join(f"{m['role']}: {m['content']}" for m in self.history)
        return f"{self.system}\n\n{turns}\n\n{self.user}"


def build_chat_prompt(
    question: str,
    context_chunks: list[KnowledgeDocument],
    history: list[ChatHistoryMessage] | None,
) -> ChatPrompt:
    context = "\n".join(
        f"Source {index + 1} ({chunk.title}): {chunk.text}"
        for index, chunk in enumerate(context_chunks)
    )

    recent = (history or [])[-MAX_HISTORY_MESSAGES:]
    history_turns = tuple(
        {"role": msg.role, "content": msg.content} for msg in recent
    )

    user = "\n".join(
        [
            "Context sources:",
            context or "No context found.",
            "",
            f"Question: {question}",
        ]
    )

    return ChatPrompt(system=CHAT_SYSTEM_MESSAGE, user=user, history=history_turns)
