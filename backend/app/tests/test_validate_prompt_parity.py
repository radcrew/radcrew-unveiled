"""Tests for training/scripts/validate_prompt_parity.py (dataset vs build_chat_prompt)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = REPO_ROOT / "training" / "scripts" / "validate_prompt_parity.py"


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
