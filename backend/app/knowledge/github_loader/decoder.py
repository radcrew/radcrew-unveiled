from __future__ import annotations

import base64


def decode_blob_content(blob_payload: dict[str, object]) -> str:
    content = blob_payload.get("content")
    if not isinstance(content, str):
        raise ValueError("GitHub blob response missing content")
    encoding = str(blob_payload.get("encoding") or "")
    if encoding and encoding.lower() != "base64":
        raise ValueError(f"Unsupported GitHub blob encoding: {encoding}")
    raw = base64.b64decode(content.encode("utf-8"), validate=False)
    return raw.decode("utf-8", errors="replace")
