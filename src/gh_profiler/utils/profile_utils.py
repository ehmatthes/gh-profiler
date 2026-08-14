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
    if pdata.username == "ghost":
        # This is GitHub's deleted user, and we don't need to do anything.
        return
        
    # Fetch data. This can all be done in parallel. The benchmarking is here
    # because this is the slowest part of the program, and it's helpful at
    # times to benchmark just this fetching code.
    ts_before = perf_counter()
    with ThreadPoolExecutor() as executor:
        # Make fetching calls.
        fetch_calls = {
            "status": executor.submit(_fetch_status),
            "profile": executor.submit(_fetch_profile_dict),
            "orgs": executor.submit(_fetch_orgs),
            "socials": executor.submit(_fetch_socials),
            "recent PR activity": executor.submit(_fetch_pr_activity),
            "recent issue activity": executor.submit(_fetch_issue_activity),
        }

        # Auth is the one failure we want to explain ourselves, so resolve and
        # check that call first.
        status_obj = fetch_calls["status"].result()

        # If a fetch fails, the gh call itself went wrong and the message says
        # what happened. One bad call shouldn't take down the whole run with an
        # opaque traceback, so guard each call as we collect results.
        fetch_results = {}
        for name, future in fetch_calls.items():
            if name == "status":
                continue
            try:
                fetch_results[name] = future.result()
            except ValueError as e:
                sys.exit(e)

    ts_after = perf_counter()
    if pdata.benchmark_fetch:
        print(f"Fetch data: {ts_after - ts_before:.2f} seconds")

    # Parse data. This should only happen after all data has been fetched.
    _parse_status(status_obj)
    _parse_profile_dict(fetch_results["profile"])
    _parse_orgs(fetch_results["orgs"])
    _parse_socials(fetch_results["socials"])
    _parse_pr_activity(fetch_results["recent PR activity"])
    _parse_issue_activity(fetch_results["recent issue activity"])


# --- Helper functions ---

def _run_gh_cmd(cmd, context):
    """Run a gh command and make sure it actually worked.

    We used to parse whatever came back and blame timeouts whenever parsing
    failed, which hid the real problem (bad token, 404, rate limit, and so on).
    Checking the return code and reading stderr gives the user a much better
    message. This raises ValueError, which callers can catch or let ride.
    """
    result = infra_utils.run_cmd(cmd)
    if result.returncode != 0:
        msg = f"Couldn't fetch {context} from GitHub."
        if result.stderr:
            msg += f"\n  gh said: {result.stderr.strip()}"
        else:
            msg += "\n  The gh CLI may have timed out."
        msg += "\n  You may want to try running the command again."
        raise ValueError(msg)
    return result

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

    # A nonexistent user comes back as a 404, so give that a clear message
    # instead of a generic failure.
    if result.returncode != 0:
        if "404" in result.stderr:
            sys.exit(f"GitHub user '{pdata.username}' not found.")
        msg = f"Couldn't fetch profile info from GitHub."
        if result.stderr:
            msg += f"\n  gh said: {result.stderr.strip()}"
        else:
            msg += "\n  The gh CLI may have timed out."
        msg += "\n  You may want to try running the command again."
        raise ValueError(msg)

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
    result = _run_gh_cmd(cmd, "org info")

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

def _classify_repos(nodes, username, orgs):
    """Split nodes into owned, org, and external repos.

    GitHub logins are case-insensitive, so we compare casefolded values
    everywhere. The original PR and issue parsers each did this by hand, and
    they drifted apart (issues were case-sensitive, PRs were not). One helper
    keeps them in sync.
    """
    username_casefold = username.casefold()
    orgs_casefold = {org.casefold() for org in orgs}

    owned = [
        node for node in nodes
        if node["repository"]["owner"]["login"].casefold() == username_casefold
    ]

    in_orgs = [
        node for node in nodes
        if node not in owned
        and node["repository"]["owner"]["login"].casefold() in orgs_casefold
    ]

    external = [
        node for node in nodes
        if node not in owned
        and node not in in_orgs
    ]

    return owned, in_orgs, external

def _fetch_socials():
    """Fetch social media accounts from user's profile.
    
    Social media accounts from profiles are a separate endpoint, so I believe
    they require an additional API call.
    """
    cmd = f"gh api users/{pdata.username}/social_accounts"
    result = _run_gh_cmd(cmd, "social account info")

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
    result = _run_gh_cmd(cmd, "recent PR activity")

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

    prs_owned, prs_orgs, prs_external = _classify_repos(prs, pdata.username, pdata.orgs)

    pdata.opened_count_owned = len(prs_owned)
    pdata.opened_count_orgs = len(prs_orgs)
    pdata.opened_count_external = len(prs_external)
    pdata.merged_count_external = sum(pr["mergedAt"] is not None for pr in prs_external)
    pdata.closed_count_external = sum(
        pr["state"] == "CLOSED" and pr["mergedAt"] is None for pr in prs_external
    )

def _fetch_issue_activity():
    """Fetch target user's recent public issue activity."""
    cutoff = (dt.now(tz.utc) - timedelta(days=21)).date().isoformat()
    gh_call = _get_gh_issues_call(pdata.username, cutoff)
    result = _run_gh_cmd(gh_call, "recent issue activity")

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
    issues_owned, issues_orgs, issues_external = _classify_repos(
        issue_dicts, pdata.username, pdata.orgs
    )

    # The search API caps results at 100 nodes, but issueCount can report a
    # higher number. Report what we actually analyzed, so the count always
    # matches the rest of the issue analysis.
    pdata.new_issue_count = len(issue_dicts)

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
