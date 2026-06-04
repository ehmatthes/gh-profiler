"""Utils for analyzing account information."""

from datetime import datetime as dt, timezone
from datetime import timezone as tz

from .profile_data import profile_data as pdata
from . import flags


def process_data():
    """Process all data."""
    _process_account_age()
    _process_profile_info()
    _process_pr_activity()
    _process_issue_activity()

    _set_overall_flags()

    # This is a step done after all individual and group flags have been set.
    _adjust_flags()


# --- Helper functions ---


def _process_account_age():
    """Evaluate account age."""
    try:
        ts_created = dt.fromisoformat(pdata.profile_dict["created_at"])
    except ValueError:
        # This happens with Python <3.11. Let's support 3.10 for a while.
        ts_created = dt.strptime(
            pdata.profile_dict["created_at"],
            "%Y-%m-%dT%H:%M:%SZ",
        ).replace(tzinfo=timezone.utc)

    pdata.account_age = dt.now(tz.utc) - ts_created

    if pdata.account_age.days > 3 * 365:
        pdata.flag_age = flags.green_flag
    elif pdata.account_age.days > 90:
        pdata.flag_age = flags.yellow_flag
    else:
        pdata.flag_age = flags.red_flag


def _process_profile_info():
    """Evaluate available profile information.

    Focus on: name, company, blog, location, email, bio, socials
    """
    fields = ["name", "company", "blog", "location", "email", "bio"]
    pdata.profile_info = {field: pdata.profile_dict[field] for field in fields}

    num_filled = sum(v not in (None, "") for v in pdata.profile_info.values())

    # Include social media URLs, which are handled separately by GitHub.
    filled_socials = [d for d in pdata.socials if d["url"]]
    num_filled += len(filled_socials)

    if num_filled == 0:
        pdata.flag_profile = flags.red_flag
    elif num_filled < 3:
        pdata.flag_profile = flags.yellow_flag
    else:
        pdata.flag_profile = flags.green_flag


def _process_pr_activity():
    """Evaluate recent PR activity.
    
    Only evaluate PR activity against external repos, not PRs against repos
    the user owns.
    """
    # Don't need to analyze PR activity below a small threshold.
    min_external_pr_threshold = 4
    if pdata.opened_count_external < min_external_pr_threshold:
        pdata.flag_merged_pr = flags.green_flag
        pdata.flag_closed_pr = flags.green_flag

        if pdata.verbose:
            msg = f"PR flags set green because fewer than {min_external_pr_threshold} PRs opened against external repos."
            print(msg)

        return

    # All the following analysis focuses on PRs against external repos.
    if pdata.opened_count_external == 0:
        # DEV: Do these need to be set?
        pdata.flag_merged_pr = flags.green_flag
        pdata.flag_closed_pr = flags.green_flag
        return

    ratio_merged = pdata.merged_count_external / pdata.opened_count_external
    ratio_closed = pdata.closed_count_external / pdata.opened_count_external

    if ratio_closed > 0.5:
        # The lowest threshold would be 2 out of 4 PRs closed, which might be
        # too low but is reasonable to start with.
        pdata.flag_closed_pr = flags.red_flag
    elif ratio_closed > 0.2 and pdata.closed_count_external > 2:
        # Don't set this flag if the total closed count is 2 or fewer.
        pdata.flag_closed_pr = flags.yellow_flag
    else:
        pdata.flag_closed_pr = flags.green_flag

    pdata.flag_merged_pr = None
    if ratio_merged > 0.5:
        pdata.flag_merged_pr = flags.green_flag


def _process_issue_activity():
    """Evaluate recent public issue activity."""
    _process_issue_state()
    _process_repeated_issues()

    # Determine a flag for the overall issue section.
    _process_issue_flags()


def _process_issue_state():
    """Examine state of closed issues."""
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

def _adjust_flags():
    """Make final adjustments to flags.

    This takes place after all individual flags have been set, and all group
    flags have been set based on flags within the group.

    For example, if a newer account has no other red or yellow flags, we'll
    adjust the profile flags to green.

    Be careful about unintended effects. As evaluation criteria gets more
    complex, it would be easy to undo some reasoning implemented earlier.

    These function names can be longer than typical names, more like test
    function names.
    """
    _adjust_account_age_flag()
    _adjust_profile_flag_no_pr_issue_activity()

def _adjust_account_age_flag():
    """Reevaluate the account age flag.

    If PR and issue flags are green, the account age flag should be green.
    This applies when:
    - The account age flag is not green.
    - All other overall flags (PRs and issues) are green.
    """
    # Check for clear reasons this doesn't apply. Account age flag is already green,
    # or another overall flag is not green.
    if (
        pdata.flag_age == flags.green_flag
        or pdata.flag_overall_pr != flags.green_flag
        or pdata.flag_overall_issues != flags.green_flag
    ):
        return

    # Set the account age flag green, and reevaluate overall profile flag.
    pdata.flag_age = flags.green_flag
    _process_profile_flags()

    # Verbose rationale.
    msg = "\nFlag adjusted: Set account age flag green. This user has a newer account,"
    msg += "\n  but they have no other concerning activity."
    if pdata.verbose:
        print(msg)

def _adjust_profile_flag_no_pr_issue_activity():
    """If user has no recent PRs or issues, profile flags should be green.
    
    This is meant to handle the specific situation where the target user has
    had not recent PR or issue activity, and they have little or no profile
    information. For example, people who have scrubbed their GH accounts but
    not deleted their profile shouldn't raise any yellow or red flags.
    
    This should never come into play on a PR or issue. This should only come
    into play when someone decides to run a profile against the user's account
    for some other reason, such as curiosity. This was brought to my attention
    by someone running gh-profiler on their own account, and feeling
    uncomfortable about seeing flags raised despite no problematic activity.
    """
    # Doesn't apply if there are any new PRs or issues.
    if pdata.opened_count > 0 or pdata.new_issue_count > 0:
        return

    # Doesn't apply if relevant flags are already green.
    if (
        pdata.flag_profile == flags.green_flag
        and pdata.flag_overall_profile == flags.green_flag
    ):
        return

    pdata.flag_profile = flags.green_flag
    pdata.flag_overall_profile = flags.green_flag

    # Verbose rationale.
    msg = "\nFlags adjusted: Set profile info and overall profile flags green. This user has not"
    msg += "\n  opened any recent PRs or issues, so they have no concerning activity."
    if pdata.verbose:
        print(msg)
