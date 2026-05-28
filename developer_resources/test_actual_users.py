"""Run tests against real-world users.

This test runs against a set of users known to have all green appropriate
behaviors, and users known to have problematic behaviors.

It fails on any non-green flag in known green user profiles.
It fails on all-green results for known problematic users.

The user lists are entirely private and will never be posted publicly. This is
meant to help make sure we're not actually flagging appropriate behaviors, or
not catching inappropriate behaviors.

When a test fails, it doesn't necessarily mean there's a problem with
gh-profiler. When this test fails, we should look at that user's profile. If
they are expected to be all green, we should see if there's a legitimate
behavior that's being flagged. If they're expected not to be all green, we 
should see if the user has stopped being active, has improved their activity,
or if we're just not catching something.

The target file should be a .toml file, with two lists:
  green_users, and non_green_users.
We're using TOML so we can have comments in the data file. I like to keep track
of why I'm testing against certain users.
"""

from pathlib import Path
import tomllib
import subprocess
import os

import pytest

from gh_profiler.utils import infra_utils
from gh_profiler.utils import flags


# --- Fixtures ---

def get_users(category):
    """Return data object containing green and non-green user lists."""
    path = os.environ.get("PATH_ACTUAL_USERS", None)
    if path:
        path = Path(path)
    else:
        path_src_dir = Path(__file__).parents[2]
        path = path_src_dir / "gh-profiler_support" / "actual_users.toml"
    
    if not path.exists():
        msg = "No actual_users.py file found."
        pytest.exit(msg)

    with path.open("rb") as f:
        data = tomllib.load(f)
    
    if category == "green":
        return data["green_users"]
    elif category == "non_green":
        return data["non_green_users"]


# --- Helper functions ---

def run_with_timeout(cmd):
    """Run gh-profiler command, with a timeout."""
    num_attempts = 0
    while num_attempts < 5:
        try:
            output = infra_utils.run_cmd(cmd, timeout=5)
        except subprocess.TimeoutExpired:
            print("Time out.")
            num_attempts += 1
        else:
            return output
    
    msg = "Too many timeouts."
    pytest.exit(msg)


# --- Test functions ---


@pytest.mark.parametrize("username", get_users("green"))
def test_green_users(username):
    """Run gh-profiler against known green users."""
    print(f"\nTesting against green user {username}")
    cmd = f"uv run gh-profiler {username} --concise"
    output = run_with_timeout(cmd)

    assert output.count(flags.green_flag) == 3

def test_non_green_users():
    """Run gh-profiler against known non-green users."""
    non_green_users = get_users("non_green")
    print("\n\nTesting non-green users...")
    for username in non_green_users:
        print(f"  Testing against non-green user {username}")
        cmd = f"uv run gh-profiler {username} --concise"
        output = run_with_timeout(cmd)

        assert output.count(flags.green_flag) < 3
