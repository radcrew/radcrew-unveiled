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
