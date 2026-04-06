"""Non-stream chat completion with tool calling and optional JSON fallback."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any

from huggingface_hub import InferenceClient
from huggingface_hub.errors import HFValidationError, HfHubHTTPError
from huggingface_hub.inference._generated.types.chat_completion import (
    ChatCompletionInputResponseFormatJSONObject,
)

from app.chat.huggingface.common import (
    DETERMINISTIC_GENERATION_SEED,
    providers_to_try,
    safe_get,
)
from app.schemas import ChatHistoryMessage

logger = logging.getLogger(__name__)

# Prepended to the routing completion so the model defaults to *no* tool call; without this,
# a single exposed tool is often invoked on every turn (especially with user-only transcripts).
TOOL_ROUTING_SYSTEM_MESSAGE = (
    "You are an intent router for a chat assistant. One optional tool exists: "
    "send_feedback. Your default is to call NO tools. "
    "Call send_feedback only when the user's latest message clearly means they want to "
    "submit feedback, suggestions, or a bug report to the company—e.g. they explicitly ask to "
    "send feedback, email the team with feedback, or share product feedback meant for staff. "
    "Do not call it for greetings, general questions, small talk, or normal FAQ-style questions."
)


def build_feedback_routing_messages(
    message: str,
    history: list[ChatHistoryMessage],
) -> list[dict[str, Any]]:
    """System router, then full chat history (both roles), then the latest user message."""
    msgs: list[dict[str, Any]] = [
        {"role": "system", "content": TOOL_ROUTING_SYSTEM_MESSAGE},
    ]
    for m in history:
        msgs.append({"role": m.role, "content": m.content})
    msgs.append({"role": "user", "content": message})
    return msgs


# Tool schema for user feedback submission (Web3Forms payload fields).
FEEDBACK_SUBMISSION_TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "send_feedback",
            "description": (
                "Submit structured feedback to the team on behalf of the user. "
                "Call ONLY when they clearly intend to send feedback—not for ordinary questions "
                "or conversation."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "The feedback body to deliver.",
                    },
                    "subject": {
                        "type": "string",
                        "description": "Optional short subject line for the feedback.",
                    },
                },
                "required": ["message"],
            },
        },
    }
]

_JSON_FALLBACK_SUFFIX = (
    "Based on the conversation and the routing rules in the system message, decide whether "
    "the user's latest message clearly intends to submit feedback via send_feedback. "
    'Reply with ONLY a single JSON object (no markdown fences) of the form: '
    '{"tool_calls":[]} when no tool call is appropriate (this should be the usual case), or '
    '{"tool_calls":[{"name":"send_feedback","arguments":{"message":"<text>",'
    '"subject":"<optional>"}}]} only when they clearly want to send feedback to the company.'
)


@dataclass(frozen=True)
class ParsedToolCall:
    """One model-emitted tool call (OpenAI-style)."""

    id: str
    name: str
    arguments: str


def _choices(resp: Any) -> list[Any]:
    ch = safe_get(resp, "choices")
    return ch if isinstance(ch, list) else []


def _first_message(resp: Any) -> Any:
    ch = _choices(resp)
    if not ch:
        return None
    return safe_get(ch[0], "message")


def parse_tool_calls_from_completion(resp: Any) -> list[ParsedToolCall]:
    """Parse ``choices[0].message.tool_calls`` from a chat completion response."""
    msg = _first_message(resp)
    if msg is None:
        return []
    raw_calls = safe_get(msg, "tool_calls")
    if not raw_calls:
        return []
    out: list[ParsedToolCall] = []
    for tc in raw_calls:
        tc_id = safe_get(tc, "id")
        fn = safe_get(tc, "function")
        name = safe_get(fn, "name") if fn is not None else None
        args = safe_get(fn, "arguments") if fn is not None else None
        if isinstance(args, str):
            arg_str = args
        elif args is None:
            arg_str = "{}"
        else:
            arg_str = json.dumps(args)
        out.append(
            ParsedToolCall(
                id=str(tc_id) if tc_id is not None else "",
                name=str(name) if name is not None else "",
                arguments=arg_str,
            )
        )
    return out


def _extract_message_content(resp: Any) -> str:
    msg = _first_message(resp)
    if msg is None:
        return ""
    content = safe_get(msg, "content")
    return content if isinstance(content, str) else ""


def _strip_json_fences(text: str) -> str:
    t = text.strip()
    if not t.startswith("```"):
        return t
    lines = t.split("\n")
    if lines and lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]
    return "\n".join(lines).strip()


def parse_tool_calls_from_json_text(text: str) -> list[ParsedToolCall] | None:
    """
    Parse fallback JSON ``{"tool_calls": [...]}`` from model text.

    Returns ``None`` if the payload is not valid JSON with a ``tool_calls`` array.
    Returns an empty list when ``tool_calls`` is valid but empty.
    """
    raw = _strip_json_fences(text)
    if not raw:
        return None
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        logger.warning("[tool routing] JSON fallback could not parse model output")
        return None
    if not isinstance(data, dict):
        return None
    calls = data.get("tool_calls")
    if not isinstance(calls, list):
        return None
    out: list[ParsedToolCall] = []
    for i, item in enumerate(calls):
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        if not isinstance(name, str) or not name.strip():
            continue
        args = item.get("arguments")
        if isinstance(args, dict):
            arg_str = json.dumps(args)
        elif isinstance(args, str):
            arg_str = args
        else:
            arg_str = "{}"
        out.append(
            ParsedToolCall(
                id=f"json-fallback-{i}",
                name=name.strip(),
                arguments=arg_str,
            )
        )
    return out


def _chat_completion_tools_once(
    model: str,
    access_token: str,
    messages: list[dict[str, Any]],
    provider: str,
    tools: list[dict[str, Any]],
) -> Any:
    client = InferenceClient(model=model, token=access_token, provider=provider)  # type: ignore[arg-type]
    return client.chat_completion(
        messages=messages,
        tools=tools,
        tool_choice="auto",
        stream=False,
        max_tokens=512,
        temperature=0,
        top_p=1,
        seed=DETERMINISTIC_GENERATION_SEED,
    )


def _json_fallback_messages(base: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [*base, {"role": "user", "content": _JSON_FALLBACK_SUFFIX}]


def _chat_completion_json_fallback_once(
    model: str,
    access_token: str,
    messages: list[dict[str, Any]],
    provider: str,
    *,
    use_json_object_format: bool,
) -> Any:
    client = InferenceClient(model=model, token=access_token, provider=provider)  # type: ignore[arg-type]
    kwargs: dict[str, Any] = {
        "messages": messages,
        "stream": False,
        "max_tokens": 512,
        "temperature": 0,
        "top_p": 1,
        "seed": DETERMINISTIC_GENERATION_SEED,
    }
    if use_json_object_format:
        kwargs["response_format"] = ChatCompletionInputResponseFormatJSONObject(type="json_object")
    return client.chat_completion(**kwargs)


def route_tool_calls(
    model: str,
    access_token: str,
    messages: list[dict[str, Any]],
    provider_policy: str = "hf-inference",
    *,
    tools: list[dict[str, Any]] | None = None,
) -> list[ParsedToolCall]:
    """
    Run non-stream ``chat_completion`` with ``tools`` and ``tool_choice="auto"``,
    parse ``choices[0].message.tool_calls``, and return structured calls.

    If every provider fails the tools request (HTTP/validation errors), runs an
    optional JSON-only completion (with and without ``response_format: json_object``)
    and parses ``{"tool_calls": [...]}`` from the assistant message content.
    """
    tool_list = tools if tools is not None else FEEDBACK_SUBMISSION_TOOLS
    providers = providers_to_try(provider_policy)

    for provider in providers:
        try:
            resp = _chat_completion_tools_once(
                model, access_token, messages, provider, tool_list
            )
            return parse_tool_calls_from_completion(resp)
        except Exception as err:
            logger.error("[HF chatCompletionTools provider=%s] %s", provider, err)

    # JSON fallback: same providers; try json_object response format first, then plain.
    fallback_msgs = _json_fallback_messages(messages)
    for provider in providers:
        for use_json_fmt in (True, False):
            try:
                resp = _chat_completion_json_fallback_once(
                    model,
                    access_token,
                    fallback_msgs,
                    provider,
                    use_json_object_format=use_json_fmt,
                )
                content = _extract_message_content(resp)
                parsed = parse_tool_calls_from_json_text(content)
                if parsed is not None:
                    return parsed
            except Exception as err:
                logger.error(
                    "[HF chatCompletionJsonFallback provider=%s json_fmt=%s] %s",
                    provider,
                    use_json_fmt,
                    err,
                )

    return []
