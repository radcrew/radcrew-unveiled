from __future__ import annotations

import json
from urllib import request

from app.core.settings import get_settings

WEB3FORMS_SUBMIT_URL = "https://api.web3forms.com/submit"

def submit_feedback(
    body: str,
    subject: str | None = None,
) -> None:
    settings = get_settings()

    access_key = settings.WEB3FORMS_ACCESS_KEY
    if not access_key:
        raise Exception("Feedback submission is not configured (missing access key).")

    payload_obj: dict[str, object] = {
        "access_key": access_key,
        "message": body,
        "subject": subject
    }

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

    with request.urlopen(req, timeout=30) as response:
        response.read()
