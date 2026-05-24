"""Tests for making final adjustments to flags."""

from gh_profiler.utils.profile_data import profile_data as pdata
from gh_profiler.utils.analysis_utils import _adjust_account_age_flag
from gh_profiler.utils import flags



def test_account_age_all_green():
    """Flags stay green when all are green."""
    _adjust_account_age_flag()

    assert pdata.flag_age == flags.green_flag
    assert pdata.flag_overall_profile == flags.green_flag

def test_account_age_yellow():
    """Yellow age flag turns green when all others green."""
    pdata.flag_age = flags.yellow_flag
    pdata.flag_overall_profile = flags.yellow_flag

    _adjust_account_age_flag()

    assert pdata.flag_age == flags.green_flag
    assert pdata.flag_overall_profile == flags.green_flag

def test_account_age_red():
    """Red age flag turns green when all others green."""
    pdata.flag_age = flags.red_flag
    pdata.flag_overall_profile = flags.red_flag

    _adjust_account_age_flag()

    assert pdata.flag_age == flags.green_flag
    assert pdata.flag_overall_profile == flags.green_flag

def test_issues_flag_yellow():
    """Yellow age flag stays yellow when issues flag not green."""
    pdata.flag_age = flags.yellow_flag
    pdata.flag_overall_profile = flags.yellow_flag
    pdata.flag_overall_issues = flags.yellow_flag

    _adjust_account_age_flag()

    assert pdata.flag_age == flags.yellow_flag
    assert pdata.flag_overall_profile == flags.yellow_flag
    