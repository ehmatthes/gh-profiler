"""Utils for analyzing account information."""

from profile_data import profile_data
from . import flags


def process_account_age():
    """Evaluate account age."""
    if profile_data.account_age.days > 3 * 365:
        profile_data.flag_age = flags.green_flag
    elif profile_data.account_age.days > 90:
        profile_data.flag_age = yellow_flag
    else:
        profile_data.flag_age = flags.red_flag


def process_pr_activity():
    """Evaluate recent PR activity."""
    ratio_merged = profile_data.merged_count / profile_data.opened_count
    ratio_closed = profile_data.closed_count / profile_data.opened_count

    if ratio_closed > 0.5:
        profile_data.flag_closed_pr = flags.red_flag
    elif ratio_closed > 0.15:
        profile_data.flag_closed_pr = flags.yellow_flag
    else:
        profile_data.flag_closed_pr = flags.green_flag

    profile_data.flag_merged_pr = None
    if ratio_merged > 0.5:
        profile_data.flag_merged_pr = flags.green_flag
