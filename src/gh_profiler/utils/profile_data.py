"""One place to store all data about the user."""

from dataclasses import dataclass


@dataclass
class ProfileData:
    username: str = ""

    # Profile info
    profile_info: dict | None = None
    account_age: int = 0

    flag_age: str = ""

    # PR fields
    opened_count: int = 0
    merged_count: int = 0
    closed_count: int = 0

    flag_merged_pr: str = ""
    flag_closed_pr: str = ""

    # Issue fields
    new_issue_count: int = 0
    issues_not_planned: int = 0
    total_repeats: int = 0
    repeated_issue_titles: dict | None = None

    flag_issues_not_planned: str = ""
    flag_repeated_issues: str = ""

    flag_overall_issues: str = ""


profile_data = ProfileData()
