"""Tests for the summary that's generated."""

from datetime import timedelta

from gh_profiler.utils import summary_utils
from gh_profiler.utils.profile_data import profile_data as pdata
from gh_profiler.utils import flags
from reference_files import reference_summaries



def test_summary():
    """Test the overall summary output.
    
    DEV: Consider processing the profile data, instead of setting it?
         Maybe that's an integration test?
         Maybe unit test the processing function?
    """
    pdata.username = "ehmatthes"
    pdata.profile_info = {
        "name": "Eric Matthes",
        "company": None,
        "blog": "https://www.mostlypython.com",
        "location": "western North Carolina",
        "email": "ehmatthes@gmail.com",
        "bio": None,
    }
    pdata.opened_count = 5
    pdata.closed_count = 1
    pdata.merged_count = 3
    pdata.account_age = timedelta(days=5058)
    pdata.flag_age = flags.green_flag
    pdata.flag_profile = flags.green_flag

    # This is taken from analysis_utils.py:
    fields = ["name", "company", "blog", "location", "email", "bio"]
    pdata.profile_dict = {field:pdata.profile_info[field] for field in fields}

    summary = summary_utils._get_summary()
    assert summary.strip() == reference_summaries.full_summary
