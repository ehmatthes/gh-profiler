"""Tests for whether the correct flags are assigned, based on what's found."""

from gh_profiler.utils import analysis_utils
from gh_profiler.utils import summary_utils
from gh_profiler.utils.profile_data import profile_data as pdata
from gh_profiler.utils import flags
from reference_files import reference_summaries



def test_low_pr_volume_one_external_pr_closed():
    """Test that an external PR being closed doesn't result in a yellow or red
    flag when there's low overall PR volume.
    """
    # Set relevant user data.
    pdata.opened_count = 3
    pdata.opened_count_owned = 0
    pdata.opened_count_external = 3

    pdata.merged_count_external = 2
    pdata.closed_count_external = 1

    # Just run the PR activity analysis.
    analysis_utils._process_pr_activity()

    summary = summary_utils._get_summary()

    assert flags.yellow_flag not in summary
    assert flags.red_flag not in summary
