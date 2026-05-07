"""Examine a user's profile, and highlight evidence they're human or AI.

The goal is to help make quick, evidence-based decisions about how much time
to invest in reviewing PRs, and general interaction on open source projects.
"""

import sys

from .utils import profile_utils
from .utils import analysis_utils
from .utils import summary_utils


def main():
    # Make sure gh is available.
    profile_utils.ensure_gh()

    # Get all data we'll need from GitHub.
    profile_utils.get_data()




    # How old is the account?
    analysis_utils.process_account_age()

    # How much profile information is available?
    analysis_utils.process_profile_info()

    # What does recent PR activity look like?
    analysis_utils.process_pr_activity()

    # What does recent issue activity look like?
    analysis_utils.process_issue_activity()

    # Summarize findings.
    summary_utils.show_summary()

    # Finished, don't return control to cli.py.
    sys.exit()
