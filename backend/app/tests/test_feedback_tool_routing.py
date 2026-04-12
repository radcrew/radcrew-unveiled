"""Tests for HF-backed feedback intent classification (graph routes to RAG when no tool)."""

from unittest.mock import MagicMock, patch

from app.chatbot.feedback.tool_branch import classify_feedback_route


def test_classify_feedback_calls_hf_route_when_key_set_and_model_returns_no_tool() -> None:
    with patch("app.chatbot.feedback.tool_branch.get_settings") as mock_settings, patch(
        "app.chatbot.feedback.tool_branch.route_send_feedback_call"
    ) as mock_route:
        mock_settings.return_value = MagicMock(HUGGINGFACE_API_KEY="x")
        mock_route.return_value = None
        assert classify_feedback_route("and their skills?", []) is None
        mock_route.assert_called_once()
