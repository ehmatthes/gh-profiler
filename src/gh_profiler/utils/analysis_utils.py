"""Utils for analyzing account information."""

from datetime import datetime as dt
from datetime import timezone as tz
from collections import Counter

from .profile_data import profile_data as pdata
from . import flags


def process_data():
    """Process all data."""
    _process_account_age()
    _process_profile_info()
    _process_pr_activity()
    _process_issue_activity()

    _set_overall_flags()


# --- Helper functions ---


def _process_account_age():
    """Evaluate account age."""
    ts_created = dt.fromisoformat(pdata.profile_dict["created_at"])
    pdata.account_age = dt.now(tz.utc) - ts_created

    if pdata.account_age.days > 3 * 365:
        pdata.flag_age = flags.green_flag
    elif pdata.account_age.days > 90:
        pdata.flag_age = flags.yellow_flag
    else:
        pdata.flag_age = flags.red_flag


def _process_profile_info():
    """Evaluate available profile information.

    Focus on: name, company, blog, lcoation, email, bio
    """
    fields = ["name", "company", "blog", "location", "email", "bio"]
    pdata.profile_info = {field: pdata.profile_dict[field] for field in fields}

    num_filled = sum(v not in (None, "") for v in pdata.profile_info.values())
    if num_filled == 0:
        pdata.flag_profile = flags.red_flag
    elif num_filled < 3:
        pdata.flag_profile = flags.yellow_flag
    else:
        pdata.flag_profile = flags.green_flag


def _process_pr_activity():
    """Evaluate recent PR activity."""
    # Don't need to analyze PR activity if fewer than 10 PRs opened recently.
    if pdata.opened_count < 10:
        pdata.flag_merged_pr = flags.green_flag
        pdata.flag_closed_pr = flags.green_flag
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


def _process_issue_activity():
    """Evaluate recent public issue activity."""
    # How many new issues have been opened recently?
    pdata.new_issue_count = pdata.issue_activity["issueCount"]

    # How many have been closed with a problematic state?
    _process_issue_state()
    _process_repeated_issues()

    # Determine a flag for the overall issue section.
    _process_issue_flags()


def _process_issue_state():
    """Examine state of closed issues.

    Mostly looking for statuses like "NOT_PLANNED".
    The GraphQL endpoint
    """
    issue_dicts = pdata.issue_activity["nodes"]

    # How many issues were closed as NOT_PLANNED?
    pdata.issues_not_planned = len(
        [d for d in issue_dicts if d["stateReason"] == "NOT_PLANNED"]
    )

    # Green flag
    if pdata.issues_not_planned <= 3:
        flag = flags.green_flag
    elif pdata.issues_not_planned <= 5:
        flag = flags.yellow_flag
    else:
        flag = flags.red_flag
    pdata.flag_issues_not_planned = flag


def _process_repeated_issues():
    """Look for spamming the same issue to multiple repositories."""
    issue_dicts = pdata.issue_activity["nodes"]
    issue_titles = [d["title"].strip() for d in issue_dicts]

    counter = Counter(issue_titles)
    # Only keep titles for repeated issues.
    pdata.repeated_issue_titles = {
        title: count for title, count in counter.items() if count > 1
    }
    pdata.total_repeats = sum(pdata.repeated_issue_titles.values())

    # There are some valid reasons for someone to open the same issue across
    # several repositories. For example if they open it on the wrong issue,
    # close it, then open it on the correct repo, that's two identical issues.
    # One person can also implement something on one repo, and implement that
    # same feature or improvement on several repos. There should be a threshold
    # where that's a clear sign of spamming though.
    if pdata.total_repeats <= 3:
        flag = flags.green_flag
    elif pdata.total_repeats <= 5:
        flag = flags.yellow_flag
    else:
        flag = flags.red_flag
    pdata.flag_repeated_issues = flag


def _set_overall_flags():
    """Set the overall flags, based on individual flags.
    
    These are used for header lines in the final summary, and for the concise
    summary as well.
    """
    _process_profile_flags()
    _process_pr_flags()
    _process_issue_flags()

def _process_profile_flags():
    """Determine a flag for the overall profile section."""
    profile_flags = (
        pdata.flag_age,
        pdata.flag_profile,
    )
    pdata.flag_overall_profile = _get_overall_flag(profile_flags)

def _process_pr_flags():
    """Determine a flag for the overall PR section."""
    # flag_merged is either None or green. It's never yellow or red.
    # People can have PRs open for a long time waiting for merges.
    pr_flags = (
        pdata.flag_closed_pr,
    )
    pdata.flag_overall_pr = _get_overall_flag(pr_flags)

def _process_issue_flags():
    """Determine a flag for the overall issue section."""
    issues_flags = (
        pdata.flag_issues_not_planned,
        pdata.flag_repeated_issues,
    )
    pdata.flag_overall_issues = _get_overall_flag(issues_flags)

def _get_overall_flag(component_flags):
    """Get an overall flag based on individual flags from a section.
    
    Overall flag is red if any component flag is red.
    Then, yellow if any component flag is yellow.
    If no red or yellow flags, return green.
    """
    if flags.red_flag in component_flags:
        return flags.red_flag
    if flags.yellow_flag in component_flags:
        return flags.yellow_flag
    return flags.green_flag
