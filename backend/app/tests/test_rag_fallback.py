"""rag_answer_node only triggers deep search when KB confidence is low."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from app.chatbot.graph.nodes.rag_answer import answer as answer_mod
from app.chatbot.knowledge.models import KnowledgeDocument
from app.schemas import ChatRequest

_MODULE = "app.chatbot.graph.nodes.rag_answer.answer"
_KB = [KnowledgeDocument(id="hero", title="RadCrew", text="RadCrew builds software.")]


def _run(confidence: float, available: bool, threshold: float = 0.30):
    state = {"body": ChatRequest(message="what is your github?"), "knowledge_chunks": _KB}

    settings = MagicMock()
    settings.DEEP_SEARCH_SIMILARITY_THRESHOLD = threshold

    web_doc = KnowledgeDocument(id="web-0", title="GitHub", text="github.com/radcrew")
    deep_search = MagicMock(return_value=[web_doc])

    with patch(f"{_MODULE}.get_settings", return_value=settings), patch(
        f"{_MODULE}.retrieve_with_confidence", return_value=(_KB, confidence)
    ), patch(f"{_MODULE}.is_deep_search_available", return_value=available), patch(
        f"{_MODULE}.deep_search_documents", deep_search
    ), patch(f"{_MODULE}.get_cached_response", return_value=None), patch(
        f"{_MODULE}.generate_answer", return_value=iter(["ok"])
    ):
        result = answer_mod.rag_answer_node(state)
        "".join(result["output_stream"])  # drain stream so caching/side effects run
    return deep_search


def test_deep_search_triggers_on_low_confidence() -> None:
    deep_search = _run(confidence=0.10, available=True)
    deep_search.assert_called_once()


def test_deep_search_skipped_on_high_confidence() -> None:
    deep_search = _run(confidence=0.80, available=True)
    deep_search.assert_not_called()


def test_deep_search_skipped_when_unavailable() -> None:
    deep_search = _run(confidence=0.10, available=False)
    deep_search.assert_not_called()
