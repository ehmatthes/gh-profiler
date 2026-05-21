"""Utils for retrieving user information."""

import json
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime as dt
from datetime import timedelta
from datetime import timezone as tz
from textwrap import dedent
from time import perf_counter

from . import infra_utils
from .profile_data import profile_data as pdata


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
    """Get all data we'll need from GitHub.
    
    Fetch all data we'll need, then parse it into the data structures that
    can be analyzed and processed.
    """
    # This is the first call, and it checks if the user exists. This call needs
    # to happen before all others.
    _get_profile_dict()

    # Fetch data. This can all be done in parallel. The benchmarking is here
    # because this is the slowest part of the program, and it's helpful at
    # times to benchmark just this block of code.
    ts_before = perf_counter()
    with ThreadPoolExecutor() as executor:
        socials_future = executor.submit(_fetch_socials)
        pr_activity_future = executor.submit(_fetch_pr_activity)
        issue_activity_future = executor.submit(_fetch_issue_activity)

        socials_str = socials_future.result()
        pr_activity_str = pr_activity_future.result()
        issue_activity_str = issue_activity_future.result()

    ts_after = perf_counter()
    if pdata.benchmark_fetch:
        print(f"Fetch data: {ts_after - ts_before:.2f} seconds")

    # Parse data. This should only happen after all data has been fetched.
    _parse_socials(socials_str)
    _parse_pr_activity(pr_activity_str)
    _parse_issue_activity(issue_activity_str)


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

def _fetch_socials():
    """Fetch social media accounts from user's profile.
    
    Social media accounts from profiles are a separate endpoint, so I believe
    they require an additional API call.
    """
    cmd = f"gh api users/{pdata.username}/social_accounts"
    return infra_utils.run_cmd(cmd)

def _parse_socials(socials_str):
    """Parse the data string returned from _fetch_socials()."""
    try:
        pdata.socials = json.loads(socials_str)
    except json.decoder.JSONDecodeError:
        msg = "Couldn't get GitHub profile info. The gh CLI may have timed out."
        msg += "\n  You may want to try running the command again."
        sys.exit(msg)


def _fetch_pr_activity():
    """Fetch information about recent PR activity."""
    cutoff = (dt.now(tz.utc) - timedelta(days=21)).date().isoformat()

    pr_query = _get_pr_query()
    search_query = (
        f"author:{pdata.username} is:pull-request is:public created:>={cutoff}"
    )
    cmd = f"gh api graphql -f query='{pr_query}' -F q='{search_query}' -F n=100"
    return infra_utils.run_cmd(cmd)

def _parse_pr_activity(pr_activity_str):
    """Parse the data returned by _fetch_pr_activity()."""
    try:
        data = json.loads(pr_activity_str)
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


def _fetch_issue_activity():
    """Fetch target user's recent public issue activity."""
    cutoff = (dt.now(tz.utc) - timedelta(days=21)).date().isoformat()
    gh_call = _get_gh_issues_call(pdata.username, cutoff)
    return infra_utils.run_cmd(gh_call)

def _parse_issue_activity(issue_activity_str):
    """Parse data returned by _fetch_issue_activity()."""
    try:
        pdata.issue_activity = json.loads(issue_activity_str)["data"]["search"]
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
