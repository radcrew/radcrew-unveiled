from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.config import Settings


def test_settings_requires_repo_url_when_github_token_is_set():
    with pytest.raises(ValidationError, match="GITHUB_KB_REPO_URL is required"):
        Settings(_env_file=None, GITHUB_KB_TOKEN="ghp_test_token")


def test_settings_requires_token_for_private_repo():
    with pytest.raises(ValidationError, match="GITHUB_KB_TOKEN is required"):
        Settings(
            _env_file=None,
            GITHUB_KB_REPO_URL="https://github.com/example-org/private-repo",
            GITHUB_KB_PRIVATE_REPO=True,
        )


def test_settings_accepts_private_repo_with_token():
    settings = Settings(
        _env_file=None,
        GITHUB_KB_REPO_URL="https://github.com/example-org/private-repo",
        GITHUB_KB_PRIVATE_REPO=True,
        GITHUB_KB_TOKEN="  ghp_test_token  ",
        GITHUB_KB_BRANCH="  docs-branch  ",
        GITHUB_KB_PATH="  docs/knowledge  ",
    )

    assert str(settings.GITHUB_KB_REPO_URL) == "https://github.com/example-org/private-repo"
    assert settings.GITHUB_KB_TOKEN == "ghp_test_token"
    assert settings.GITHUB_KB_BRANCH == "docs-branch"
    assert settings.GITHUB_KB_PATH == "docs/knowledge"
