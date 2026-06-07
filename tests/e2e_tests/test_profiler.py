"""Test real-world gh-profiler calls.

Makes an actual gh-profiler call. Currently calls against my own user account
(ehmatthes). It would be good to find another target, but I'm not sure what
to use.
"""

import subprocess
import re

import pytest

from gh_profiler.utils import infra_utils


# --- Helper functions ---

def run_with_timeout(cmd):
    """Run gh-profiler command, with a timeout."""
    num_attempts = 0
    while num_attempts < 5:
        try:
            result = infra_utils.run_cmd(cmd, timeout=5)
            output = result.stdout
        except subprocess.TimeoutExpired:
            print("Time out.")
            num_attempts += 1
        else:
            # Did not time out, but check that we got a response.
            if output:
                return output
            else:
                print("Got an empty response.")
                num_attempts += 1
                continue
    
    # Skip this entire module if there are too many timeouts.
    msg = "Too many timeouts."
    pytest.skip(msg, allow_module_level=True)


# --- Test functions ---

@pytest.mark.parametrize("target", ["ehmatthes", 1, 3])
def test_full_run(target):
    """Test a standard run of gh-profiler.
    
    Parametrization tests the three main usages:
    - target is a GitHub username
    - target is an issue number (1)
    - target is a PR number (3)
    """
    cmd = f"uv run gh-profiler {target}"
    output = run_with_timeout(cmd)

    if output == "":
        msg = "Output was empty, which may indicate a gh timeout rather than a problem with the code."
        pytest.fail(msg)

    # Make assertions about stable parts of output, not entire output string.
    # Start with user information:
    if target == "ehmatthes":
        expected_strings = ["GitHub user: ehmatthes"]
    else:
        expected_strings = ["Author: ehmatthes"]

    # Issue and PR title:
    if target == 1:
        expected_strings += ["Issue #1: Quick post-POC cleanup"]
    elif target == 3:
        expected_strings += ["PR #3: Use a single shared data structure to store all information about user."]

    # DEV: Find some assertions to make about PRs and issues?
    expected_strings += [
        "🟢 Profile information:",
        "name: Eric Matthes",
        "mastodon: https://fosstodon.org/@ehmatthes",
        "Empty fields: company, bio",
        "Orgs: openlearningtools, django-simple-deploy",
    ]

    for expected_string in expected_strings:
        assert expected_string in output

def test_concise_run():
    """Test a --concise run of gh-profiler."""
    cmd = "uv run gh-profiler ehmatthes --concise"
    output = run_with_timeout(cmd)

    if output == "":
        msg = "Output was empty, which may indicate a gh timeout rather than a problem with the code."
        pytest.fail(msg)

    # Make assertions about stable parts of output, not entire output string.
    # DEV: Find some assertions to make about PRs and issues?
    expected_strings = (
        "GitHub user: ehmatthes",
        "🟢 No concerns found with user's profile.",
        "🟢 No concerns found with recent PR activity.",
        "🟢 No concerns found with recent issue activity.",
        "For a more detailed report, run `gh-profiler ehmatthes`.",
    )

    for expected_string in expected_strings:
        assert expected_string in output

def test_redact():
    """Test a --redact run of gh-profiler."""
    cmd = "uv run gh-profiler ehmatthes --redact"
    output = run_with_timeout(cmd)

    if output == "":
        msg = "Output was empty, which may indicate a gh timeout rather than a problem with the code."
        pytest.fail(msg)

    # Make assertions about stable parts of output, not entire output string.
    redacted_strings = (
        "ehmatthes",
        "Eric Matthes",
        "https://mostlypython.com",
        "western North Carolina",
        "gmail.com",
        "fosstodon",
        "openlearningtools",
    )

    for redacted_string in redacted_strings:
        assert redacted_string not in output

    # Should currently see 7 redacted fields in my output.
    assert output.count("<redacted>") == 7

def test_bulk_open_prs():
    """Test a run against a repo URL for bulk processing open PRs."""
    # Django is likely to have many open PRs.
    url = "https://github.com/django/django"
    cmd = f"uv run gh-profiler {url} -n 3"
    output = run_with_timeout(cmd)

    assert output.count("https://github.com/django/django/pull/") == 6
    assert output.count("GitHub user: ") == 3

    # Check that there are 3 PR numbers and titles in output.
    re_pr_title = r"(PR \d+: ).*"
    matches = re.findall(re_pr_title, output)
    assert len(matches) == 3


def test_bulk_open_prs_table_only():
    """Test a table-only run against a repo URL for bulk processing open PRs."""
    # Django is likely to have many open PRs.
    url = "https://github.com/django/django"
    cmd = f"uv run gh-profiler {url} -n 3 --table-only"
    output = run_with_timeout(cmd)

    assert output.count("https://github.com/django/django/pull/") == 3
    assert "GitHub user: " not in output
    assert "Merged." not in output
    assert "Closed." not in output

    # Make sure Merged? column is not in output for open PRs.
    assert "Merged?" not in output

    # Check that there are no PR numbers and titles in output.
    re_pr_title = r"(PR \d+: ).*"
    matches = re.findall(re_pr_title, output)
    assert len(matches) == 0


def test_bulk_closed_prs():
    """Test a run against a repo URL for bulk processing closed PRs."""
    # Django is likely to have many closed PRs.
    url = "https://github.com/django/django"
    cmd = f"uv run gh-profiler {url} --back -n 3"
    output = run_with_timeout(cmd)

    assert output.count("https://github.com/django/django/pull/") == 6
    assert output.count("GitHub user: ") + output.count("`ghost`") == 3
    assert output.count("Merged.") + output.count("Closed.") == 3

    # Check that there are 3 PR numbers and titles in output.
    re_pr_title = r"(PR \d+: ).*"
    matches = re.findall(re_pr_title, output)
    assert len(matches) == 3


def test_bulk_closed_prs_table_only():
    """Test a table-only run against a repo URL for bulk processing closed PRs."""
    # Django is likely to have many closed PRs.
    url = "https://github.com/django/django"
    cmd = f"uv run gh-profiler {url} --back -n 3 --table-only"
    output = run_with_timeout(cmd)

    assert output.count("https://github.com/django/django/pull/") == 3
    assert "GitHub user: " not in output
    assert "Merged." not in output
    assert "Closed." not in output

    # Check that there are no PR numbers and titles in output.
    re_pr_title = r"(PR \d+: ).*"
    matches = re.findall(re_pr_title, output)
    assert len(matches) == 0


@pytest.mark.parametrize("mode", ["", "--concise"])
def test_ghost_profile(mode):
    """Test a run against the `ghost` user.

    GitHub has a special user account named `ghost` that stands in for
    deleted users in completed actions, such as closed PRs.

    This should return a single red flag, with an explanation of this role.

    See: https://github.com/ghost
    """
    cmd = f"uv run gh-profiler ghost {mode}"
    output = run_with_timeout(cmd)

    assert output.strip() == f"🔴 The `ghost` account is GitHub's reference to a deleted user."
