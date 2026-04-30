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

from datetime import datetime as dt
from datetime import timezone as tz
from datetime import timedelta
import subprocess
import sys
import shlex
import json

from profile_data import profile_data
from utils import profile_utils
from utils.infra_utils import run_cmd
from utils import analysis_utils
from utils import summary_utils


gh_user = sys.argv[1]
profile_data.username = gh_user

def main():
    # How old is the account?
    profile_utils.get_account_age()
    analysis_utils.process_account_age()

    # What does recent PR activity look like?
    pr_counts = profile_utils.get_pr_activity()
    opened_count, merged_count, closed_count = pr_counts
    flag_closed_pr, flag_merged_pr = analysis_utils.process_pr_activity(pr_counts)

    # Summarize findings.
    summary_utils.show_summary(
        gh_user,
        opened_count,
        merged_count,
        closed_count,
        flag_merged_pr,
        flag_closed_pr,
    )


if __name__ == "__main__":
    main()
