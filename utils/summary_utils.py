"""Utils for summarizing findings."""

from profile_data import profile_data
from . import flags


def show_summary(
    gh_user,
    opened_count,
    merged_count,
    closed_count,
    flag_merged_pr,
    flag_closed_pr,
    ):
    """Show a concise summary of what was found."""
    print(f"\nGitHub user: {gh_user}")
    print(f"  {profile_data.flag_age} Account age: {profile_data.account_age.days} days")

    if opened_count >= 10:
        # Only show merged if it's a good sign.
        if flag_merged_pr == green_flag:
            print(f"  {flag_merged_pr} {merged_count} of {opened_count} PRs have been merged in the last 21 days.")
        print(f"  {flag_closed_pr} {closed_count} of {opened_count} PRs have been closed without merging in the last 21 days.")
    else:
        print(f"  {flags.green_flag} {gh_user} has opened fewer than 10 PRs in the last 21 days.")
    print("")