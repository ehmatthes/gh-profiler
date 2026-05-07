"""Tests for the summary that's generated."""

from gh_profiler.utils import summary_utils
from gh_profiler.utils.profile_data import profile_data as pdata
from reference_files import reference_summaries


def test_summary():
    """Test the overall summary output.

    DEV: Consider processing the profile data, instead of setting it?
         Maybe that's an integration test?
         Maybe unit test the processing function?
    """
    summary = summary_utils._get_summary()
    assert summary.strip() == reference_summaries.full_summary


def test_summary_empty_profile(empty_profile_info):
    """Test summary for user with an empty profile."""
    summary = summary_utils._get_summary()
    assert summary.strip() == reference_summaries.summary_empty_profile


def test_no_issue_activity():
    """Test output when there's no recent issue activity."""
    pdata.new_issue_count = 0
    summary = summary_utils._get_summary()

    assert "🟢 ehmatthes has not opened any new issues in the last 21 days." in summary
    assert "issues have been closed as NOT_PLANNED." not in summary
    assert "issues were opened with the same title:" not in summary


def test_redact():
    """Test output when pdata.redact is True."""
    pdata.redact = True
    summary = summary_utils._get_summary()

    assert "ehmatthes" not in summary
    assert summary.count("<redacted") == 7
