"""Examine a user's profile, and highlight evidence they're human or AI.

The goal is to help make quick, evidence-based decisions about how much time
to invest in reviewing PRs, and general interaction on open source projects.
"""


from .utils import profile_utils
from .utils import analysis_utils
from .utils import summary_utils


def main():
    # Make sure gh is available.
    profile_utils.ensure_gh()

    # Get and analyze all data we'll need from GitHub.
    profile_utils.get_data()
    analysis_utils.process_data()

    # Summarize findings.
    summary_utils.show_summary()
