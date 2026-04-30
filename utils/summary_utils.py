"""Utils for summarizing findings."""

from profile_data import profile_data as pdata
from . import flags


def show_summary():
    """Show a concise summary of what was found."""
    # Username, account age:
    print(f"\nGitHub user: {pdata.username}")
    print(f"  {pdata.flag_age} Account age: {pdata.account_age.days} days")

    # Available profile information:
    print(f"\n  {pdata.flag_profile} Profile information:")
    for k, v in pdata.profile_dict.items():
        print(f"      {k}: {v}")

    # Recent PR activity:
    print()
    if pdata.opened_count >= 10:
        # Only show merged if it's a good sign.
        if pdata.flag_merged_pr == flags.green_flag:
            print(
                f"  {pdata.flag_merged_pr} {pdata.merged_count} of {pdata.opened_count} PRs have been merged in the last 21 days."
            )
        print(
            f"  {pdata.flag_closed_pr} {pdata.closed_count} of {pdata.opened_count} PRs have been closed without merging in the last 21 days."
        )
    else:
        print(
            f"  {flags.green_flag} {pdata.username} has opened fewer than 10 PRs in the last 21 days."
        )
    print("")
