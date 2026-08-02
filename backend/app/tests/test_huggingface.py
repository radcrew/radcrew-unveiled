from unittest.mock import MagicMock, patch

import pytest
from collections.abc import Iterator

from app.chatbot.huggingface import generate_answer


def _collect_stream(chunks: Iterator[str]) -> str:
    return "".join(chunks)


@patch("app.chatbot.huggingface.generate.stream_text_generation")
@patch("app.chatbot.huggingface.generate.stream_chat_completion")
def test_generate_answer_returns_chat_completion_text(
    mock_chat: MagicMock, mock_tg: MagicMock
) -> None:
    mock_chat.return_value = iter(["  Answer", " from chat.  "])

    result = _collect_stream(generate_answer("system text", "prompt text"))

    assert result == "  Answer from chat.  "
    assert mock_chat.call_count >= 1
    mock_tg.assert_not_called()


@patch("app.chatbot.huggingface.generate.stream_text_generation")
@patch("app.chatbot.huggingface.generate.stream_chat_completion")
def test_generate_answer_falls_back_to_text_generation(
    mock_chat: MagicMock, mock_tg: MagicMock
) -> None:
    mock_chat.return_value = iter([])
    mock_tg.return_value = iter(["  From text gen.  "])

    result = _collect_stream(generate_answer("s", "p"))

    assert result == "  From text gen.  "
    mock_tg.assert_called()


def _raising_stream(err: Exception, before: list[str] | None = None) -> Iterator[str]:
    yield from (before or [])
    raise err


@patch("app.chatbot.huggingface.generate.sleep")
@patch("app.chatbot.huggingface.generate.stream_text_generation")
@patch("app.chatbot.huggingface.generate.stream_chat_completion")
def test_generate_answer_retries_chat_completion_after_a_transient_failure(
    mock_chat: MagicMock, mock_tg: MagicMock, mock_sleep: MagicMock
) -> None:
    # A blip before any content is exactly what a retry should absorb, rather
    # than falling through to text-generation and failing the whole answer.
    mock_chat.side_effect = [
        _raising_stream(RuntimeError("502 Bad Gateway")),
        iter(["Answer on the retry."]),
    ]

    result = _collect_stream(generate_answer("s", "p"))

    assert result == "Answer on the retry."
    assert mock_chat.call_count == 2
    mock_sleep.assert_called_once()
    mock_tg.assert_not_called()


@patch("app.chatbot.huggingface.generate.sleep")
@patch("app.chatbot.huggingface.generate.stream_text_generation")
@patch("app.chatbot.huggingface.generate.stream_chat_completion")
def test_generate_answer_does_not_retry_after_partial_output(
    mock_chat: MagicMock, mock_tg: MagicMock, mock_sleep: MagicMock
) -> None:
    # Those words are already on the wire to the browser. Retrying would append a
    # second answer to the partial one.
    mock_chat.side_effect = [
        _raising_stream(RuntimeError("connection reset"), before=["Half an "]),
        iter(["A whole second answer."]),
    ]

    result = _collect_stream(generate_answer("s", "p"))

    assert result == "Half an "
    assert mock_chat.call_count == 1
    mock_tg.assert_not_called()


def _http_error(status: int, message: str) -> Exception:
    """An exception shaped like huggingface_hub's, which carries `.response.status_code`."""
    err = RuntimeError(message)
    err.response = MagicMock(status_code=status)  # type: ignore[attr-defined]
    return err


@patch("app.chatbot.huggingface.generate.sleep")
@patch("app.chatbot.huggingface.generate.stream_text_generation")
@patch("app.chatbot.huggingface.generate.stream_chat_completion")
def test_generate_answer_does_not_retry_a_depleted_account(
    mock_chat: MagicMock, mock_tg: MagicMock, mock_sleep: MagicMock
) -> None:
    # 402 means the HF account is out of included credits. It answers the same
    # however many times we ask, so retrying only burns more failed calls.
    mock_chat.side_effect = [
        _raising_stream(_http_error(402, "Payment Required: depleted credits")),
        iter(["never reached"]),
    ]

    # The raised error names the account, not the task-support red herring that
    # text-generation would have logged last.
    with pytest.raises(RuntimeError, match="depleted credits"):
        list(generate_answer("s", "p"))

    assert mock_chat.call_count == 1
    mock_sleep.assert_not_called()
    # Nothing will serve this token, so the dead fallback is skipped entirely.
    mock_tg.assert_not_called()


@patch("app.chatbot.huggingface.generate.sleep")
@patch("app.chatbot.huggingface.generate.stream_text_generation")
@patch("app.chatbot.huggingface.generate.stream_chat_completion")
def test_generate_answer_retries_server_errors_and_rate_limits(
    mock_chat: MagicMock, mock_tg: MagicMock, mock_sleep: MagicMock
) -> None:
    mock_chat.side_effect = [
        _raising_stream(_http_error(429, "Too Many Requests")),
        _raising_stream(_http_error(503, "Service Unavailable")),
        iter(["Answer after the upstream recovered."]),
    ]

    result = _collect_stream(generate_answer("s", "p"))

    assert result == "Answer after the upstream recovered."
    assert mock_chat.call_count == 3


@patch("app.chatbot.huggingface.generate.sleep")
@patch("app.chatbot.huggingface.generate.stream_text_generation")
@patch("app.chatbot.huggingface.generate.stream_chat_completion")
def test_generate_answer_falls_back_only_after_every_chat_attempt_fails(
    mock_chat: MagicMock, mock_tg: MagicMock, mock_sleep: MagicMock
) -> None:
    mock_chat.side_effect = [
        _raising_stream(RuntimeError("503")),
        _raising_stream(RuntimeError("503")),
        _raising_stream(RuntimeError("503")),
    ]
    mock_tg.return_value = iter(["From text gen."])

    result = _collect_stream(generate_answer("s", "p"))

    assert result == "From text gen."
    assert mock_chat.call_count == 3


@patch("app.chatbot.huggingface.generate.get_settings")
@patch("app.chatbot.huggingface.generate.stream_text_generation")
@patch("app.chatbot.huggingface.generate.stream_chat_completion")
def test_generate_answer_raises_when_all_paths_fail(
    mock_chat: MagicMock,
    mock_tg: MagicMock,
    mock_settings: MagicMock,
) -> None:
    mock_settings.return_value.HUGGINGFACE_MODEL = "my-model"
    mock_settings.return_value.HUGGINGFACE_PROVIDER = "hf-inference"
    mock_chat.return_value = iter([])
    mock_tg.return_value = iter([])

    with pytest.raises(RuntimeError, match='No inference provider could stream model "my-model"'):
        list(generate_answer("s", "p"))
