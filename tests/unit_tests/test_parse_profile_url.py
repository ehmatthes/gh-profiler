"""Tests for distinguishing profile URLs from repo URLs."""

import pytest

from gh_profiler.cli import _parse_profile_url


@pytest.mark.parametrize(
    "url, expected",
    [
        ("https://github.com/octocat", "octocat"),
        ("https://github.com/octocat/", "octocat"),
    ],
)
def test_profile_url_returns_username(url, expected):
    """A profile URL (owner only) returns the username."""
    assert _parse_profile_url(url) == expected


@pytest.mark.parametrize(
    "url",
    [
        "https://github.com/octocat/Hello-World",
        "https://github.com/octocat/Hello-World/",
        "https://github.com/octocat/Hello-World/pull/1",
    ],
)
def test_repo_url_returns_none(url):
    """A repo URL (owner and repo) returns None."""
    assert _parse_profile_url(url) is None
