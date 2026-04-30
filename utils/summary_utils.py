"""Utils for summarizing findings."""

from profile_data import profile_data as pdata
from . import flags


def show_summary():
    """Show a concise summary of what was found."""
    # Username, account age:
    print(f"\nGitHub user: {pdata.username}")
    print(f"  {pdata.flag_age} Account age: {pdata.account_age.days} days")

    # Available profile information:
    if pdata.flag_profile == flags.red_flag:
        print(f"\n  {pdata.flag_profile} No profile information has been provided.")
    else:
        _show_profile_dict()
    
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


# --- Helper functions ---

def _show_profile_dict():
    """Summarize information from the user's profile dict."""
    print(f"\n  {pdata.flag_profile} Profile information:")

    for k, v in pdata.profile_dict.items():
        if v and k != "bio":
            print(f"      {k}: {v}")
        elif k == "bio":
            _show_bio(v)
        else:
            print(f"      {k}:")

def _show_bio(bio):
    """Show a bio appropriately."""
    if bio in (None, ""):
        print(f"      bio:")
        return
        
    if bio.count("\n") == 0:
        print(f"      bio: {bio}")
        return

    # Print a multi-line bio.
    print("      bio:")
    for line in bio.splitlines():
        print(f"        {line}")
