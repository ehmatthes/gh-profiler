"""Tests for fetching and parsing repo-level data."""

import json

from gh_profiler.utils import infra_utils
from gh_profiler.utils import repo_fetching
from gh_profiler.utils.cli_config import cli_config


def _pr_node(number, title, author, closed_at, merged=False):
    return {
        "number": number,
        "title": title,
        "state": "MERGED" if merged else "CLOSED",
        "merged": merged,
        "createdAt": "2024-01-01T00:00:00Z",
        "closedAt": closed_at,
        "mergedAt": "2024-01-01T00:00:00Z" if merged else None,
        "url": f"https://github.com/owner/repo/pull/{number}",
        "author": {"login": author},
    }


def test_parse_prs(monkeypatch):
    """Open PRs should parse into PRData objects in order."""
    cli_config.back = False
    cli_config.num_targets = 10

    nodes = [
        _pr_node(1, "First PR", "alice", None),
        _pr_node(2, "Second PR", "bob", None),
    ]
    response = infra_utils.CommandResult(
        stdout=json.dumps({"data": {"repository": {"pullRequests": {"nodes": nodes}}}}),
        stderr="",
        returncode=0,
    )

    target_prs = repo_fetching._parse_prs(response)

    assert [pr.pr_num for pr in target_prs] == [1, 2]
    assert [pr.author for pr in target_prs] == ["alice", "bob"]
    assert target_prs[0].title == "First PR"
    assert target_prs[0].merged is None


def test_parse_prs_back_uses_closed_at(monkeypatch):
    """When looking back, PRs should be sorted by closedAt and capped."""
    cli_config.back = True
    cli_config.num_targets = 2

    nodes = [
        _pr_node(1, "Old", "alice", "2024-01-01T00:00:00Z"),
        _pr_node(2, "New", "bob", "2024-03-01T00:00:00Z", merged=True),
        _pr_node(3, "Middle", "carol", "2024-02-01T00:00:00Z"),
    ]
    response = infra_utils.CommandResult(
        stdout=json.dumps({"data": {"repository": {"pullRequests": {"nodes": nodes}}}}),
        stderr="",
        returncode=0,
    )

    target_prs = repo_fetching._parse_prs(response)

    assert [pr.pr_num for pr in target_prs] == [2, 3]
    assert target_prs[0].merged is True
    assert target_prs[1].merged is False