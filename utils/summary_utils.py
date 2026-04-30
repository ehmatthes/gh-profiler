"""Utils for summarizing findings."""

from profile_data import profile_data
from . import flags


def show_summary(
    flag_merged_pr,
    flag_closed_pr,
    ):
    """Show a concise summary of what was found."""
    print(f"\nGitHub user: {profile_data.username}")
    print(f"  {profile_data.flag_age} Account age: {profile_data.account_age.days} days")

    if profile_data.opened_count >= 10:
        # Only show merged if it's a good sign.
        if flag_merged_pr == green_flag:
            print(f"  {flag_merged_pr} {profile_data.merged_count} of {profile_data.opened_count} PRs have been merged in the last 21 days.")
        print(f"  {flag_closed_pr} {profile_data.closed_count} of {profile_data.opened_count} PRs have been closed without merging in the last 21 days.")
    else:
        print(f"  {flags.green_flag} {profile_data.username} has opened fewer than 10 PRs in the last 21 days.")
    print("")