"""Examine a user's profile, and highlight evidence they're human or AI.

The goal is to help make quick, evidence-based decisions about how much time
to invest in reviewing PRs, and general interaction on open source projects.

Scores:
3: green
2: yellow
1: red

Package, so usage can be:
$ uvx gh-profiler ehmatthes

Or, maybe from within a project:
$ uvx gh-profiler <pr-num>

Given a PR number, it finds the author of the PR and runs the profiler on that
user?
"""

import sys

from profile_data import profile_data as pdata
from utils import profile_utils
from utils import analysis_utils
from utils import summary_utils


gh_user = sys.argv[1]
pdata.username = gh_user


def main():
    # Get all information we'll need about the user's profile.
    profile_utils.get_profile_info()

    # How old is the account?
    analysis_utils.process_account_age()

    # How much profile information is available?
    analysis_utils.process_profile_info()

    # What does recent PR activity look like?
    profile_utils.get_pr_activity()
    analysis_utils.process_pr_activity()

    # Summarize findings.
    summary_utils.show_summary()


if __name__ == "__main__":
    main()
