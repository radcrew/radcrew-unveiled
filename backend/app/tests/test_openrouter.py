"""OpenRouter backend: provider selection, SSE parsing, and payload shape."""

from __future__ import annotations

import json
import urllib.error
from io import BytesIO
from unittest.mock import patch

import pytest

from app.chatbot import llm
from app.chatbot.openrouter import client as or_client
from app.core.settings import Settings


def _sse(*lines: str) -> BytesIO:
    return BytesIO("".join(f"{line}\n" for line in lines).encode("utf-8"))


def _chunk(content: str) -> str:
    return "data: " + json.dumps({"choices": [{"delta": {"content": content}}]})


# --------------------------------------------------------------------------
# Provider selection
# --------------------------------------------------------------------------


def test_provider_is_none_without_credentials() -> None:
    assert Settings(_env_file=None).llm_provider() == "none"


def test_provider_is_huggingface_with_only_hf_token() -> None:
    assert Settings(_env_file=None, HF_TOKEN="hf_x").llm_provider() == "huggingface"


def test_provider_is_openrouter_with_only_openrouter_key() -> None:
    assert Settings(_env_file=None, OPENROUTER_API_KEY="sk-or-x").llm_provider() == "openrouter"


def test_openrouter_wins_when_both_are_configured() -> None:
    """HF_TOKEN may be present purely to keep embeddings working."""
    settings = Settings(_env_file=None, HF_TOKEN="hf_x", OPENROUTER_API_KEY="sk-or-x")
    assert settings.llm_provider() == "openrouter"


# --------------------------------------------------------------------------
# Dispatch
# --------------------------------------------------------------------------


def test_generate_answer_dispatches_to_openrouter() -> None:
    with patch.object(llm, "active_provider", return_value="openrouter"), patch.object(
        llm, "_or_generate_answer", return_value=iter(["from openrouter"])
    ) as mock_or, patch.object(llm, "_hf_generate_answer") as mock_hf:
        assert "".join(llm.generate_answer("s", "u")) == "from openrouter"

    mock_or.assert_called_once()
    mock_hf.assert_not_called()


def test_generate_answer_dispatches_to_huggingface() -> None:
    with patch.object(llm, "active_provider", return_value="huggingface"), patch.object(
        llm, "_hf_generate_answer", return_value=iter(["from hf"])
    ) as mock_hf, patch.object(llm, "_or_generate_answer") as mock_or:
        assert "".join(llm.generate_answer("s", "u")) == "from hf"

    mock_hf.assert_called_once()
    mock_or.assert_not_called()


# --------------------------------------------------------------------------
# SSE stream parsing
# --------------------------------------------------------------------------


def test_stream_concatenates_content_deltas() -> None:
    response = _sse(_chunk("Hello "), _chunk("there."), "data: [DONE]")

    with patch.object(or_client, "_open", return_value=response):
        out = "".join(or_client.stream_chat_completion([{"role": "user", "content": "hi"}]))

    assert out == "Hello there."


def test_stream_skips_keepalive_comments_and_bad_json() -> None:
    """OpenRouter emits ': OPENROUTER PROCESSING' lines to hold the connection."""
    response = _sse(
        ": OPENROUTER PROCESSING",
        _chunk("ok"),
        "data: {not json",
        "",
        "data: [DONE]",
    )

    with patch.object(or_client, "_open", return_value=response):
        out = "".join(or_client.stream_chat_completion([{"role": "user", "content": "hi"}]))

    assert out == "ok"


def test_stream_stops_at_done_sentinel() -> None:
    response = _sse(_chunk("kept"), "data: [DONE]", _chunk("after done"))

    with patch.object(or_client, "_open", return_value=response):
        out = "".join(or_client.stream_chat_completion([{"role": "user", "content": "hi"}]))

    assert out == "kept"


# --------------------------------------------------------------------------
# Request shape
# --------------------------------------------------------------------------


def test_generate_answer_builds_system_history_user_order() -> None:
    from app.chatbot import openrouter

    captured: dict[str, object] = {}

    def fake_stream(messages, *_args, **_kwargs):
        captured["messages"] = messages
        return iter([])

    with patch.object(openrouter, "stream_chat_completion", fake_stream):
        list(openrouter.generate_answer("sys", "now", [{"role": "user", "content": "before"}]))

    assert captured["messages"] == [
        {"role": "system", "content": "sys"},
        {"role": "user", "content": "before"},
        {"role": "user", "content": "now"},
    ]


def test_complete_json_sends_strict_schema_and_returns_content() -> None:
    body = json.dumps({"choices": [{"message": {"content": '{"intent":"question"}'}}]})
    captured: dict[str, object] = {}

    def fake_open(payload):
        captured["payload"] = payload
        return BytesIO(body.encode("utf-8"))

    with patch.object(or_client, "_open", fake_open):
        out = or_client.complete_json(
            [{"role": "user", "content": "hi"}],
            "routing_reply",
            "Label the intent.",
            {"type": "object"},
        )

    assert out == '{"intent":"question"}'
    payload = captured["payload"]
    assert payload["stream"] is False
    assert payload["response_format"]["json_schema"]["strict"] is True
    assert payload["response_format"]["json_schema"]["name"] == "routing_reply"


def test_stream_payload_requests_streaming_and_deterministic_decoding() -> None:
    captured: dict[str, object] = {}

    def fake_open(payload):
        captured["payload"] = payload
        return _sse("data: [DONE]")

    with patch.object(or_client, "_open", fake_open):
        list(or_client.stream_chat_completion([{"role": "user", "content": "hi"}]))

    payload = captured["payload"]
    assert payload["stream"] is True
    assert payload["temperature"] == 0


# --------------------------------------------------------------------------
# Failure surfacing
# --------------------------------------------------------------------------


def test_mid_stream_error_raises_instead_of_ending_silently() -> None:
    """OpenRouter answers 200 before the upstream provider is proven healthy.

    An error arriving as a stream payload must not close the stream cleanly and
    hand the caller a blank answer.
    """
    payload = "data: " + json.dumps({"error": {"message": "Provider returned error"}})
    response = _sse(payload, "data: [DONE]")

    with patch.object(or_client, "_open", return_value=response):
        with pytest.raises(RuntimeError, match="Provider returned error"):
            "".join(or_client.stream_chat_completion([{"role": "user", "content": "hi"}]))


def test_http_error_body_is_kept_in_the_message() -> None:
    """urllib's own message omits the body, which is the part that says why."""
    def raising_open(*_args, **_kwargs):
        raise urllib.error.HTTPError(
            url="https://openrouter.ai/api/v1/chat/completions",
            code=402,
            msg="Payment Required",
            hdrs=None,
            fp=BytesIO(b'{"error":{"message":"Insufficient credits"}}'),
        )

    with patch.object(or_client.urllib.request, "urlopen", side_effect=raising_open):
        with pytest.raises(RuntimeError, match="Insufficient credits"):
            list(or_client.stream_chat_completion([{"role": "user", "content": "hi"}]))
