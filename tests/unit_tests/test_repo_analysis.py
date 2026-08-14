"""Tests for analyzing repo data in bulk processing."""

from gh_profiler.utils import repo_analysis
from gh_profiler.utils.profile_data import profile_data as pdata
from gh_profiler.utils.repo_data import PRData


def test_adjust_author_summary_drops_closing_line():
    """The bulk version should not carry the 'run a detailed report' line."""
    pdata.username = "alice"
    concise = (
        "GitHub user: alice\n"
        "🟢 No concerns found with user's profile.\n"
        "🟢 No concerns found with recent PR activity.\n"
        "🟢 No concerns found with recent issue activity.\n"
        "\nFor a more detailed report, run `gh-profiler alice`."
    )

    adjusted = repo_analysis._adjust_author_summary(concise)

    assert "For a more detailed report" not in adjusted
    assert adjusted.splitlines()[0] == "  GitHub user: alice"


def test_get_cached_author_info():
    """A second PR from the same author should reuse the first profile."""
    prs = [
        PRData(pr_num=1, author="alice"),
        PRData(
            pr_num=2,
            author="alice",
            author_summary="summary text",
            profile_flag="\U0001f7e2",
            pr_flag="\U0001f7e1",
            issue_flag="\U0001f7e2",
        ),
        PRData(pr_num=3, author="bob"),
    ]

    info = repo_analysis._get_cached_author_info("alice", prs)

    assert info == ("summary text", "\U0001f7e2", "\U0001f7e1", "\U0001f7e2")


def test_get_cached_author_info_no_match():
    """An author with no cached profile should return None."""
    prs = [PRData(pr_num=1, author="alice")]

    assert repo_analysis._get_cached_author_info("bob", prs) is None