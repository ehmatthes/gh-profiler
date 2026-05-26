"""Tests for making final adjustments to flags."""

from gh_profiler.utils.profile_data import profile_data as pdata
from gh_profiler.utils import analysis_utils
from gh_profiler.utils import flags



def test_account_age_all_green():
    """Flags stay green when all are green."""
    analysis_utils._adjust_account_age_flag()

    assert pdata.flag_age == flags.green_flag
    assert pdata.flag_overall_profile == flags.green_flag

def test_account_age_yellow():
    """Yellow age flag turns green when all others green."""
    pdata.flag_age = flags.yellow_flag
    pdata.flag_overall_profile = flags.yellow_flag

    analysis_utils._adjust_account_age_flag()

    assert pdata.flag_age == flags.green_flag
    assert pdata.flag_overall_profile == flags.green_flag

def test_account_age_red():
    """Red age flag turns green when all others green."""
    pdata.flag_age = flags.red_flag
    pdata.flag_overall_profile = flags.red_flag

    analysis_utils._adjust_account_age_flag()

    assert pdata.flag_age == flags.green_flag
    assert pdata.flag_overall_profile == flags.green_flag

def test_issues_flag_yellow():
    """Yellow age flag stays yellow when issues flag not green."""
    pdata.flag_age = flags.yellow_flag
    pdata.flag_overall_profile = flags.yellow_flag
    pdata.flag_overall_issues = flags.yellow_flag

    analysis_utils._adjust_account_age_flag()

    assert pdata.flag_age == flags.yellow_flag
    assert pdata.flag_overall_profile == flags.yellow_flag

def test_no_pr_issue_activity():
    """If a user has not opened any recent PRs or issues, profile is green."""
    pdata.flag_profile = flags.yellow_flag
    pdata.flag_overall_profile = flags.yellow_flag
    pdata.opened_count = 0
    pdata.new_issue_count = 0

    analysis_utils._adjust_profile_flag_no_pr_issue_activity()

    assert pdata.flag_profile == flags.green_flag
    assert pdata.flag_overall_profile == flags.green_flag
    