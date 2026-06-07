"""Utils for analyzing repo data."""

from .profile_data import profile_data as pdata
from . import profile_utils, analysis_utils, summary_utils
from . import flags


def process_data(target_prs):
    """Process a list of PRs.
    
    Takes a list of PRData objects.
    Calls gh-profiler on each PR author.
    Evaluates results.
    """
    for pr in target_prs:
        # Get concise gh-profiler output for author.
        pdata.username = pr.author
        # breakpoint()
        profile_utils.get_data()
        analysis_utils.process_data()
        summary = summary_utils._get_concise_summary()

        print(f"\nPR number: {pr.pr_num}")
        print(f"  {pr.title}")
        print(summary)

