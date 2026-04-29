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

from utils import profile_utils
from utils.infra_utils import run_cmd
from utils import analysis_utils

gh_user = sys.argv[1]

red_flag = "\U0001F534"
yellow_flag = "\U0001F7E1"
green_flag = "\U0001F7E2"

def main():
    # How old is the account?
    account_age = profile_utils.get_account_age(gh_user)
    flag_age = analysis_utils.process_account_age(account_age)

    # What does recent PR activity look like?
    pr_counts = profile_utils.get_pr_activity(gh_user)
    opened_count, merged_count, closed_count = pr_counts
    flag_closed_pr, flag_merged_pr = analysis_utils.process_pr_activity(pr_counts)


    # How much of the profile is filled out?
    # email? website? social?

    # Summarize findings.
    print(f"\nGitHub user: {gh_user}")
    print(f"  {flag_age} Account age: {account_age.days} days")

    if opened_count >= 10:
        # Only show merged if it's a good sign.
        if flag_merged_pr == green_flag:
            print(f"  {flag_merged_pr} {merged_count} of {opened_count} PRs have been merged in the last 21 days.")
        print(f"  {flag_closed_pr} {closed_count} of {opened_count} PRs have been closed without merging in the last 21 days.")
    else:
        print(f"  {green_flag} {gh_user} has opened fewer than 10 PRs in the last 21 days.")
    print("")


if __name__ == "__main__":
    main()
