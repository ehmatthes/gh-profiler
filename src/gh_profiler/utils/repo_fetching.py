"""Utils for retrieving repo information when targeting a URL."""

import json
import sys
from concurrent.futures import ThreadPoolExecutor
from textwrap import dedent
from time import perf_counter
from datetime import datetime as dt, timezone

from . import infra_utils
from .profile_data import profile_data as pdata
from .repo_data import repo_data, PRData
from .cli_config import cli_config

import httpx2


def get_data():
    """Get all repo-level data we'll need from GitHub.
    
    Repo-level data includes things like which PR or issue numbers are we
    targeting.

    Fetch all data we'll need, then parse it into the data structures that
    can be analyzed and processed.
    """
    # Fetch data. This can all be done in parallel. The benchmarking is here
    # because this is the slowest part of the program, and it's helpful at
    # times to benchmark just this fetching code.
    ts_before = perf_counter()
    with ThreadPoolExecutor() as executor:
        # Make fetching calls.
        # reachable_future = executor.submit(_fetch_reachable)
        prs_future = executor.submit(_fetch_prs)

        # When each call finishes, store the result.
        # reachable_str = reachable_future.result()
        prs_obj = prs_future.result()

    ts_after = perf_counter()
    if pdata.benchmark_fetch:
        print(f"Fetch data: {ts_after - ts_before:.2f} seconds")

    # Parse data. This should only happen after all data has been fetched.
    # _parse_reachable(reachable_str)
    target_prs = _parse_prs(prs_obj)

    return target_prs


# --- Helper functions ---

def _fetch_reachable():
    """Fetch page at URL.
    
    Make sure this URL is reachable.
    """
    r = httpx2.get(cli_config.url)
    return r.status_code

def _parse_reachable(reachable_str):
    """Parse output of reachable call."""
    if reachable_str == 200:
        return

    msg = f"URL returned status code {reachable_str}."
    msg += "\n  Is the URL correct?"
    sys.exit(msg)

def _fetch_prs():
    """Fetch relevant PRs.
    
    Need: n most recently opened PRs.
    For each PR:
    - username, title, id
    """
    pr_query = _get_pr_query()
    result = infra_utils.run_cmd(pr_query)
    return result


def _parse_prs(prs_obj):
    """Parse required info from PR query."""
    prs_str = prs_obj.stdout
    prs_json = json.loads(prs_str)

    # Build a list of usernames to profile, along with relevant PR title
    # and number.
    target_prs = []
    for pr_dict in prs_json["data"]["repository"]["pullRequests"]["nodes"]:
        pr_data = PRData(
            pr_num=pr_dict["number"],
            author=_get_author(pr_dict),
            title=pr_dict["title"],
            url=pr_dict["url"],
        )
        if cli_config.back:
            _add_pr_back_fields(pr_dict, pr_data)
        target_prs.append(pr_data)

    # When looking back, we grabbed more PRs than we need. Sort them by 
    # closedAt, and return the number that were actually requested.
    if cli_config.back:
        target_prs.sort(key=lambda pr: pr.closed_at, reverse=True)
        target_prs = target_prs[:cli_config.num_targets]


    return target_prs

def _get_author(pr_dict):
    """Get the author of the PR.
    
    When a user deletes their account, GitHub shows the author as `ghost`.
    """
    if pr_dict["author"] is None:
        return "ghost"
    else:
        return pr_dict["author"]["login"]
    

def _add_pr_back_fields(pr_dict, pr_data):
    """Add fields to PRData object that only related to looking back."""
    pr_data.closed_at = _parse_gh_timestamp(pr_dict["closedAt"])

    if pr_dict["merged"]:
        pr_data.merged = True
    else:
        pr_data.merged = False


def _parse_gh_timestamp(ts):
    """Parse a gh API timestamp."""
    return dt.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(
        tzinfo=timezone.utc
    )

def _get_pr_query():
    """Return the gh call for recent PRs in a repo."""
    if cli_config.back:
        gh_state = "[CLOSED, MERGED]"
        order_field = "UPDATED_AT"
    else:
        gh_state = "OPEN"
        order_field = "CREATED_AT"

    if cli_config.back:
        # Get 5x as many PRs as requested. This query is sorted by updatedAt,
        # We want to show by closedAt. Make sure we don't request more than
        # 100 records.
        num_prs = 5 * cli_config.num_targets
        num_prs = min(num_prs, 100)
    else:
        # When looking at open PRs, no need to modify count.
        num_prs = cli_config.num_targets


    gh_call = f"""
        gh api graphql -f query='
        query($owner: String!, $repo: String!, $n: Int!) {{
        repository(owner: $owner, name: $repo) {{
            pullRequests(
            first: $n,
            states: {gh_state},
            orderBy: {{field: {order_field}, direction: DESC}}
            ) {{
            nodes {{
                number
                title
                state
                merged
                createdAt
                closedAt
                mergedAt
                url
                author {{
                login
                }}
            }}
            }}
        }}
        }}' -F owner='{repo_data.owner}' -F repo='{repo_data.repo_name}' -F n={num_prs}
    """

    return dedent(gh_call).strip()