"""Utils for analyzing account information."""

from datetime import datetime as dt
from datetime import timezone as tz

from profile_data import profile_data as pdata
from . import flags


def process_account_age():
    """Evaluate account age."""
    ts_created = dt.fromisoformat(pdata.profile_info["created_at"])
    pdata.account_age = dt.now(tz.utc) - ts_created

    if pdata.account_age.days > 3 * 365:
        pdata.flag_age = flags.green_flag
    elif pdata.account_age.days > 90:
        pdata.flag_age = yellow_flag
    else:
        pdata.flag_age = flags.red_flag

def process_profile_info():
    """Evaluate available profile information.

    Focus on: name, company, blog, lcoation, email, bio
    """
    fields = ["name", "company", "blog", "location", "email", "bio"]
    pdata.profile_dict = {field:pdata.profile_info[field] for field in fields}

    num_filled = sum(v not in (None, "") for v in pdata.profile_dict.values())
    if num_filled == 0:
        pdata.flag_profile = flags.red_flag
    elif num_filled < 3:
        pdata.flag_profile = flags.yellow_flag
    else:
        pdata.flag_profile = flags.green_flag


def process_pr_activity():
    """Evaluate recent PR activity."""
    ratio_merged = pdata.merged_count / pdata.opened_count
    ratio_closed = pdata.closed_count / pdata.opened_count

    if ratio_closed > 0.5:
        pdata.flag_closed_pr = flags.red_flag
    elif ratio_closed > 0.15:
        pdata.flag_closed_pr = flags.yellow_flag
    else:
        pdata.flag_closed_pr = flags.green_flag

    pdata.flag_merged_pr = None
    if ratio_merged > 0.5:
        pdata.flag_merged_pr = flags.green_flag
