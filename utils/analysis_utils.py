"""Utils for analyzing account information."""

from . import flags

def process_account_age(account_age):
    """Evaluate account age."""
    if account_age.days > 3*365:
        return flags.green_flag
    elif account_age.days > 90:
        return flags.yellow_flag
    else: 
        return flags.red_flag

def process_pr_activity(pr_counts):
    """Evaluate recent PR activity."""
    opened_count, merged_count, closed_count = pr_counts
    ratio_merged = merged_count / opened_count
    ratio_closed = closed_count / opened_count

    if ratio_closed > 0.5:
        flag_closed_pr = flags.red_flag
    elif ratio_closed > 0.15:
        flag_closed_pr = flags.yellow_flag
    else:
        flag_closed_pr = flags.green_flag

    flag_merged_pr = None
    if ratio_merged > 0.5:
        flag_merged_pr = flags.green_flag

    return flag_closed_pr, flag_merged_pr
