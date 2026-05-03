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

    # Available profile information:
    summary += _profile_summary()
    
    # Recent PR activity:
    summary += "\n"
    if pdata.opened_count >= 10:
        # Only show merged if it's a good sign.
        if pdata.flag_merged_pr == flags.green_flag:
            summary += f"  {pdata.flag_merged_pr} {pdata.merged_count} of {pdata.opened_count} PRs have been merged in the last 21 days.\n"
        summary += f"  {pdata.flag_closed_pr} {pdata.closed_count} of {pdata.opened_count} PRs have been closed without merging in the last 21 days.\n"
    else:
        summary += f"  {flags.green_flag} {pdata.username} has opened fewer than 10 PRs in the last 21 days.\n"
    summary += "\n"

    return summary


# --- Helper functions ---

def _profile_summary():
    """Summarize information from the user's profile dict."""
    if pdata.flag_profile == flags.red_flag:
        return f"\n  {pdata.flag_profile} No profile information has been provided.\n"

    summary = f"\n  {pdata.flag_profile} Profile information:\n"

    for k, v in pdata.profile_dict.items():
        if v and k != "bio":
            summary += f"      {k}: {v}\n"
        elif k == "bio":
            summary += _bio_summary(v)
        else:
            summary += f"      {k}:\n"

    return summary

def _bio_summary(bio):
    """Show a bio appropriately."""
    if bio in (None, ""):
        return f"      bio:\n"
        
    if bio.count("\n") == 0:
        return f"      bio: {bio}\n"

    # Print a multi-line bio.
    summary = "      bio:\n"
    for line in bio.splitlines():
        summary += f"        {line}\n"
    return summary