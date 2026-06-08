"""Utils for analyzing repo data."""

from .profile_data import profile_data as pdata
from . import profile_utils, analysis_utils, summary_utils
from . import flags
from .cli_config import cli_config

from rich.console import Console
from rich.table import Table


def process_data(target_prs):
    """Process a list of PRs.
    
    Takes a list of PRData objects.
    Calls gh-profiler on each PR author.
    Evaluates results.
    """
    if cli_config.table_only:
        print("Fetching user profiles ", end="", flush=True)
        
    for pr in target_prs:
        # Get concise gh-profiler output for PR author.
        pdata.reset_fields()
        pdata.username = pr.author

        if author_info := _get_cached_author_info(pdata.username, target_prs):
            # breakpoint()
            pr.author_summary, pr.profile_flag, pr.pr_flag, pr.issue_flag = author_info
        else:
            profile_utils.get_data()
            analysis_utils.process_data()
            pr.author_summary = summary_utils._get_concise_summary()

            pr.profile_flag = pdata.flag_overall_profile
            pr.pr_flag = pdata.flag_overall_pr
            pr.issue_flag = pdata.flag_overall_issues

        pr.summary = _get_pr_summary(pr, pr.author_summary)

        # DEV: Print the summary here while we're not doing this in parallel.
        # When these are being processed in parallel, we'll remove this line
        # and call show_summary() from gh_profiler.
        # Also, redacting here for now.
        if cli_config.redact:
            pr.author = "<redacted>"

        if cli_config.table_only:
            print(".", end="", flush=True)
        else:
            print(pr.summary)

    if cli_config.table_only:
        print("\n")
    show_table(target_prs)

def _get_cached_author_info(username, target_prs):
    """Get an existing author summary if it's already been built."""
    author_prs = [pr for pr in target_prs if pr.author == username]

    for pr in author_prs:
        if pr.author_summary:
            return (
                pr.author_summary,
                pr.profile_flag,
                pr.pr_flag,
                pr.issue_flag,
            )


def show_table(target_prs):
    """Show table of results.
    
    If looking back, show final merged state as well.
    """
    table = Table(title="Comparison of gh-profiler results with final merged state:")

    table.add_column("PR num", justify="center")
    if cli_config.back:
        table.add_column("Merged?", justify="center")
    table.add_column("gh-profiler")
    table.add_column("Author", no_wrap=True)
    table.add_column("PR link", no_wrap=True)

    for pr in target_prs:
        if cli_config.back:
            if pr.merged:
                merged_flag = flags.merged_flag
            else:
                merged_flag = flags.red_flag
        
        profile_flags = "".join([pr.profile_flag, pr.pr_flag, pr.issue_flag])

        if cli_config.back:
            table.add_row(str(pr.pr_num), merged_flag, profile_flags, pr.author, pr.url)
        else:
            table.add_row(str(pr.pr_num), profile_flags, pr.author, pr.url)

    console = Console()
    console.print(table)

        
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

    pr_summary = f"PR {pr.pr_num}: {pr.title.strip()}"
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
    if not cli_config.back:
        return f"\n{pr.url}\n\n"
    
    if pr.merged:
        status = f"{flags.merged_flag} Merged."
    else:
        status = f"{flags.red_flag} Closed."

    return f"\n{status} {pr.url}\n\n"
    
