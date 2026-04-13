from collections.abc import Iterator

from app.chatbot.graph.state import ChatState
from app.chatbot.rag.stream import stream_rag_chat_answer

def rag_answer_node(state: ChatState) -> dict[str, Iterator[str]]:
    return {
        "output_stream": stream_rag_chat_answer(
            state["body"],
            state["knowledge_chunks"],
        ),
    }
