from __future__ import annotations

import json
from urllib import request

API_BASE = "https://api.github.com"
ACCEPT_JSON = "application/vnd.github+json"


def get_json(url: str, *, token: str | None) -> dict[str, object]:
    req = request.Request(
        url=url,
        headers=build_headers(token),
        method="GET",
    )

    with request.urlopen(req, timeout=20) as response:
        payload = response.read()

    parsed = json.loads(payload.decode("utf-8"))
    if not isinstance(parsed, dict):
        raise ValueError("GitHub API response must be a JSON object")

    return parsed


def build_headers(token: str | None) -> dict[str, str]:
    headers = {
        "Accept": ACCEPT_JSON,
        "User-Agent": "radcrew-unveiled-kb-loader",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers
