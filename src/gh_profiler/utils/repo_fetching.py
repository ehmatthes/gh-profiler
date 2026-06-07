"""Utils for retrieving repo information when targeting a URL."""

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
        reachable_future = executor.submit(_fetch_reachable)

        # When each call finishes, store the result.
        reachable_str = reachable_future.result()

    ts_after = perf_counter()
    if pdata.benchmark_fetch:
        print(f"Fetch data: {ts_after - ts_before:.2f} seconds")

    # Parse data. This should only happen after all data has been fetched.
    _parse_reachable(reachable_str)


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
