"""Main CLI entry point for gh-profiler."""

import click

from . import gh_profiler


@click.command()
@click.argument("target")
def main(target):
    """Process user's gh-profiler command."""

    # If the main argument is an integer, process the PR/issue number.
    # Otherwise, assume it's the username.
    try:
        pr_issue_num = int(target)
    except ValueError:
        gh_profiler.main(target)
    
    # The user provided a PR/issue number. Get the relevant username, then
    # call gh_profiler.main().
    username = _get_username(pr_issue_num)
    gh_profiler.main(username)


# --- Helper functions ---

def _get_username(pr_issue_num):
    """Get the user that opened this PR/issue."""
    ...