import pytest
from unittest.mock import MagicMock, patch

from app.chat.huggingface.tool_routing import (
    ParsedToolCall,
    RouteReplyUnparseable,
    parse_tool_call_from_route_reply,
    route_send_feedback_call,
)


def test_parse_tool_call_from_route_reply_valid() -> None:
    text = '{"tool_call":{"name":"send_feedback","arguments":{"message":"x"}}}'
    got = parse_tool_call_from_route_reply(text)
    assert got is not None
    assert got.name == "send_feedback"
    assert '"message": "x"' in got.arguments or '"message":"x"' in got.arguments


def test_parse_tool_call_from_route_reply_null_means_no_tool() -> None:
    assert parse_tool_call_from_route_reply('{"tool_call": null}') is None


def test_parse_tool_call_from_route_reply_invalid_json_raises() -> None:
    with pytest.raises(RouteReplyUnparseable):
        parse_tool_call_from_route_reply("not json")


def test_parse_tool_call_from_route_reply_missing_tool_call_key_raises() -> None:
    with pytest.raises(RouteReplyUnparseable):
        parse_tool_call_from_route_reply("{}")


@patch("app.chat.huggingface.tool_routing.completion.InferenceClient")
@patch("app.chat.huggingface.tool_routing.route.get_settings")
def test_route_send_feedback_call_returns_none_for_other_tool(
    mock_get_settings: MagicMock, mock_cls: MagicMock
) -> None:
    cfg = MagicMock()
    cfg.HUGGINGFACE_MODEL = "m"
    cfg.HUGGINGFACE_API_KEY = "tok"
    cfg.HUGGINGFACE_PROVIDER = "hf-inference"
    mock_get_settings.return_value = cfg
    mock_inst = MagicMock()
    mock_cls.return_value = mock_inst
    mock_inst.chat_completion.return_value = {
        "choices": [
            {
                "message": {
                    "content": '{"tool_call":{"name":"other","arguments":{}}}',
                }
            }
        ]
    }
    assert route_send_feedback_call([{"role": "user", "content": "x"}]) is None


@patch("app.chat.huggingface.tool_routing.completion.InferenceClient")
@patch("app.chat.huggingface.tool_routing.route.get_settings")
def test_route_send_feedback_call_returns_none_when_tool_call_null(
    mock_get_settings: MagicMock, mock_cls: MagicMock
) -> None:
    cfg = MagicMock()
    cfg.HUGGINGFACE_MODEL = "m"
    cfg.HUGGINGFACE_API_KEY = "tok"
    cfg.HUGGINGFACE_PROVIDER = "hf-inference"
    mock_get_settings.return_value = cfg
    mock_inst = MagicMock()
    mock_cls.return_value = mock_inst
    mock_inst.chat_completion.return_value = {
        "choices": [{"message": {"content": '{"tool_call": null}'}}]
    }
    assert route_send_feedback_call([{"role": "user", "content": "hello"}]) is None


@patch("app.chat.huggingface.tool_routing.completion.InferenceClient")
@patch("app.chat.huggingface.tool_routing.route.get_settings")
def test_route_send_feedback_call_reads_send_feedback_from_message_content(
    mock_get_settings: MagicMock, mock_cls: MagicMock
) -> None:
    cfg = MagicMock()
    cfg.HUGGINGFACE_MODEL = "m"
    cfg.HUGGINGFACE_API_KEY = "tok"
    cfg.HUGGINGFACE_PROVIDER = "hf-inference"
    mock_get_settings.return_value = cfg
    mock_inst = MagicMock()
    mock_cls.return_value = mock_inst
    mock_inst.chat_completion.return_value = {
        "choices": [
            {
                "message": {
                    "content": (
                        '{"tool_call":{"name":"send_feedback",'
                        '"arguments":{"message":"m"}}}'
                    ),
                }
            }
        ]
    }
    msgs = [{"role": "user", "content": "send feedback: great"}]
    got = route_send_feedback_call(msgs)
    assert got is not None
    assert got.name == "send_feedback"
    assert "m" in got.arguments
    call_kw = mock_inst.chat_completion.call_args.kwargs
    assert call_kw.get("tools") is None
    assert call_kw.get("stream") is False


@patch("app.chat.huggingface.tool_routing.completion.InferenceClient")
@patch("app.chat.huggingface.tool_routing.route.get_settings")
def test_route_send_feedback_call_returns_none_when_reply_unparseable(
    mock_get_settings: MagicMock, mock_cls: MagicMock
) -> None:
    cfg = MagicMock()
    cfg.HUGGINGFACE_MODEL = "m"
    cfg.HUGGINGFACE_API_KEY = "tok"
    cfg.HUGGINGFACE_PROVIDER = "hf-inference"
    mock_get_settings.return_value = cfg
    mock_inst = MagicMock()
    mock_cls.return_value = mock_inst
    mock_inst.chat_completion.return_value = {
        "choices": [{"message": {"content": "not valid json for routing"}}]
    }
    got = route_send_feedback_call([{"role": "user", "content": "hello"}])
    assert got is None
