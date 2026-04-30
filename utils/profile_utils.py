"""Utils for retrieving user information."""

import json
from datetime import datetime as dt
from datetime import timezone as tz
from datetime import timedelta
from urllib.parse import quote

from profile_data import profile_data as pdata
from . import infra_utils


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

    pdata.opened_count = int(infra_utils.run_cmd(opened_cmd).strip())
    pdata.merged_count = int(infra_utils.run_cmd(merged_cmd).strip())
    pdata.closed_count = int(infra_utils.run_cmd(closed_cmd).strip())
