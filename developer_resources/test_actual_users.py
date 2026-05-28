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

The target file should be a .py file, with two lists:
  green_users, and non_green_users.
"""

from pathlib import Path

import pytest


@pytest.fixture()
def path_actual_usernames(request):
    path = request.config.getoption("--path-actual-usernames")
    if path:
        path = Path(path)
    else:
        path_src_dir = Path(__file__).parents[2]
        path = path_src_dir / "gh-profiler_support" / "actual_users.py"
    
    if path.exists():
        return path
    else:
        msg = "No actual_users.py file found."
        breakpoint()
        pytest.exit(msg)



def test_actual_users(path_actual_usernames):
    """Run gh-profiler against actual users, and look for appropriate flags.
    """
    assert False    
