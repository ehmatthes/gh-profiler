"""Tests for writing a workflow file."""

from pathlib import Path

import pytest

from gh_profiler.utils import workflow_utils


def test_get_workflow_path_no_conflicts(tmp_path, monkeypatch):
    """If .github/workflows exists and the file is new, use that path."""
    workflows_dir = tmp_path / ".github" / "workflows"
    workflows_dir.mkdir(parents=True)

    monkeypatch.chdir(tmp_path)

    path = workflow_utils._get_workflow_path()

    assert path == workflows_dir / "profile_contributors.yml"


def test_get_workflow_path_missing_git_dir(tmp_path, monkeypatch):
    """Without a .git dir, exit with a helpful message instead of a NameError.

    This is a regression test: this path used to reference an undefined
    `path_cwd` variable and crash.
    """
    monkeypatch.chdir(tmp_path)

    with pytest.raises(SystemExit) as exc_info:
        workflow_utils._get_workflow_path()

    assert "Could not find a .git dir" in str(exc_info.value)
