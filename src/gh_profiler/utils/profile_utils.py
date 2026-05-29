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
    """Make sure user has gh installed.

    Check for authentication issues in batch of external calls, rather than making
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
    # Fetch data. This can all be done in parallel. The benchmarking is here
    # because this is the slowest part of the program, and it's helpful at
    # times to benchmark just this fetching code.
    ts_before = perf_counter()
    with ThreadPoolExecutor() as executor:
        # Make fetching calls.
        status_future = executor.submit(_fetch_status)
        profile_dict_future = executor.submit(_fetch_profile_dict)
        socials_future = executor.submit(_fetch_socials)
        pr_activity_future = executor.submit(_fetch_pr_activity)
        issue_activity_future = executor.submit(_fetch_issue_activity)

        # When each call finishes, store the result.
        status_str = status_future.result()
        profile_dict_str = profile_dict_future.result()
        socials_str = socials_future.result()
        pr_activity_str = pr_activity_future.result()
        issue_activity_str = issue_activity_future.result()

    ts_after = perf_counter()
    if pdata.benchmark_fetch:
        print(f"Fetch data: {ts_after - ts_before:.2f} seconds")

    # Parse data. This should only happen after all data has been fetched.
    _parse_status(status_str)
    _parse_profile_dict(profile_dict_str)
    _parse_socials(socials_str)
    _parse_pr_activity(pr_activity_str)
    _parse_issue_activity(issue_activity_str)


# --- Helper functions ---

def _fetch_status():
    """Fetch output of `gh auth status`."""
    cmd = "gh auth status"
    return infra_utils.run_cmd(cmd)

def _parse_status(status_str):
    """Parse output of status call."""
    if "Logged in to github.com account " not in status_str:
        # Show the stdout part of `gh auth status`, if there is any.
        # I believe this is relevant when the user has an expired token.
        if status_str:
            msg = f"{status_str}\n"
        else:
            msg = ""

        msg += "The GitHub CLI tool (gh) is not authenticated."
        msg += "\nRun `gh auth login` to authenticate."
        sys.exit(msg)

def _fetch_profile_dict():
    """Fetch the profile information we'll need."""
    cmd = f"gh api users/{pdata.username} --jq '{{login, name, created_at, company, blog, location, email, bio}}'"
    return infra_utils.run_cmd(cmd)

def _parse_profile_dict(profile_dict_str):
    """Parse the profile information that was fetched."""
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

    # PRs against repos the user owns.
    prs_owned = [
        pr for pr in prs
        if pr["repository"]["owner"]["login"].casefold()
        == pdata.username.casefold()
    ]

    pdata.opened_count_owned = len(prs_owned)
    pdata.merged_count_owned = sum(pr["mergedAt"] is not None for pr in prs_owned)
    pdata.closed_count_owned = sum(
        pr["state"] == "CLOSED" and pr["mergedAt"] is None for pr in prs_owned
    )

    # PRs against external repos.
    prs_external = [
        pr for pr in prs
        if pr["repository"]["owner"]["login"].casefold()
        != pdata.username.casefold()
    ]
    pdata.opened_count_external = len(prs_external)
    pdata.merged_count_external = sum(pr["mergedAt"] is not None for pr in prs_external)
    pdata.closed_count_external = sum(
        pr["state"] == "CLOSED" and pr["mergedAt"] is None for pr in prs_external
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
                        repository {{
                            nameWithOwner
                            owner {{
                                login
                            }}
                        }}
                    }}
                }}
            }}
        }}
    """

    return dedent(pr_query).strip()
