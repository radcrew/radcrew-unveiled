"""Tests for training/scripts/validate_prompt_parity.py (dataset vs build_chat_prompt)."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

from app.chatbot.rag.prompt import build_chat_prompt
from app.chatbot.knowledge.models import KnowledgeChunk
from app.schemas import ChatHistoryMessage

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = REPO_ROOT / "training" / "scripts" / "validate_prompt_parity.py"


def _load_parity_module():
    spec = importlib.util.spec_from_file_location("validate_prompt_parity", SCRIPT_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_rebuild_user_prompt_matches_build_chat_prompt() -> None:
    vpp = _load_parity_module()
    chunks = [KnowledgeChunk(id="c1", title="Guide", text="Team A owns X.", tokens=[])]
    history = [ChatHistoryMessage(role="user", content="Hello there")]
    expected = build_chat_prompt("Who maintains X?", chunks, history)

    row = {
        "question": "Who maintains X?",
        "history": [{"role": "user", "content": "Hello there"}],
        "context_chunks": [{"title": "Guide", "text": "Team A owns X."}],
        "messages": [
            {"role": "user", "content": expected},
            {"role": "assistant", "content": "Team A maintains X."},
        ],
    }
    assert vpp.stored_user_content(row) == expected
    assert vpp.rebuild_user_prompt(row) == expected


def test_rebuild_empty_context_and_history() -> None:
    vpp = _load_parity_module()
    expected = build_chat_prompt("Any news?", [], None)
    row = {
        "question": "Any news?",
        "context_chunks": [],
        "messages": [
            {"role": "user", "content": expected},
            {"role": "assistant", "content": "Not enough information."},
        ],
    }
    assert vpp.rebuild_user_prompt(row) == expected


def test_cli_exits_zero_on_valid_jsonl(tmp_path: Path) -> None:
    chunks = [KnowledgeChunk(id="c1", title="Guide", text="Body", tokens=[])]
    expected = build_chat_prompt("Q?", chunks, None)
    row = {
        "question": "Q?",
        "context_chunks": [{"title": "Guide", "text": "Body"}],
        "messages": [
            {"role": "user", "content": expected},
            {"role": "assistant", "content": "A."},
        ],
    }
    jsonl = tmp_path / "rows.jsonl"
    jsonl.write_text(json.dumps(row) + "\n", encoding="utf-8")

    proc = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), str(jsonl)],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr + proc.stdout


def test_cli_exits_nonzero_on_mismatch(tmp_path: Path) -> None:
    row = {
        "question": "Q?",
        "context_chunks": [{"title": "Guide", "text": "Body"}],
        "messages": [
            {"role": "user", "content": "this is not the real prompt"},
            {"role": "assistant", "content": "A."},
        ],
    }
    jsonl = tmp_path / "rows.jsonl"
    jsonl.write_text(json.dumps(row) + "\n", encoding="utf-8")

    proc = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), str(jsonl)],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 1
