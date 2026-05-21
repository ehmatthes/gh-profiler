"""Test real-world gh-profiler calls.

Makes an actual gh-profiler call. Currently calls against my own user account
(ehmatthes). It would be good to find another target, but I'm not sure what
to use.
"""

import pytest

from gh_profiler.utils import infra_utils


def test_full_run():
    """Test a standard run of gh-profiler."""
    cmd = "uv run gh-profiler ehmatthes"
    output = infra_utils.run_cmd(cmd)

    if output == "":
        msg = "Output was empty, which may indicate a gh timeout rather than a problem with the code."
        pytest.fail(msg)

    # Make assertions about stable parts of output, not entire output string.
    # DEV: Find some assertions to make about PRs and issues?
    expected_strings = (
        "GitHub user: ehmatthes",
        "🟢 Profile information:",
        "name: Eric Matthes",
        "mastodon: https://fosstodon.org/@ehmatthes",
        "Empty fields: company, bio",
    )

    for expected_string in expected_strings:
        assert expected_string in output

def test_concise_run():
    """Test a --concise run of gh-profiler."""
    cmd = "uv run gh-profiler ehmatthes --concise"
    output = infra_utils.run_cmd(cmd)

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
