"""Run tests against real-world users.

This test runs against a set of users known to have all green appropriate
behaviors, and users known to have problematic behaviors.

It fails on any non-green flag in known green user profiles.
It fails on all-green results for known problematic users.

The user lists are entirely private and will never be in the public repo. This
test helps make sure we're not accidentally flagging appropriate behaviors, or
missing inappropriate behaviors.

When this test fails, it doesn't necessarily mean there's a problem with
gh-profiler. When it fails, we should look at that user's profile. If
they're expected to be all green, we should see if there's a legitimate
behavior that's being flagged. If they're expected to raise yellow or red flags,
we should see if the user has stopped being active, has improved their activity,
or if we're missing something.

The target file should be a .toml file, with two lists: green_users, and
non_green_users. We're using TOML so we can have comments in the data file.
I like to keep track of why I'm testing against certain users. You can see a
sample actual_users.toml file in developer_resources/.

Running this test:
    uv run pytest developer_resources/test_actual_users.py -s

If your data file isn't being found, you can see what path is being used
with this command:
    uv run pytest developer_resources/test_actual_users.py -rs
"""

from pathlib import Path
import tomllib
import subprocess
import os

import pytest

from gh_profiler.utils import infra_utils
from gh_profiler.utils import flags


# --- Helper functions ---

def get_users(category):
    """Return data object containing green and non-green user lists."""
    path = os.environ.get("PATH_ACTUAL_USERS", None)
    if path:
        path = Path(path)
    else:
        path_src_dir = Path(__file__).parents[2]
        path = path_src_dir / "gh-profiler_support" / "actual_users.toml"
    
    if not path.exists():
        msg = f"No actual_users.toml file found. Tried {path}"
        pytest.skip(msg, allow_module_level=True)

    with path.open("rb") as f:
        data = tomllib.load(f)
    
    if category == "green":
        return data["green_users"]
    elif category == "non_green":
        return data["non_green_users"]

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
    
    msg = "Too many timeouts."
    pytest.exit(msg)


# --- Test functions ---

@pytest.mark.parametrize("username", get_users("green"))
def test_green_users(username):
    """Run gh-profiler against known green users.
    
    We should not find any yellow or red flags for these users.
    """
    print(f"\nTesting against green user {username}")
    cmd = f"uv run gh-profiler {username} --concise"
    output = run_with_timeout(cmd)

    assert flags.yellow_flag not in output
    assert flags.red_flag not in output

@pytest.mark.parametrize("username", get_users("non_green"))
def test_non_green_users(username):
    """Run gh-profiler against known non-green users.
    
    We should find at least one yellow or red flag for these users.
    """
    print(f"\nTesting against non-green user {username}")
    cmd = f"uv run gh-profiler {username} --concise"
    output = run_with_timeout(cmd)

    assert flags.yellow_flag in output or flags.red_flag in output
