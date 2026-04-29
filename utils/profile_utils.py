"""Utils for retrieving user information."""

import json
from datetime import datetime as dt
from datetime import timezone as tz
from datetime import timedelta
from urllib.parse import quote

from profile_data import profile_data
from . import infra_utils


def get_account_age(gh_user):
    cmd = f"gh api users/{gh_user} --jq '{{login, name, created_at}}'"
    account_info = infra_utils.run_cmd(cmd)
    account_info = json.loads(account_info)
    ts_created = dt.fromisoformat(account_info["created_at"])
    profile_data.account_age = dt.now(tz.utc) - ts_created

def get_pr_activity(gh_user):
    """Get information about recent PR activity."""
    cutoff = (dt.now(tz.utc) - timedelta(days=21)).date().isoformat()
    base_query = f"author:{gh_user} is:pr created:>={cutoff}"

    opened_cmd = (
        f'gh api "search/issues?q={quote(base_query)}" --jq .total_count'
    )
    merged_cmd = (
        f'gh api "search/issues?q={quote(base_query + " is:merged")}" --jq .total_count'
    )
    closed_cmd = (
        f'gh api "search/issues?q={quote(base_query + " is:closed -is:merged")}" --jq .total_count'
    )

    opened_count = int(infra_utils.run_cmd(opened_cmd).strip())
    merged_count = int(infra_utils.run_cmd(merged_cmd).strip())
    closed_count = int(infra_utils.run_cmd(closed_cmd).strip())

    return (opened_count, merged_count, closed_count)
