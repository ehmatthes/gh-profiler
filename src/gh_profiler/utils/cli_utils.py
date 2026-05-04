"""Utils for the gh-profiler CLI."""

import sys


from .infra_utils import run_cmd


def get_username(pr_issue_num):
    """Get the user that opened this PR/issue."""
    repo_slug = _get_repo_slug()

    # Try as a PR, then as an issue.
    if username := _process_pr(pr_issue_num, repo_slug):
        return username
    if username := _process_issue(pr_issue_num, repo_slug):
        return username

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
