"""Tests for HF-backed feedback tool routing (before RAG)."""

from unittest.mock import MagicMock, patch

from app.chat.feedback.tool_branch import try_feedback_tool_call


def test_try_feedback_calls_hf_route_when_key_set_and_model_returns_no_tool() -> None:
    with patch("app.chat.feedback.tool_branch.get_settings") as mock_settings, patch(
        "app.chat.feedback.tool_branch.route_send_feedback_call"
    ) as mock_route:
        mock_settings.return_value = MagicMock(HUGGINGFACE_API_KEY="x")
        mock_route.return_value = None
        assert try_feedback_tool_call("and their skills?", []) is None
        mock_route.assert_called_once()
