from unittest.mock import MagicMock, patch

from app.chat.huggingface.tool_routing import (
    ParsedToolCall,
    parse_tool_calls_from_completion,
    parse_tool_calls_from_json_text,
    route_send_feedback_call,
    route_tool_calls,
)


def test_parse_tool_calls_from_completion_dict() -> None:
    resp = {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [
                        {
                            "id": "call_1",
                            "type": "function",
                            "function": {
                                "name": "send_feedback",
                                "arguments": '{"message": "hi", "subject": "s"}',
                            },
                        }
                    ],
                }
            }
        ]
    }
    got = parse_tool_calls_from_completion(resp)
    assert got == [
        ParsedToolCall(
            id="call_1",
            name="send_feedback",
            arguments='{"message": "hi", "subject": "s"}',
        )
    ]


def test_parse_tool_calls_from_json_text_valid() -> None:
    text = '{"tool_calls":[{"name":"send_feedback","arguments":{"message":"x"}}]}'
    got = parse_tool_calls_from_json_text(text)
    assert got is not None
    assert len(got) == 1
    assert got[0].name == "send_feedback"
    assert '"message": "x"' in got[0].arguments or '"message":"x"' in got[0].arguments


def test_parse_tool_calls_from_json_text_empty() -> None:
    assert parse_tool_calls_from_json_text('{"tool_calls":[]}') == []


def test_parse_tool_calls_from_json_text_invalid() -> None:
    assert parse_tool_calls_from_json_text("not json") is None


@patch("app.chat.huggingface.tool_routing.route.route_tool_calls")
def test_route_send_feedback_call_picks_send_feedback(mock_route: MagicMock) -> None:
    mock_route.return_value = [
        ParsedToolCall(id="a", name="other", arguments="{}"),
        ParsedToolCall(id="b", name="send_feedback", arguments='{"message":"x"}'),
    ]
    got = route_send_feedback_call([])
    assert got is not None
    assert got.name == "send_feedback"
    assert "x" in got.arguments


@patch("app.chat.huggingface.tool_routing.route.route_tool_calls", return_value=[])
def test_route_send_feedback_call_returns_none_when_absent(_mock: MagicMock) -> None:
    assert route_send_feedback_call([]) is None


@patch("app.chat.huggingface.tool_routing.completion.InferenceClient")
@patch("app.chat.huggingface.tool_routing.route.get_settings")
def test_route_tool_calls_uses_tools_and_returns_parsed(
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
                    "tool_calls": [
                        {
                            "id": "c1",
                            "function": {
                                "name": "send_feedback",
                                "arguments": '{"message":"m"}',
                            },
                        }
                    ],
                }
            }
        ]
    }
    msgs = [{"role": "user", "content": "send feedback: great"}]
    got = route_tool_calls(msgs)
    assert len(got) == 1
    assert got[0].name == "send_feedback"
    call_kw = mock_inst.chat_completion.call_args.kwargs
    assert call_kw.get("tools") is not None
    assert call_kw.get("tool_choice") == "auto"
    assert call_kw.get("stream") is False


@patch("app.chat.huggingface.tool_routing.completion.InferenceClient")
@patch("app.chat.huggingface.tool_routing.route.get_settings")
def test_route_tool_calls_json_fallback_when_tools_raises(
    mock_get_settings: MagicMock, mock_cls: MagicMock
) -> None:
    cfg = MagicMock()
    cfg.HUGGINGFACE_MODEL = "m"
    cfg.HUGGINGFACE_API_KEY = "tok"
    cfg.HUGGINGFACE_PROVIDER = "hf-inference"
    mock_get_settings.return_value = cfg
    mock_inst = MagicMock()
    mock_cls.return_value = mock_inst

    def side_effect(*_a: object, **kw: object) -> dict[str, object]:
        if kw.get("tools"):
            raise RuntimeError("tools not supported")
        return {
            "choices": [
                {
                    "message": {
                        "content": '{"tool_calls":[{"name":"send_feedback","arguments":{"message":"fb"}}]}',
                    }
                }
            ]
        }

    mock_inst.chat_completion.side_effect = side_effect
    got = route_tool_calls([{"role": "user", "content": "please submit feedback"}])
    assert len(got) == 1
    assert got[0].name == "send_feedback"
    assert "fb" in got[0].arguments
