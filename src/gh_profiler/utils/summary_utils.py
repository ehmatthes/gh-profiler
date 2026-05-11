"""Utils for summarizing findings."""

from .profile_data import profile_data as pdata
from . import flags


def show_summary():
    """Show a concise summary of what was found."""
    summary = _get_summary()
    print(summary)


def _get_summary():
    """Build a summary string.

    This is more testable and flexible than just printing each bit of information.
    """
    if pdata.redact:
        _redact_info()

    summary = ""

    # If target is a PR or issue, add title.
    summary += _pr_title_line()
    summary += _issue_title_line()

    # Include username, with label when appropriate.
    summary += _username_line()

    # Always include account age.
    summary += f"  {pdata.flag_age} Account age: {pdata.account_age.days} days\n"

    # Include profiler, PR activity, and issue activity sections.
    summary += _profile_summary()
    summary += "\n"
    summary += _pr_activity_summary()
    summary += "\n"
    summary += _issue_activity_summary()

    return summary.strip()


# --- Helper functions ---


def _redact_info():
    """Redact identifying information when --redact passed.

    This is primarily used for live demos, and screenshots.

    Redact here, when all analysis has been done, and we're only presenting
    information.
    """
    pdata.username = "<redacted>"
    for k, v in pdata.profile_info.items():
        if v:
            pdata.profile_info[k] = "<redacted>"


def _pr_title_line():
    """If target is a PR, include title."""
    if not pdata.is_pr:
        return ""

    return f"PR #{pdata.pr_number}: {pdata.pr_title}\n"


def _issue_title_line():
    """If target is an issue, include title."""
    if not pdata.is_issue:
        return ""

    return f"Issue #{pdata.issue_number}: {pdata.issue_title}\n"


def _username_line():
    """Include username, with appropriate label."""
    if pdata.is_pr or pdata.is_issue:
        return f"Author: {pdata.username}\n"

    return f"GitHub user: {pdata.username}\n"


def _profile_summary():
    """Summarize information from the user's profile dict."""
    if pdata.flag_profile == flags.red_flag:
        return f"\n  {pdata.flag_profile} No profile information has been provided.\n"

    # Only show lines for fields that have information.
    # Collect empty fields for last line.
    summary = f"\n  {pdata.flag_profile} Profile information:\n"
    empty_fields = []
    for k, v in pdata.profile_info.items():
        if v and k != "bio":
            summary += f"      {k}: {v}\n"
        elif v and k == "bio":
            summary += _bio_summary(v)
        else:
            empty_fields.append(k)

    # List empty fields.
    if empty_fields:
        fields_str = ", ".join(empty_fields)
        summary += f"     Empty fields: {fields_str}\n"

    return summary


def _bio_summary(bio):
    """Summarize bio section of profile."""
    if bio in (None, ""):
        return f"      bio:\n"

    if bio.count("\n") == 0:
        return f"      bio: {bio}\n"

    # Print a multi-line bio.
    summary = "      bio:\n"
    for line in bio.splitlines():
        summary += f"        {line}\n"
    return summary


def _pr_activity_summary():
    """Summarize recent PR activity."""
    if pdata.opened_count < 10:
        return f"  {flags.green_flag} {pdata.username} has opened fewer than 10 PRs in the last 21 days.\n"

    summary = ""
    # Only show merged if it's a good sign.
    if pdata.flag_merged_pr == flags.green_flag:
        summary += f"  {pdata.flag_merged_pr} {pdata.merged_count} of {pdata.opened_count} PRs have been merged in the last 21 days.\n"

    # Include number closed for everyone.
    summary += f"  {pdata.flag_closed_pr} {pdata.closed_count} of {pdata.opened_count} PRs have been closed without merging in the last 21 days.\n"

    return summary


def _issue_activity_summary():
    """Summarize recent public issue activity."""
    if pdata.new_issue_count == 0:
        return f"  {flags.green_flag} {pdata.username} has not opened any new issues in the last 21 days.\n"

    summary = f"  {pdata.flag_overall_issues} {pdata.username} has opened {pdata.new_issue_count} new issues in the last 21 days.\n"
    summary += f"     {pdata.flag_issues_not_planned} {pdata.issues_not_planned} issues have been closed as NOT_PLANNED.\n"

    # Repeated issues:
    if pdata.total_repeats == 0:
        summary += f"     {pdata.flag_repeated_issues} {pdata.total_repeats} issues were opened with the same title.\n"
    else:
        summary += f"     {pdata.flag_repeated_issues} {pdata.total_repeats} issues were opened with the same title:\n"
    for title, count in pdata.repeated_issue_titles.items():
        summary += f"        {title} ({count})\n"

    return summary
