"""Main CLI entry point for gh-profiler."""

import json
import sys

import click

from . import gh_profiler
from .utils.infra_utils import run_cmd


@click.command()
@click.argument("target")
def main(target):
    """Examine a GitHub user's profile, to help quickly decide how much to invest in their contributions.
    
    You can target a GitHub username, or a PR/issue number from the repository you're working in.

    \b
    Usage as a tool:
    $ uvx gh-profiler ehmatthes
    $ uvx gh-profiler 8

    \b
    Usage when installing gh-profiler:
    $ gh-profiler ehmatthes
    $ python -m gh_profiler ehmatthes
      ...
    """

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
    repo_slug = _get_repo_slug()
    
    # Try as a PR, then as an issue.
    if username := _process_pr(pr_issue_num, repo_slug):
        return username
    if username := _process_issue(pr_issue_num, repo_slug):
        return username

    msg = f"Couldn't find a PR or issue #{pr_issue_num} in the repository {repo_slug}."
    sys.exit(msg)

def _get_repo_slug():
    """Ask `gh` for the resolved default repo (honors `gh repo set-default`)."""
    slug = run_cmd("gh repo view --json nameWithOwner --jq .nameWithOwner").strip()
    if not slug:
        msg = (
            "Couldn't determine the default GitHub repository. "
            "Run `gh repo set-default` in this directory and try again."
        )
        sys.exit(msg)
    return slug

def _process_pr(pr_issue_num, repo_slug):
    """See if this is a PR."""
    pr_cmd = f'gh pr view {pr_issue_num} --repo {repo_slug} --json author --jq ".author.login"'
    try:
        if username := run_cmd(pr_cmd).strip():
            return username
    except Exception as e:
        breakpoint()
        return None

def _process_issue(pr_issue_num, repo_slug):
    """See if this is an issue."""
    issue_cmd = f'gh issue view {pr_issue_num} --repo {repo_slug} --json author --jq ".author.login"'
    try:
        if username := run_cmd(issue_cmd).strip():
            return username
    except Exception:
        msg = f"Couldn't find a PR or issue #{pr_issue_num} in the repository {repo_slug}."
        sys.exit(msg)
