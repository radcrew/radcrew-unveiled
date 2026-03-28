from unittest.mock import MagicMock, patch

import pytest

from app.chat.huggingface import generate_answer


def _chat_out(content: str) -> MagicMock:
    msg = MagicMock()
    msg.content = content
    choice = MagicMock()
    choice.message = msg
    out = MagicMock()
    out.choices = [choice]
    return out


@patch("app.chat.huggingface.InferenceClient")
def test_generate_answer_returns_chat_completion_text(mock_client_cls: MagicMock) -> None:
    mock_inst = MagicMock()
    mock_client_cls.return_value = mock_inst
    mock_inst.chat_completion.return_value = _chat_out("  Answer from chat.  ")

    result = generate_answer(
        "Qwen/Qwen2.5-1.5B-Instruct",
        "token",
        "prompt text",
        "hf-inference",
    )

    assert result == "Answer from chat."
    assert mock_inst.chat_completion.call_count >= 1
    mock_inst.text_generation.assert_not_called()


@patch("app.chat.huggingface.InferenceClient")
def test_generate_answer_falls_back_to_text_generation(mock_client_cls: MagicMock) -> None:
    mock_inst = MagicMock()
    mock_client_cls.return_value = mock_inst
    mock_inst.chat_completion.return_value = _chat_out("")
    mock_inst.text_generation.return_value = "  From text gen.  "

    result = generate_answer("m", "t", "p", "auto")

    assert result == "From text gen."
    mock_inst.text_generation.assert_called()


@patch("app.chat.huggingface.InferenceClient")
def test_generate_answer_raises_when_all_paths_fail(mock_client_cls: MagicMock) -> None:
    mock_inst = MagicMock()
    mock_client_cls.return_value = mock_inst
    mock_inst.chat_completion.return_value = _chat_out("")
    mock_inst.text_generation.return_value = ""

    with pytest.raises(RuntimeError, match="No inference provider could run model"):
        generate_answer("my-model", "t", "p", "hf-inference")
