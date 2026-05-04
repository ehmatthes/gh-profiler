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
    summary = ""

    # Username, account age:
    summary += f"GitHub user: {pdata.username}\n"
    summary += f"  {pdata.flag_age} Account age: {pdata.account_age.days} days\n"

    summary += _profile_summary()
    summary += "\n"
    summary += _pr_activity_summary()
    summary += "\n"
    summary += _issue_activity_summary()
    summary += "\n"

    return summary.strip()


# --- Helper functions ---


def _profile_summary():
    """Summarize information from the user's profile dict."""
    if pdata.flag_profile == flags.red_flag:
        return f"\n  {pdata.flag_profile} No profile information has been provided.\n"

    # Only show lines for fields that have information.
    # Collect empty fields for last line.
    summary = f"\n  {pdata.flag_profile} Profile information:\n"
    empty_fields = []
    for k, v in pdata.profile_dict.items():
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
    ...
    if pdata.new_issue_count == 0:
        return f"\n    {pdata.usename} has not opened any new issues in the last 21 days.\n"

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
