"""conftest for unit tests."""

from datetime import timedelta

import pytest

from gh_profiler.utils.profile_data import profile_data as pdata
from gh_profiler.utils import flags


@pytest.fixture(autouse=True)
def filled_pdata():
    """Fill in a basic pdata profile.

    This fixture doesn't need to be passed, because it modifies the singleton
    pdata object.

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
    pdata.account_age = timedelta(days=5058)

    pdata.opened_count = 5
    pdata.closed_count = 1
    pdata.merged_count = 3

    pdata.flag_age = flags.green_flag
    pdata.flag_profile = flags.green_flag

    # This is taken from analysis_utils.py:
    fields = ["name", "company", "blog", "location", "email", "bio"]
    pdata.profile_dict = {field: pdata.profile_info[field] for field in fields}

    # Issue fields
    pdata.new_issue_count = 7
    pdata.total_repeats = 0
    pdata.repeated_issue_titles = {}

    pdata.flag_issues_not_planned = flags.green_flag
    pdata.flag_repeated_issues = flags.green_flag

    # Call function to process this?
    pdata.flag_overall_issues = flags.green_flag


@pytest.fixture()
def empty_profile_info():
    """Empty the profile dict.

    Tests that need this will need to include this fixture explicitly.
    This can simplify some more specific profile tests.
    """
    pdata.profile_info = {}
    pdata.flag_profile = flags.red_flag
