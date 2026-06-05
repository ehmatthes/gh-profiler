"""Test real-world gh-profiler calls.

Makes an actual gh-profiler call. Currently calls against my own user account
(ehmatthes). It would be good to find another target, but I'm not sure what
to use.
"""

import sys
import subprocess

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
    # DEV: Find some assertions to make about PRs and issues?
    if target == "ehmatthes":
        expected_strings = ["GitHub user: ehmatthes"]
    else:
        expected_strings = ["Author: ehmatthes"]

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
