"""Utils for retrieving repo information when targeting a URL."""

import json
import sys
from concurrent.futures import ThreadPoolExecutor
from textwrap import dedent
from time import perf_counter

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
            author=pr_dict["author"]["login"],
            title=pr_dict["title"],
            url=pr_dict["url"],
        )
        target_prs.append(pr_data)

    return target_prs


def _get_pr_query():
    """Return the gh call for recent open PRs in a repo."""
    gh_call = f"""
        gh api graphql -f query='
        query($owner: String!, $repo: String!, $n: Int!) {{
        repository(owner: $owner, name: $repo) {{
            pullRequests(
            first: $n,
            states: OPEN,
            orderBy: {{field: CREATED_AT, direction: DESC}}
            ) {{
            nodes {{
                number
                title
                url
                author {{
                login
                }}
            }}
            }}
        }}
        }}' -F owner='{repo_data.owner}' -F repo='{repo_data.repo_name}' -F n={cli_config.num_targets}
    """

    return dedent(gh_call).strip()