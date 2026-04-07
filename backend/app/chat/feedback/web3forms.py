"""Submit company feedback via Web3Forms (https://web3forms.com)."""

from __future__ import annotations

import json
from urllib import error, request

from app.config import get_settings

WEB3FORMS_SUBMIT_URL = "https://api.web3forms.com/submit"

# Reasonable limits; message is the main email body.
MAX_MESSAGE_CHARS = 50_000


class FeedbackError(Exception):
    """Feedback submission failed (config, validation, network, or API)."""

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

    access_key = settings.WEB3FORMS_ACCESS_KEY
    if not access_key or not str(access_key).strip():
        raise FeedbackError("Feedback submission is not configured (missing access key).")

    payload_obj: dict[str, object] = {
        "access_key": str(access_key).strip(),
        "message": body,
    }

    subject = subject.strip() if subject else None
    if subject:
        payload_obj["subject"] = subject

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
                _raise_submission_error(status)
            _ensure_success_payload(raw)

    except error.HTTPError as e:
        _raise_submission_error(e.code)

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

    raise FeedbackError("Feedback could not be sent.")


def _raise_submission_error(status: int) -> None:
    raise FeedbackError(f"Feedback service returned HTTP {status}.")
