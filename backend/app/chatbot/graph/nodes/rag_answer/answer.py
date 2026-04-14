from collections.abc import Iterator

from app.chatbot.cache.response import (
    get_cached_response,
    prompt_cache_key,
    stream_answer_with_cache,
)
from app.chatbot.messages import MSG_FALLBACK_LOW_CONTEXT
from app.chatbot.graph.state import ChatState
from app.chatbot.utils import get_text_chunk_stream
from app.chatbot.huggingface import generate_answer
from .prompt import build_chat_prompt
from .retrieval import retrieve_relevant_chunks, retrieval_fallback_needed

def rag_answer_node(state: ChatState) -> dict[str, Iterator[str]]:
    body = state["body"]
    knowledge_chunks = state["knowledge_chunks"]

    message = body.message
    history = body.history or []
    recent_user_turns = [m.content for m in history if m.role == "user" and m.content]

    retrieval_query = message
    if recent_user_turns:
        recent_context = "\n".join(recent_user_turns[-2:])
        retrieval_query = f"{message}\n\nPrevious user context:\n{recent_context}"

    relevant_chunks, top_similarity = retrieve_relevant_chunks(
        knowledge_chunks,
        retrieval_query,
        5,
    )

    if retrieval_fallback_needed(top_similarity) and not history:
        return {"output_stream": get_text_chunk_stream(MSG_FALLBACK_LOW_CONTEXT)}

    prompt = build_chat_prompt(message, relevant_chunks, history)

    cache_key = prompt_cache_key(prompt)
    cached = get_cached_response(cache_key)
    if cached is not None:
        return {"output_stream": get_text_chunk_stream(cached)}

    return {
        "output_stream": stream_answer_with_cache(
            generate_answer(prompt),
            cache_key,
        )
    }