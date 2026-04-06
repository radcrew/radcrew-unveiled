"""Submit company feedback via Web3Forms (https://web3forms.com)."""

from __future__ import annotations

import json
from urllib import error, request

from app.config import get_settings

WEB3FORMS_SUBMIT_URL = "https://api.web3forms.com/submit"

# Reasonable limits; message is the main email body.
MAX_MESSAGE_CHARS = 50_000
MAX_SUBJECT_CHARS = 200


class FeedbackError(Exception):
    """Feedback submission failed (config, validation, network, or API)."""


def _normalize_optional_subject(subject: str | None) -> str | None:
    if subject is None:
        return None
    s = subject.strip()
    return s if s else None


def _validate_message(text: str) -> str:
    if not isinstance(text, str):
        raise FeedbackError("Feedback message must be a string.")
    stripped = text.strip()
    if not stripped:
        raise FeedbackError("Feedback message cannot be empty.")
    if len(stripped) > MAX_MESSAGE_CHARS:
        raise FeedbackError(
            f"Feedback message is too long (max {MAX_MESSAGE_CHARS} characters)."
        )
    return stripped


def _validate_subject(subject: str | None) -> str | None:
    normalized = _normalize_optional_subject(subject)
    if normalized is None:
        return None
    if len(normalized) > MAX_SUBJECT_CHARS:
        raise FeedbackError(
            f"Subject is too long (max {MAX_SUBJECT_CHARS} characters)."
        )
    return normalized


def _message_from_api_payload(payload: dict[str, object]) -> str | None:
    if payload.get("success") is True:
        return None
    msg = payload.get("message")
    if isinstance(msg, str) and msg.strip():
        return msg.strip()
    body = payload.get("body")
    if isinstance(body, dict):
        inner = body.get("message")
        if isinstance(inner, str) and inner.strip():
            return inner.strip()
    err = payload.get("error")
    if isinstance(err, str) and err.strip():
        return err.strip()
    return None


def _read_response_body(resp: object) -> bytes:
    read = getattr(resp, "read", None)
    if callable(read):
        return read()
    return b""


def submit_feedback_via_web3forms(
    body: str,
    subject: str | None = None,
) -> None:
    """
    POST JSON to Web3Forms. Raises FeedbackError if configuration, validation,
    HTTP, API, or network handling fails.
    """
    settings = get_settings()

    cfg = settings if settings is not None else get_settings()
    access_key = cfg.WEB3FORMS_ACCESS_KEY
    if not access_key or not str(access_key).strip():
        raise FeedbackError("Feedback submission is not configured (missing access key).")

    message = _validate_message(body)
    subject_clean = _validate_subject(subject)

    payload_obj: dict[str, object] = {
        "access_key": str(access_key).strip(),
        "message": message,
    }
    if subject_clean is not None:
        payload_obj["subject"] = subject_clean

    payload = json.dumps(payload_obj).encode("utf-8")
    req = request.Request(
        url=WEB3FORMS_SUBMIT_URL,
        data=payload,
        method="POST",
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "application/json",
            "User-Agent": "radcrew-unveiled-feedback/1.0",
        },
    )

    try:
        with request.urlopen(req, timeout=30) as response:
            raw = _read_response_body(response)
            status = getattr(response, "status", None)
            if status is not None and status != 200:
                _raise_submission_error(status, raw)
            _ensure_success_payload(raw)
    except error.HTTPError as e:
        raw = e.read() if hasattr(e, "read") else b""
        _raise_submission_error(e.code, raw)
    except error.URLError as e:
        reason = e.reason
        detail = str(reason) if reason else str(e)
        raise FeedbackError(f"Could not reach feedback service: {detail}") from e


def _ensure_success_payload(raw: bytes) -> None:
    if not raw:
        raise FeedbackError("Empty response from feedback service.")
    try:
        parsed = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        raise FeedbackError("Invalid JSON response from feedback service.") from e
    if not isinstance(parsed, dict):
        raise FeedbackError("Unexpected response from feedback service.")
    if parsed.get("success") is True:
        return
    msg = _message_from_api_payload(parsed) or "Feedback could not be sent."
    raise FeedbackError(msg)


def _raise_submission_error(status: int, raw: bytes) -> None:
    msg: str | None = None
    if raw:
        try:
            parsed = json.loads(raw.decode("utf-8"))
            if isinstance(parsed, dict):
                msg = _message_from_api_payload(parsed)
        except (UnicodeDecodeError, json.JSONDecodeError):
            pass
    if not msg:
        msg = f"Feedback service returned HTTP {status}."
    raise FeedbackError(msg)
