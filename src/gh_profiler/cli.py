"""Main CLI entry point for gh-profiler."""

import json
import re
import sys

import click

from . import gh_profiler
from .utils.infra_utils import run_cmd


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
    remote_output = run_cmd("git remote -v")
    match = re.search(
        r"github\.com[:/](?P<owner>[^/\s]+)/(?P<repo>[^.\s]+)(?:\.git)?\s",
        remote_output,
    )
    if not match:
        msg = f"Couldn't determine appropriate required information from `git remote -v`."
        sys.exit(msg)

    owner = match.group("owner")
    repo = match.group("repo")
    repo_slug = f"{owner}/{repo}"

    # See if this is a PR.
    pr_cmd = (
        f'gh pr view {pr_issue_num} '
        f'--repo {repo_slug} '
        f'--json author '
        f'--jq ".author.login"'
    )
    try:
        username = run_cmd(pr_cmd).strip()
        if username:
            return username

    except Exception:
        # The number wasn't a PR.
        pass

    # Then try as an issue.
    issue_cmd = (
        f'gh issue view {pr_issue_num} '
        f'--repo {repo_slug} '
        f'--json author '
        f'--jq ".author.login"'
    )
    try:
        username = run_cmd(issue_cmd).strip()
        if username:
            return username
    except Exception:
        msg = f"Couldn't find a PR or issue #{pr_issue_num} in the repository {repo_slug}."
        sys.exit(msg)
