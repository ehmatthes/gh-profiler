"""Utils for retrieving user information."""

import json
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime as dt
from datetime import timedelta
from datetime import timezone as tz
from textwrap import dedent
from time import perf_counter
from collections import Counter

from . import infra_utils
from .profile_data import profile_data as pdata


def ensure_gh():
    """Make sure user has gh installed.

    Check for authentication issues in batch of external calls, rather than making
    a call just for that purpose here.
    """
    cmd = "gh --version"
    try:
        result = infra_utils.run_cmd(cmd)
        version_info = result.stdout
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
        orgs_future = executor.submit(_fetch_orgs)
        socials_future = executor.submit(_fetch_socials)
        pr_activity_future = executor.submit(_fetch_pr_activity)
        issue_activity_future = executor.submit(_fetch_issue_activity)

        # When each call finishes, store the result.
        status_obj = status_future.result()
        profile_dict_str = profile_dict_future.result()
        orgs_str = orgs_future.result()
        socials_str = socials_future.result()
        pr_activity_str = pr_activity_future.result()
        issue_activity_str = issue_activity_future.result()

    ts_after = perf_counter()
    if pdata.benchmark_fetch:
        print(f"Fetch data: {ts_after - ts_before:.2f} seconds")

    # Parse data. This should only happen after all data has been fetched.
    _parse_status(status_obj)
    _parse_profile_dict(profile_dict_str)
    _parse_orgs(orgs_str)
    _parse_socials(socials_str)
    _parse_pr_activity(pr_activity_str)
    _parse_issue_activity(issue_activity_str)


# --- Helper functions ---

def _fetch_status():
    """Fetch output of `gh auth status`.
    
    Unlike most other calls, this returns the CommandResult instance, because
    we'll need to inspect stdout and stderr.
    """
    cmd = "gh auth status"
    return infra_utils.run_cmd(cmd)

def _parse_status(status_obj):
    """Parse output of status call.
    
    Unlike most other parsing functions, this acts no an instance of
    CommandResult, because we need to look at stdout and stderr.
    """
    msg_authenticated = "Logged in to github.com "
    authenticated = (
        msg_authenticated in status_obj.stdout
        or msg_authenticated in status_obj.stderr
    )
    if not authenticated:
        # Show the output of `gh auth status`, if there is any.
        # I believe this is relevant when the user has an expired token.
        msg = ""
        if status_obj.stdout:
            msg += f"\n{status_obj.stdout}\n"
        if status_obj.stderr:
            msg += f"\n{status_obj.stderr}\n"

        msg += "\nThe GitHub CLI tool (gh) is not authenticated."
        msg += "\nRun `gh auth login` to authenticate."
        sys.exit(msg)

def _fetch_profile_dict():
    """Fetch the profile information we'll need."""
    cmd = f"gh api users/{pdata.username} --jq '{{login, name, created_at, company, blog, location, email, bio}}'"
    result = infra_utils.run_cmd(cmd)

    return result.stdout

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

def _fetch_orgs():
    """Fetch the user's publicly visible orgs.
    
    This will be used to distinguish between PRs and issues opened against
    external repos, and repos the user is associated with.
    """
    cmd = (
        f"gh api users/{pdata.username}/orgs "
        "--jq '[.[] | {login, description, url}]'"
    )
    result = infra_utils.run_cmd(cmd)

    return result.stdout

def _parse_orgs(orgs_str):
    """Parse the org info that was found."""
    try:
        orgs = json.loads(orgs_str)
    except json.decoder.JSONDecodeError:
        msg = "Couldn't get org info. The gh CLI may have timed out."
        msg += "\n  You may want to try running the command again."
        sys.exit(msg)

    pdata.orgs = [org["login"] for org in orgs]

def _fetch_socials():
    """Fetch social media accounts from user's profile.
    
    Social media accounts from profiles are a separate endpoint, so I believe
    they require an additional API call.
    """
    cmd = f"gh api users/{pdata.username}/social_accounts"
    result = infra_utils.run_cmd(cmd)

    return result.stdout

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
    result = infra_utils.run_cmd(cmd)

    return result.stdout

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

    # PRS against repos in orgs the user is publicly associated with.
    prs_orgs = [
        pr for pr in prs
        if pr["repository"]["owner"]["login"] in pdata.orgs
    ]

    pdata.opened_count_orgs = len(prs_orgs)

    # PRs against external repos.
    prs_external = [
        pr for pr in prs
        if pr not in prs_owned
        and pr not in prs_orgs
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
    result = infra_utils.run_cmd(gh_call)

    return result.stdout

def _parse_issue_activity(issue_activity_str):
    """Parse data returned by _fetch_issue_activity()."""
    try:
        issue_activity = json.loads(issue_activity_str)["data"]["search"]
    except (json.decoder.JSONDecodeError, KeyError):
        msg = "Couldn't get recent issue activity. The gh CLI may have timed out."
        msg += "\n  You may want to try running the command again."
        sys.exit(msg)

    issue_dicts = issue_activity["nodes"]
    issues_owned = [
        id for id in issue_dicts
        if id["repository"]["owner"]["login"] == pdata.username
    ]
    issues_orgs = [
         id for id in issue_dicts
         if id["repository"]["owner"]["login"] in pdata.orgs
    ]
    issues_external = [
         id for id in issue_dicts
         if id not in issues_owned
         and id not in issues_orgs
    ]

    # DEV: Should we be dealing with pagination?
    # When does issueCount != len(issue_dicts)?
    pdata.new_issue_count = issue_activity["issueCount"]

    pdata.issues_owned = len(issues_owned)
    pdata.issues_orgs = len(issues_orgs)
    pdata.issues_external = len(issues_external)
    pdata.issues_not_planned = len(
        [d for d in issues_external if d["stateReason"] == "NOT_PLANNED"]
    )

    _process_repeated_issues(issues_external)

def _process_repeated_issues(issues_external):
    """Look for issues with the same title across multiple repositories."""
    issue_titles = [d["title"].strip() for d in issues_external]

    counter = Counter(issue_titles)
    # Only keep titles for repeated issues.
    pdata.repeated_issue_titles = {
        title: count for title, count in counter.items() if count > 1
    }
    pdata.total_repeats = sum(pdata.repeated_issue_titles.values())


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
                isInOrganization
                owner {{
                    __typename
                    login
                }}
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
                            isInOrganization
                            owner {{
                                __typename
                                login
                            }}
                        }}
                    }}
                }}
            }}
        }}
    """

    return dedent(pr_query).strip()
