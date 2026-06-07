"""Utils for analyzing repo data."""

from .profile_data import profile_data as pdata
from . import profile_utils, analysis_utils, summary_utils
from . import flags
from .cli_config import cli_config


def process_data(target_prs):
    """Process a list of PRs.
    
    Takes a list of PRData objects.
    Calls gh-profiler on each PR author.
    Evaluates results.
    """
    for pr in target_prs:
        # Get concise gh-profiler output for PR author.
        pdata.username = pr.author
        profile_utils.get_data()
        analysis_utils.process_data()
        author_summary = summary_utils._get_concise_summary()
        pr.summary = _get_pr_summary(pr, author_summary)

        # DEV: Print the summary here while we're not doing this in parallel.
        # When these are being processed in parallel, we'll remove this line
        # and call show_summary() from gh_profiler.
        print(pr.summary)

        
def _adjust_author_summary(summary):
    """Modify standard concise output to fit bulk reporting needs.

    - Remove closing line about running a detailed report.
    - Indent lines
    """
    lines = summary.splitlines()

    if pdata.username != "ghost":
        # Remove "For a more detailed report..."
        lines = lines[:-2]

    # Indent lines.
    lines = [f"  {l}" for l in lines]

    return "\n".join(lines)

def _get_pr_summary(pr, author_summary):
    """Get the summary for an individual PR."""
    author_summary = _adjust_author_summary(author_summary)

    pr_summary = f"PR {pr.pr_num}: {pr.title}"
    pr_summary += _get_status_line(pr)
    pr_summary += author_summary
    pr_summary += "\n\n"

    return pr_summary

def _get_status_line(pr):
    """Get the line that shows the status of the PR.

    For open PRs, no symbol.
    For closed PRs, flag and state.
    For all, this is where the PR URL goes as well.
    """
    # breakpoint()
    if not cli_config.back:
        return f"\n{pr.url}\n\n"
    
    if pr.closed_state == "MERGED":
        status = f"{flags.merged_flag} Merged."
    else:
        status = f"{flags.red_flag} Closed."

    return f"\n{status} {pr.url}\n\n"
    
