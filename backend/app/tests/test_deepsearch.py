"""Deep search web-search fallback: availability, parsing, graceful failure."""

from __future__ import annotations

import io
import json
import urllib.error
from unittest.mock import MagicMock, patch

from app.chatbot.deepsearch import deep_search_documents, is_deep_search_available
from app.chatbot.deepsearch.web_search import _results_to_documents


def _settings(**overrides):
    s = MagicMock()
    s.DEEP_SEARCH_ENABLED = overrides.get("enabled", True)
    s.WEB_SEARCH_API_KEY = overrides.get("api_key", "test-key")
    s.WEB_SEARCH_PROVIDER = overrides.get("provider", "tavily")
    s.WEB_SEARCH_MAX_RESULTS = overrides.get("max_results", 5)
    return s


def test_unavailable_without_api_key() -> None:
    with patch("app.chatbot.deepsearch.web_search.get_settings", return_value=_settings(api_key=None)):
        assert is_deep_search_available() is False
        assert deep_search_documents("anything") == []


def test_unavailable_when_disabled() -> None:
    with patch("app.chatbot.deepsearch.web_search.get_settings", return_value=_settings(enabled=False)):
        assert is_deep_search_available() is False


def test_blank_query_returns_empty() -> None:
    with patch("app.chatbot.deepsearch.web_search.get_settings", return_value=_settings()):
        assert deep_search_documents("   ") == []


def test_results_to_documents_filters_and_maps() -> None:
    docs = _results_to_documents(
        [
            {"title": "RadCrew", "content": "We build software.", "url": "https://radcrew.org"},
            {"title": "no content", "content": "  ", "url": "https://x.com"},  # dropped
            "not a dict",  # dropped
            {"content": "Title missing is fine."},
        ]
    )
    assert [d.title for d in docs] == ["RadCrew", "Web result"]
    assert docs[0].url == "https://radcrew.org"
    assert docs[1].text == "Title missing is fine."


def test_tavily_success_returns_documents() -> None:
    body = json.dumps(
        {"results": [{"title": "GitHub", "content": "github.com/radcrew", "url": "https://github.com/radcrew"}]}
    ).encode("utf-8")
    fake_resp = io.BytesIO(body)
    fake_resp.__enter__ = lambda self=fake_resp: self  # type: ignore[attr-defined]
    fake_resp.__exit__ = lambda *a: False  # type: ignore[attr-defined]

    with patch("app.chatbot.deepsearch.web_search.get_settings", return_value=_settings()), patch(
        "app.chatbot.deepsearch.web_search.urllib.request.urlopen", return_value=fake_resp
    ):
        docs = deep_search_documents("what is radcrew's github?")

    assert len(docs) == 1
    assert "github.com/radcrew" in docs[0].text


def test_network_error_degrades_to_empty() -> None:
    with patch("app.chatbot.deepsearch.web_search.get_settings", return_value=_settings()), patch(
        "app.chatbot.deepsearch.web_search.urllib.request.urlopen",
        side_effect=urllib.error.URLError("boom"),
    ):
        assert deep_search_documents("query") == []


def test_unknown_provider_returns_empty() -> None:
    with patch("app.chatbot.deepsearch.web_search.get_settings", return_value=_settings(provider="bogus")):
        assert deep_search_documents("query") == []
