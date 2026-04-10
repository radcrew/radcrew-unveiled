"""Tests for skipping HF feedback routing on obvious Q&A follow-ups."""

from unittest.mock import MagicMock, patch

from app.chat.feedback.tool_branch import should_attempt_feedback_routing, try_feedback_tool_call


def test_should_not_route_skills_followup() -> None:
    assert should_attempt_feedback_routing("and their skills?") is False


def test_should_not_route_what_about_them() -> None:
    assert should_attempt_feedback_routing("what about them?") is False


def test_should_not_route_is_he_comparative_question() -> None:
    assert should_attempt_feedback_routing("Is he the most experienced guy?") is False


def test_should_not_route_clarification_with_is_he() -> None:
    assert (
        should_attempt_feedback_routing(
            "I'm asking you. Is he the most experienced guy?"
        )
        is False
    )


def test_should_route_explicit_feedback_even_with_and_prefix() -> None:
    assert should_attempt_feedback_routing("and I want to send feedback: great site") is True


def test_try_feedback_skips_hf_for_skills_followup() -> None:
    with patch("app.chat.feedback.tool_branch.get_settings") as mock_settings, patch(
        "app.chat.feedback.tool_branch.route_send_feedback_call"
    ) as mock_route:
        mock_settings.return_value = MagicMock(HUGGINGFACE_API_KEY="x")
        assert try_feedback_tool_call("and their skills?", []) is None
        mock_route.assert_not_called()


def test_try_feedback_calls_hf_when_no_gate_match() -> None:
    with patch("app.chat.feedback.tool_branch.get_settings") as mock_settings, patch(
        "app.chat.feedback.tool_branch.route_send_feedback_call"
    ) as mock_route:
        mock_settings.return_value = MagicMock(HUGGINGFACE_API_KEY="x")
        mock_route.return_value = None
        assert try_feedback_tool_call("hello there", []) is None
        mock_route.assert_called_once()
