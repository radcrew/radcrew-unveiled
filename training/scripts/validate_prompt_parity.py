#!/usr/bin/env python3
"""Check JSONL dataset rows: user prompt matches build_chat_prompt(question, chunks, history).

Run from repo root (any cwd is fine):

  python training/scripts/validate_prompt_parity.py path/to/rows.jsonl

Requires structured fields on each auditable row: ``question``, ``context_chunks`` (array, may be
empty), optional ``history``. Stored user text is read from ``messages[0].content`` or ``prompt``.

See training/DATASET.md for the parity contract.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Iterator
from difflib import unified_diff
from pathlib import Path
from typing import Any


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def ensure_backend_on_path() -> None:
    backend = repo_root() / "backend"
    s = str(backend)
    if s not in sys.path:
        sys.path.insert(0, s)


def iter_jsonl_objects(path: Path) -> Iterator[tuple[int, dict[str, Any]]]:
    with path.open(encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                obj = json.loads(stripped)
            except json.JSONDecodeError as e:
                raise SystemExit(f"{path}:{line_no}: invalid JSON: {e}") from e
            if not isinstance(obj, dict):
                raise SystemExit(f"{path}:{line_no}: expected JSON object, got {type(obj).__name__}")
            yield line_no, obj


def stored_user_content(row: dict[str, Any]) -> str | None:
    if "messages" in row:
        msgs = row["messages"]
        if not isinstance(msgs, list) or len(msgs) < 1:
            return None
        first = msgs[0]
        if not isinstance(first, dict) or first.get("role") != "user":
            return None
        c = first.get("content")
        return c if isinstance(c, str) else None
    if "prompt" in row:
        p = row["prompt"]
        return p if isinstance(p, str) else None
    return None


def rebuild_user_prompt(row: dict[str, Any]) -> str:
    """Rebuild the production user prompt string from structured fields."""
    if "question" not in row:
        raise ValueError("missing 'question'")
    q = row["question"]
    if not isinstance(q, str):
        raise ValueError("'question' must be a string")

    if "context_chunks" not in row:
        raise ValueError("missing 'context_chunks' (use [] for no retrieved chunks)")
    chunks_raw = row["context_chunks"]
    if not isinstance(chunks_raw, list):
        raise ValueError("'context_chunks' must be an array")

    hist_raw = row.get("history")
    if hist_raw is None:
        hist_raw = []
    if not isinstance(hist_raw, list):
        raise ValueError("'history' must be an array when present")

    ensure_backend_on_path()
    from app.chatbot.rag.prompt import build_chat_prompt
    from app.chatbot.knowledge.models import KnowledgeChunk
    from app.schemas import ChatHistoryMessage

    chunks: list[KnowledgeChunk] = []
    for i, raw in enumerate(chunks_raw):
        if not isinstance(raw, dict):
            raise ValueError(f"context_chunks[{i}] must be an object")
        title = raw.get("title")
        text = raw.get("text")
        if not isinstance(title, str) or not isinstance(text, str):
            raise ValueError(f"context_chunks[{i}] needs string 'title' and 'text'")
        cid = raw.get("id")
        tokens_raw = raw.get("tokens")
        tokens = list(tokens_raw) if isinstance(tokens_raw, list) else []
        url = raw.get("url")
        if url is not None and not isinstance(url, str):
            raise ValueError(f"context_chunks[{i}].url must be a string or null")
        score = raw.get("score")
        if score is not None and not isinstance(score, int | float):
            raise ValueError(f"context_chunks[{i}].score must be a number or null")
        chunks.append(
            KnowledgeChunk(
                id=str(cid) if cid is not None else f"dataset-chunk-{i}",
                title=title,
                text=text,
                tokens=[str(t) for t in tokens],
                url=url,
                score=float(score) if score is not None else None,
            )
        )

    history: list[ChatHistoryMessage] = []
    for i, h in enumerate(hist_raw):
        if not isinstance(h, dict):
            raise ValueError(f"history[{i}] must be an object")
        role = h.get("role")
        content = h.get("content")
        if role not in ("user", "assistant"):
            raise ValueError(f"history[{i}].role must be 'user' or 'assistant'")
        if not isinstance(content, str):
            raise ValueError(f"history[{i}].content must be a string")
        history.append(ChatHistoryMessage(role=role, content=content))

    return build_chat_prompt(q, chunks, history)


def row_is_auditable(row: dict[str, Any]) -> bool:
    return "question" in row and "context_chunks" in row


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("jsonl", type=Path, help="Path to JSONL file")
    parser.add_argument(
        "--max-rows",
        type=int,
        default=None,
        help="Stop after this many non-empty JSONL lines (for quick sampling)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Print unified diff when a row mismatches",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with error if any line is auditable but has no stored user content to compare",
    )
    args = parser.parse_args()
    path: Path = args.jsonl
    if not path.is_file():
        raise SystemExit(f"not a file: {path}")

    checked = 0
    skipped = 0
    mismatches = 0
    strict_issues = 0
    rows_seen = 0

    for line_no, row in iter_jsonl_objects(path):
        if args.max_rows is not None and rows_seen >= args.max_rows:
            break
        rows_seen += 1

        if not row_is_auditable(row):
            skipped += 1
            continue

        stored = stored_user_content(row)
        if stored is None:
            msg = f"{path}:{line_no}: auditable row but no messages[0].content or prompt"
            if args.strict:
                strict_issues += 1
                print(msg, file=sys.stderr)
            else:
                skipped += 1
            continue

        try:
            rebuilt = rebuild_user_prompt(row)
        except Exception as e:
            mismatches += 1
            print(f"{path}:{line_no}: rebuild failed: {e}", file=sys.stderr)
            continue

        checked += 1
        if rebuilt != stored:
            mismatches += 1
            print(f"{path}:{line_no}: prompt mismatch (rebuilt != stored user content)", file=sys.stderr)
            if args.verbose:
                diff = unified_diff(
                    stored.splitlines(keepends=True),
                    rebuilt.splitlines(keepends=True),
                    fromfile="stored",
                    tofile="rebuilt",
                    n=3,
                )
                sys.stderr.writelines(diff)

    print(
        f"Summary: checked={checked}, skipped={skipped}, mismatches={mismatches}"
        + (f", strict_issues={strict_issues}" if strict_issues else "")
    )

    if mismatches:
        raise SystemExit(1)
    if args.strict and strict_issues:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
