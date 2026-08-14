"""Tests for CLI helper functions."""

import pytest

from gh_profiler.utils import cli_utils
from gh_profiler.utils import infra_utils


def _fake_run_cmd(stdout, returncode=0):
    return lambda cmd: infra_utils.CommandResult(stdout=stdout, stderr="", returncode=returncode)


def test_get_repo_slug_strips_whitespace(monkeypatch):
    """A repo slug should not carry trailing whitespace from gh."""
    monkeypatch.setattr(cli_utils, "run_cmd", _fake_run_cmd("owner/repo\n"))

    assert cli_utils._get_repo_slug() == "owner/repo"


def test_get_repo_slug_blank_output(monkeypatch):
    """Blank output should exit with a helpful message."""
    monkeypatch.setattr(cli_utils, "run_cmd", _fake_run_cmd("   "))

    with pytest.raises(SystemExit) as exc_info:
        cli_utils._get_repo_slug()

    assert "Couldn't determine the default GitHub repository" in str(exc_info.value)
