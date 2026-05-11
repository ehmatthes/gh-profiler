"""Utils for the gh-profiler CLI."""

import json
import sys


from .infra_utils import run_cmd
from .profile_data import profile_data as pdata


def process_pr_issue_num(pr_issue_num):
    """Get the user that opened this PR/issue, and PR/issue title."""
    repo_slug = _get_repo_slug()

    # Try as a PR, then as an issue.
    if username := _process_pr(pr_issue_num, repo_slug):
        pdata.username = username
    elif username := _process_issue(pr_issue_num, repo_slug):
        pdata.username = username
    else:
        msg = f"Couldn't find a PR or issue #{pr_issue_num} in the repository {repo_slug}."
        sys.exit(msg)


# --- Helper functions ---


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
    # pr_cmd = f'gh pr view {pr_issue_num} --repo {repo_slug} --json author --jq ".author.login"'
    pr_cmd = f"gh pr view {pr_issue_num} --repo {repo_slug} --json author --json title"
    try:
        results = run_cmd(pr_cmd)
        results_json = json.loads(results)

        pdata.is_pr = True
        pdata.pr_number = pr_issue_num
        pdata.pr_title = results_json["title"]

        return results_json["author"]["login"]

    except json.JSONDecodeError:
        return None


def _process_issue(pr_issue_num, repo_slug):
    """See if this is an issue."""
    issue_cmd = (
        f"gh issue view {pr_issue_num} --repo {repo_slug} --json author --json title"
    )
    try:
        results = run_cmd(issue_cmd)
        results_json = json.loads(results)

        pdata.is_issue = True
        pdata.issue_number = pr_issue_num
        pdata.issue_title = results_json["title"]

        return results_json["author"]["login"]

    except json.JSONDecodeError:
        # Target was an int, but isn't a PR or an issue.
        msg = f"Couldn't find a PR or issue #{pr_issue_num} in the repository {repo_slug}."
        sys.exit(msg)
