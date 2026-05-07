"""Utils for retrieving user information."""

import json
from datetime import datetime as dt
from datetime import timezone as tz
from datetime import timedelta
from textwrap import dedent
import sys

from .profile_data import profile_data as pdata
from . import infra_utils


def ensure_gh():
    """Make sure user has gh installed and is authenticated.

    Check for authentication issues in first external call, rather than making
    a call just for that purpose here.
    """
    cmd = "gh --version"
    try:
        version_info = infra_utils.run_cmd(cmd)
    except FileNotFoundError:
        msg = "The GitHub CLI tool (gh) must be installed."
        msg += "\n  https://cli.github.com"
        sys.exit(msg)


def get_data():
    """Get all data we'll need from GitHub."""
    _get_profile_dict()
    _get_pr_activity()
    _get_issue_activity()


# --- Helper functions ---


def _get_profile_dict():
    """Get all the profile information we'll need."""
    cmd = f"gh api users/{pdata.username} --jq '{{login, name, created_at, company, blog, location, email, bio}}'"

    profile_dict_str = infra_utils.run_cmd(cmd)
    _ensure_authenticated(profile_dict_str)

    try:
        pdata.profile_dict = json.loads(profile_dict_str)
    except json.decoder.JSONDecodeError:
        msg = "Couldn't get GitHub profile info. The gh CLI may have timed out."
        msg += "\n  You may want to try running the command again."
        sys.exit(msg)

    if "created_at" not in pdata.profile_dict:
        sys.exit(f"GitHub user '{pdata.username}' not found.")

    # On Linux, an invalid profile seems to return a dict with all the fields,
    # but every value is None.
    if pdata.profile_dict["created_at"] is None:
        sys.exit(f"GitHub user '{pdata.username}' not found.")


def _get_pr_activity():
    """Get information about recent PR activity."""
    cutoff = (dt.now(tz.utc) - timedelta(days=21)).date().isoformat()

    pr_query = _get_pr_query()
    search_query = f"author:{pdata.username} is:pull-request created:>={cutoff}"
    cmd = f"gh api graphql -f query='{pr_query}' -F q='{search_query}' -F n=100"

    try:
        data = json.loads(infra_utils.run_cmd(cmd))
    except json.decoder.JSONDecodeError:
        msg = "Couldn't get recent PR activity. The gh CLI may have timed out."
        msg += "\n  You may want to try running the command again."
        sys.exit(msg)

    search = data["data"]["search"]
    prs = search["nodes"]

    pdata.opened_count = len(prs)
    pdata.merged_count = sum(pr["mergedAt"] is not None for pr in prs)
    pdata.closed_count = sum(
        pr["state"] == "CLOSED" and pr["mergedAt"] is None for pr in prs
    )


def _get_issue_activity():
    """Get target user's recent public issue activity."""
    cutoff = (dt.now(tz.utc) - timedelta(days=21)).date().isoformat()
    gh_call = _get_gh_issues_call(pdata.username, cutoff)
    try:
        issue_activity = infra_utils.run_cmd(gh_call)
    except ValueError:
        msg = "Couldn't get recent issue activity. The gh CLI may have timed out."
        msg += "\n  You may want to try running the command again."
        sys.exit(msg)

    try:
        pdata.issue_activity = json.loads(issue_activity)["data"]["search"]
    except (json.decoder.JSONDecodeError, KeyError):
        msg = "Couldn't get recent issue activity. The gh CLI may have timed out."
        msg += "\n  You may want to try running the command again."
        sys.exit(msg)


def _ensure_authenticated(profile_dict_str):
    """Check that the gh CLI tool has been authenticated.

    This should be called when the first external gh call is made.
    Making this check on the output of an actual call is more efficent than
    calling `gh api user --jq .login` just to verify authentication.
    """
    if not profile_dict_str.strip():
        msg = "The GitHub CLI tool (gh) is not authenticated, or the API hung."
        msg += "\n  If you've already authenticated, try running the gh-profiler command again."
        msg += "\n  If you're not authenticated, run `gh auth login`."
        sys.exit(msg)


def _get_gh_issues_call(username, cutoff):
    """Return the gh call for recent public issue activity."""
    gh_call = f"""
        gh api graphql -f query='
        query($q: String!, $n: Int!) {{
        search(query: $q, type: ISSUE, first: $n) {{
            issueCount
            pageInfo {{
            hasNextPage
            endCursor
            }}
            nodes {{
            ... on Issue {{
                number
                title
                createdAt
                state
                stateReason
                url
                repository {{
                nameWithOwner
                }}
            }}
            }}
        }}
        }}' -F q='author:{username} is:issue is:public created:>={cutoff}' -F n=100
    """

    return dedent(gh_call).strip()


def _get_pr_query():
    """Return the graphql query for recent PR activity."""
    pr_query = f"""
        query($q: String!, $n: Int!) {{
            search(query: $q, type: ISSUE, first: $n) {{
                issueCount
                pageInfo {{
                hasNextPage
                endCursor
                }}
                nodes {{
                ... on PullRequest {{
                    number
                    state
                    createdAt
                    closedAt
                    mergedAt
                    url
                }}
                }}
            }}
            }}
    """

    return dedent(pr_query).strip()
