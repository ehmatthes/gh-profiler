"""Utils for retrieving user information."""

import json
from datetime import datetime as dt
from datetime import timezone as tz
from datetime import timedelta
from urllib.parse import quote
import sys

from .profile_data import profile_data as pdata
from . import infra_utils

def ensure_gh():
    """Make sure user has gh installed.
    
    DEV: This may need different implementation on Windows or Linux.
    """
    cmd = "gh --version"
    try:
        version_info = infra_utils.run_cmd(cmd)
    except FileNotFoundError:
        msg = "The GitHub CLI tool (gh) must be installed."
        msg += "\n  https://cli.github.com"
        sys.exit(msg)

def get_profile_info():
    """Get all the profile info we'll need."""
    cmd = f"gh api users/{pdata.username} --jq '{{login, name, created_at, company, blog, location, email, bio}}'"
    profile_info = infra_utils.run_cmd(cmd)
    pdata.profile_info = json.loads(profile_info)


def get_pr_activity():
    """Get information about recent PR activity."""
    cutoff = (dt.now(tz.utc) - timedelta(days=21)).date().isoformat()
    base_query = f"author:{pdata.username} is:pr created:>={cutoff}"

    opened_cmd = f'gh api "search/issues?q={quote(base_query)}" --jq .total_count'
    merged_cmd = (
        f'gh api "search/issues?q={quote(base_query + " is:merged")}" --jq .total_count'
    )
    closed_cmd = f'gh api "search/issues?q={quote(base_query + " is:closed -is:merged")}" --jq .total_count'

    # DEV: These calls seem to be timing out occasionally.
    try:
        pdata.opened_count = int(infra_utils.run_cmd(opened_cmd).strip())
        pdata.merged_count = int(infra_utils.run_cmd(merged_cmd).strip())
        pdata.closed_count = int(infra_utils.run_cmd(closed_cmd).strip())
    except ValueError:
        msg = "Couldn't get recent PR activity. The gh CLI may have timed out."
        msg += "\n  You may want to try running the command again."
        sys.exit(msg)

