"""Utils for analyzing account information."""

from datetime import datetime as dt
from datetime import timezone as tz

from .profile_data import profile_data as pdata
from . import flags


def process_account_age():
    """Evaluate account age."""
    ts_created = dt.fromisoformat(pdata.profile_info["created_at"])
    pdata.account_age = dt.now(tz.utc) - ts_created

    if pdata.account_age.days > 3 * 365:
        pdata.flag_age = flags.green_flag
    elif pdata.account_age.days > 90:
        pdata.flag_age = flags.yellow_flag
    else:
        pdata.flag_age = flags.red_flag

def process_profile_info():
    """Evaluate available profile information.

    Focus on: name, company, blog, lcoation, email, bio
    """
    fields = ["name", "company", "blog", "location", "email", "bio"]
    pdata.profile_dict = {field:pdata.profile_info[field] for field in fields}

    num_filled = sum(v not in (None, "") for v in pdata.profile_dict.values())
    if num_filled == 0:
        pdata.flag_profile = flags.red_flag
    elif num_filled < 3:
        pdata.flag_profile = flags.yellow_flag
    else:
        pdata.flag_profile = flags.green_flag


def process_pr_activity():
    """Evaluate recent PR activity."""
    # Don't need to analyze PR activity if fewer than 10 PRs opened recently.
    if pdata.opened_count < 10:
        return

    ratio_merged = pdata.merged_count / pdata.opened_count
    ratio_closed = pdata.closed_count / pdata.opened_count

    if ratio_closed > 0.5:
        pdata.flag_closed_pr = flags.red_flag
    elif ratio_closed > 0.15:
        pdata.flag_closed_pr = flags.yellow_flag
    else:
        pdata.flag_closed_pr = flags.green_flag

    pdata.flag_merged_pr = None
    if ratio_merged > 0.5:
        pdata.flag_merged_pr = flags.green_flag

def process_issue_activity():
    """Evaluate recent public issue activity."""
    # How many new issues have been opened recently?
    pdata.new_issue_count = pdata.issue_activity["issueCount"]

    # How many have been closed with a problematic state?
    _process_issue_state()

    # Determine a flag for the overall issue section.
    _process_issue_flags()


# --- Helper functions ---

def _process_issue_state():
    """Examine state of closed issues.

    Mostly looking for statuses like "NOT_PLANNED".
    The GraphQL endpoint 
    """
    issue_dicts = pdata.issue_activity["nodes"]

    # How many issues were closed as NOT_PLANNED?
    pdata.issues_not_planned = len(
        [d for d in issue_dicts if d["stateReason"] == "NOT_PLANNED"])

    # Green flag
    if pdata.issues_not_planned <= 3:
        flag = flags.green_flag
    elif pdata.issues_not_planned <= 5:
        flag = flags.yellow_flag
    else:
        flag = flags.red_flag
    pdata.flag_issues_not_planned = flag

def _process_issue_flags():
    """Determine a flag for the overall issue section."""
    # Assume flag is green.
    flag = flags.green_flag
    
    # If any are yellow, bump overall to yellow.
    if flags.yellow_flag in (pdata.flag_issues_not_planned, ):
        flag = flags.yellow_flag
    # If any are red, bump overall to red.
    if flags.red_flag in (pdata.flag_issues_not_planned, ):
        flag = flags.red_flag
    
    pdata.flag_overall_issues = flag
