"""One place to store all data about the user."""

from dataclasses import dataclass


@dataclass(slots=True)
class ProfileData:
    """The main data store for everything we learn about the user.

    There's one instance of ProfileData, which is created here when it's first
    imported.

    Uses `slots=True` to make sure this is an accurate listing of all fields
    that can be filled in about the user.
    """

    username: str = ""

    # --- Target info ---
    is_pr: bool = False
    pr_number: int = 0
    pr_title: str = ""

    is_issue: bool = False
    issue_number: int = 0
    issue_title: str = ""

    # --- Profile info ---
    # profile_dict is the raw profile data we get from GitHub.
    # profile_info is the information we analyze and present.
    profile_dict: dict | None = None
    profile_info: dict | None = None
    account_age: int = 0

    flag_age: str = ""
    flag_profile: str = ""

    # --- PR fields ---
    opened_count: int = 0
    merged_count: int = 0
    closed_count: int = 0

    flag_merged_pr: str = ""
    flag_closed_pr: str = ""

    # --- Issue fields ---
    new_issue_count: int = 0
    issues_not_planned: int = 0
    total_repeats: int = 0
    repeated_issue_titles: dict | None = None
    issue_activity: dict | None = None

    flag_issues_not_planned: str = ""
    flag_repeated_issues: str = ""

    flag_overall_issues: str = ""

    # --- Behavior fields ---
    # Redact is used primarily for live demos, and screenshots.
    redact: bool = False


profile_data = ProfileData()
