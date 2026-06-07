"""Examine a user's profile, and highlight evidence they're human or AI.

The goal is to help make quick, evidence-based decisions about how much time
to invest in reviewing PRs, and general interaction on open source projects.
"""

import sys

from .utils.profile_data import profile_data as pdata
from .utils import profile_utils
from .utils import analysis_utils
from .utils import workflow_utils
from .utils import summary_utils
from .utils import repo_fetching, repo_analysis, repo_summary


def main():
    # Generate new workflow, if that's what was requested.
    if pdata.generate_workflow:
        workflow_utils.generate_workflow()
        sys.exit()

    # Make sure gh is available.
    profile_utils.ensure_gh()

    # Get and analyze all data we'll need from GitHub.
    profile_utils.get_data()
    analysis_utils.process_data()

    # Summarize findings.
    summary_utils.show_summary()

    # Don't return to cli.
    sys.exit()

def profile_url():
    """Profile contributors of PRs or issues on a specific repo.
    
    Usage:
    # Profile contributors of the most recent 10 open PRs (concise):
    $ gh-profiler <repo>

    # Most recent 20 PRs:
    $ gh-profiler <repo> -n 20

    # Most recent merged/closed PRs (shows profile, and end state):
    $ gh-profiler <repo> --back

    # Most recently opened issues:
    $ gh-profiler <repo> --issues
    """
    # Make sure gh is available.
    profile_utils.ensure_gh()

    # Get and analyze all the data we'll need.
    target_prs = repo_fetching.get_data()
    repo_analysis.process_data(target_prs)

    # DEV: This will be used when bulk processing of PRs is done in parallel.
    # That requires pdata to not be a singleton.
    # repo_summary.show_summary(target_prs)

    # Don't return to cli.
    sys.exit()
